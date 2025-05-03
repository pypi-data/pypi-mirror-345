from typing import List, Dict

from collections import defaultdict

import os

import copy

import hashlib

#import base64

import datetime

from zoneinfo import ZoneInfo

import requests

import colorama

import tzdata

from nsj_gcf_utils.json_util import convert_to_dumps, json_loads, json_dumps, JsonLoadException

from nsj_rest_lib.dto.dto_base import DTOBase
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_client.service.integrador_cfg import (
    entidades_integracao, _entidades_particionadas_por_empresa,
    _entidades_particionadas_por_estabelecimento, _entidades_particionadas_por_grupo,
    medir_tempo, Environment, TAMANHO_PAGINA, _E_SEND_DATA, _E_CHECK_INT,
    AUTH_HEADER
)

from nsj_integracao_api_client.infra.api_client import ApiClient

from nsj_integracao_api_client.infra.token_service import TokenService

from nsj_integracao_api_client.infra.injector_factory import InjectorFactory

from nsj_integracao_api_client.infra.debug_utils import DebugUtils as _du

colorama.init(autoreset=True)

class IntegradorService():

    _injector : InjectorFactory = None

    _dao_intg: 'IntegracaoDAO' = None

    _tz_br: ZoneInfo = None

    _token_service: TokenService = None

    _api_client: ApiClient = None

    _api_key: str = None

    _tenant: int = None

    # Caso se deseje usar um tenant diferente do especificado no token
    _forced_tenant: int = None

    _filtros_particionamento: list = None

    _save_point: dict = {
        "servicos.tiposprojetos": None
    }

    _ignored_fields : list = ["tenant", "lastupdate"]

    _detalhar_diferencas: bool

    _trace: bool

    _interromper_execucao: bool

    def __init__(self, injector: InjectorFactory, log, env : Environment = Environment.PROD, forced_tenant : int = None):
        self._injector = injector
        self._logger = log
        self._forced_tenant = forced_tenant
        self._tz_br = ZoneInfo("America/Sao_Paulo")
        self._detalhar_diferencas = False
        self._trace = False
        self._api_client = ApiClient(env)
        self._token_service = TokenService()
        self._interromper_execucao = False
        #self._carregar_savepoint()

    def _log(self, msg):
        self._logger.mensagem(msg)


    def _carregar_savepoint(self):
        try:
            with open('savepoint.json', 'r') as f:
                self._save_point = json_loads(f.read())
                entidade_salva = list(self._save_point.keys())[0]
                self._log(f"Savepoint carregado para : {entidade_salva }")
        except FileNotFoundError:
            self._save_point = {}


    def _trace_check(self, filename, content):

        _du.conditional_trace(
            condition=_E_CHECK_INT or self._trace,
            func=_du.save_to_file,
            filename=filename,
            content=content
        )

    def _detail_check(self, filename, content):

        _du.conditional_trace(
            condition=_E_CHECK_INT or self._detalhar_diferencas,
            func=_du.save_to_file,
            filename=filename,
            content=content
        )

    def _fields_to_load(self, dto_class) -> dict:

        fields = {}
        fields.setdefault("root", set(dto_class.fields_map.keys()))

        for _related_entity, _related_list_fields in dto_class.list_fields_map.items():
            fields["root"].add(_related_entity)
            fields.setdefault(_related_entity, set())
            _related_fields = _related_list_fields.dto_type.fields_map.keys()
            for _related_field in _related_fields:
                fields["root"].add(f"{_related_entity}.{_related_field}")
                fields[_related_entity].add(_related_field)

        return fields


    def _integracao_dao(self):
        if self._dao_intg is None:
            self._dao_intg = self._injector.integracao_dao()
        return self._dao_intg


    @property
    def api_key(self):

        if self._api_key is None:
            self._api_key = self._integracao_dao().recuperar_token()

        return self._api_key


    @property
    def tenant(self):

        if self._forced_tenant is not None:
            return self._forced_tenant

        if self._tenant is None:
            decoded_token = self._token_service.decode_token(self.api_key)
            self._tenant = decoded_token["tenant_id"]

        return self._tenant


    def _integracao_foi_configurada(self):
        return self._integracao_dao().integracao_configurada()


    def _validar_grupos_empresariais(self, grupos) -> List[Dict[str, str]]:

        grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais(grupos)
        _cods = [grupo['codigo'] for grupo in grupos_cadastrados]
        _grupos_faltantes = [grupo for grupo in grupos if grupo not in _cods]
        assert len(_grupos_faltantes)==0, f"Grupo(s) '{','.join(_grupos_faltantes)}' não encontrado(s)."
        return grupos_cadastrados


    def executar_instalacao(self, chave_ativacao: str, grupos: List[str]):

        assert chave_ativacao, "Chave de ativação não pode ser vazia."
        self._log(f"Executando instalação com a chave de ativação: {chave_ativacao}")

        assert not self._integracao_foi_configurada(), "Integração já instalada anteriormente."
        _token: str = self._api_client.gerar_token_tenant(chave_ativacao)
        decoded_token = self._token_service.decode_token(_token)

        if grupos:
            grupos_cadastrados = self._validar_grupos_empresariais(grupos)
        else:
            grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais()

        _ids  = [str(grupo['grupoempresarial']) for grupo in grupos_cadastrados]

        self._integracao_dao().registrar_grupos_empresariais(_ids)

        self._integracao_dao().registra_token_tenant(_token)

        self._log(f"Instalação efetuada com sucesso para o tenant '{decoded_token['tenant_id']}'.")


    def ativar_grupos_empresariais(self, grupos: List[str]):

        assert self._integracao_foi_configurada(), "Integração não configurada!"
        assert grupos, "Grupos não podem ser vazios!"

        if grupos:
            grupos_cadastrados = self._validar_grupos_empresariais(grupos)
        else:
            grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais()

        _ids  = [grupo['grupoempresarial'] for grupo in grupos_cadastrados]

        self._integracao_dao().registrar_grupos_empresariais(_ids)

        self._log(f"Grupos empresariais ativados: '{','.join(grupos)}'.")


    def desativar_grupos_empresariais(self, grupos: List[str]):

        assert self._integracao_foi_configurada(), "Integração não configurada!"
        assert grupos, "Grupos não podem ser vazios!"

        grupos_cadastrados = self._validar_grupos_empresariais(grupos)

        _ids  = [grupo['grupoempresarial'] for grupo in grupos_cadastrados]

        self._integracao_dao().desativar_grupos_empresariais(_ids)

        self._log(f"Grupos empresariais desativados: '{','.join(grupos)}'.")


    def _filtro_particionamento_de(self, entidade: str):

        if self._filtros_particionamento is None:
            _dados_part = self._integracao_dao().listar_dados_particionamento()

            self._filtros_particionamento = [
                {'grupoempresarial' : ",".join(list(map(lambda i: str(i["grupoempresarial"]), _dados_part)))},
                {'empresa' : ",".join(list(map(lambda i: str(i["empresa"]), _dados_part)))},
                {'estabelecimento' : ",".join(list(map(lambda i: str(i["estabelecimento"]), _dados_part)))}
            ]

        if entidade in _entidades_particionadas_por_grupo:
            return  self._filtros_particionamento[0]

        if entidade in _entidades_particionadas_por_empresa:
            return self._filtros_particionamento[1]

        if entidade in _entidades_particionadas_por_estabelecimento:
            return self._filtros_particionamento[2]


    def _dto_to_api(
        self,
        campos: Dict[str, List[str]],
        data: List[DTOBase]
    ) -> List[dict]:
        # Converte os objetos DTO para dicionários e adiciona o tenant
        transformed_data = []
        for dto in data:
            dto.tenant = self.tenant
            dto_dict = dto.convert_to_dict(campos)

            # Implementado devido a dualidade de conversão de campos json na API que podem ser convertidos com str/dict

            if "created_by" in dto_dict and not dto_dict["created_by"] is None:
                if not isinstance(dto_dict["created_by"], dict):
                    try:
                        _value_dict = json_loads(dto_dict["created_by"])
                        dto_dict["created_by"] = _value_dict
                    except (TypeError, ValueError, JsonLoadException):
                        dto_dict["created_by"] = {"id": dto_dict["created_by"]}

            if "updated_by" in dto_dict and not dto_dict["updated_by"] is None:
                if not isinstance(dto_dict["updated_by"], dict):
                    try:
                        _value_dict = json_loads(dto_dict["updated_by"])
                        dto_dict["updated_by"] = _value_dict
                    except (TypeError, ValueError, JsonLoadException):
                        dto_dict["updated_by"] = {"id": dto_dict["updated_by"]}


            transformed_data.append(dto_dict)

        return transformed_data


    def _save_point_for(self, tabela: str):
        return self._save_point.get(tabela, None)


    def _do_save_point(self, tabela: str, chave):
        self._save_point[tabela] = chave
        with open('savepoint.json', 'w') as f:
            f.write(f'{{ "{tabela}": "{chave}" }} ' if chave else f'{{ "{tabela}": null }} ')


    def _save_point_clear(self):
        self._save_point.clear()
        if os.path.exists('savepoint.json'):
            os.remove('savepoint.json')


    def interromper_execucao(self):
        self._interromper_execucao = True


    @medir_tempo("Carga inicial")
    def executar_carga_inicial(self, entidades: list):
        self._interromper_execucao = False

        assert self._integracao_foi_configurada(), "Integração não configurada!"

        _dao = self._integracao_dao()

        self._log(f"Tenant: {self.tenant} .")
        self._log(f"{len(entidades_integracao)} entidades para processar.")

        entidades_carga_inicial = copy.copy(entidades_integracao)

        # Remover entidades que nao devem ser processadas
        if entidades:
            for entidade in entidades:
                assert entidade in entidades_integracao, f"Entidade '{entidade}' não consta como entidade para integração!"

            for entidade in entidades_integracao:
                if not entidade in entidades:
                    entidades_carga_inicial.remove(entidade)

        # Remover entidades que ja foram processadas
        if self._save_point:
            for entidade in entidades_integracao:
                if not entidade in self._save_point:
                    entidades_carga_inicial.remove(entidade)
                else:
                    break

        for entidade in entidades_carga_inicial:

            # if not entidade in ['persona.adiantamentosavulsos','persona.trabalhadores']:
            #     continue

            if self._interromper_execucao:
                self._log("Processo interrompido pelo usuário.")
                return

            _idx = entidades_integracao.index(entidade) + 1
            self._log(f"Efetuando carga {entidade}, {_idx} de {len(entidades_integracao)}.")
            _count = 0

            # Carregar dados paginados para integrar
            service = self._injector.service_for(entidade, True)
            fields = self._fields_to_load(service._dto_class)
            filters = self._filtro_particionamento_de(entidade)
            search_query = None

            pagina = 0
            self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo dados para carga.")
            while True:

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                current_after = self._save_point_for(entidade)
                _data = service.list(
                        current_after,
                        TAMANHO_PAGINA,
                        fields,
                        None,
                        filters,
                        search_query=search_query,
                    )

                _count = _count + len(_data)

                if len(_data)==0:
                    if current_after is None:
                        self._log("Sem dados para transferir, indo adiante...")
                    else:
                        self._log("Entidade integrada com sucesso.")
                    break

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")

                dict_data = self._dto_to_api(fields, _data)

                self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Enviando dados para a api.")
                self._api_client.enviar_dados(dict_data, entidade, self.api_key)

                # Aponta a leitura para a próxima página
                _last = _data[-1]
                self._do_save_point(entidade, getattr(_last, _last.pk_field))

            _dao.atualiza_ultima_integracao(entidade)
            self._save_point_clear()

        self._log("\033[92mCarga inicial finalizada com sucesso!\033[0m")


    @medir_tempo("Integração")
    def executar_integracao(self):
        self._interromper_execucao = False

        assert self._integracao_foi_configurada(), "Integração não configurada!"

        self._log(f"Tenant: {self.tenant} .")

        _dao = self._integracao_dao()

        entidades_pendentes = _dao.listar_entidades_pendentes_integracao()

        entidades_pendentes = {entidade: entidades_pendentes[entidade] for entidade in entidades_integracao if entidade in entidades_pendentes.keys()}

        self._log(f"{len(entidades_pendentes)} entidades para processar." if entidades_pendentes else "Nenhuma entidade para processar.")
        _resumo = {}

        for entidade, data_ultima_integracao in entidades_pendentes.items():

            if self._interromper_execucao:
                self._log("Processo interrompido pelo usuário.")
                return

            _idx = list(entidades_pendentes.keys()).index(entidade) + 1
            self._log(f"Integrando {entidade}, {_idx} de {len(entidades_pendentes)}.")
            _count = 0

            # Carregar dados paginados para integrar
            service = self._injector.service_for(entidade, True)
            current_after = None
            fields = self._fields_to_load(service._dto_class) #tornar publico
            filters = self._filtro_particionamento_de(entidade)
            search_query = None
            _acao = entidade.split('.')[1]

            # Dados criados apos data_ultima_integracao
            # filtro_criacao = filters.copy() if filters else {}
            # filtro_criacao['created_at'] = data_ultima_integracao
            # while True:

            #     data = service.list(
            #             current_after,
            #             TAMANHO_PAGINA,
            #             fields,
            #             None,
            #             filtro_criacao,
            #             search_query=search_query,
            #         )

            #     if len(data)==0:
            #         self._log("Sem dados para criar, indo adiante...")
            #         break

            #     # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
            #     dict_data = self._dto_to_api(fields, data)

            #     # Mandar a bagatela por apis
            #     self._enviar_dados(dict_data, _acao)

            #     # Aponta a leitura para a próxima página
            #     _last = data[-1]
            #     current_after = getattr(_last, _last.pk_field)

            # Dados alterados apos data_ultima_integracao
            filtro_atualizacao = filters.copy() if filters else {}
            filtro_atualizacao['lastupdate'] = data_ultima_integracao
            while True:

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _data = service.list(
                        current_after,
                        TAMANHO_PAGINA,
                        fields,
                        None,
                        filtro_atualizacao,
                        search_query=search_query,
                    )

                _count = _count + len(_data)

                if len(_data)==0:
                    if current_after is None:
                        self._log("Sem dados para atualizar, indo adiante...")
                    else:
                        self._log("Entidade integrada com sucesso.")
                    break

                self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")
                _resumo[entidade] = _count

                # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                dict_data = self._dto_to_api(fields, _data)

                # Mandar a bagatela por apis
                self._api_client.enviar_dados(dict_data, entidade, self.api_key)

                # Aponta a leitura para a próxima página
                _last = _data[-1]
                current_after = getattr(_last, _last.pk_field)

            # Dados excluidos apos data_ultima_integracao
            _coluna_id = service._dto_class.fields_map[service._dto_class.pk_field].entity_field
            para_apagar = _dao.listar_dados_exclusao(_coluna_id, entidade, data_ultima_integracao)
            if para_apagar:
                _resumo[entidade] = _resumo.get(entidade, 0) + len(para_apagar)
                self._api_client.apagar_dados(para_apagar, entidade, self.api_key, self.tenant)

            _dao.atualiza_ultima_integracao(entidade)

        self._log("\033[92mIntegração finalizada com sucesso!\033[0m")
        if _resumo:
            self._log(f"\033[92mResumo da integração:\033[0m {', '.join(f'{k}: {v}' for k, v in _resumo.items())}")


    def integrity_fields(self, dto) -> dict:
        fields = {"root": set()}

        for _field_name in sorted(dto.integrity_check_fields_map.keys()):

            if _field_name in self._ignored_fields:
                continue

            _field_obj = dto.integrity_check_fields_map[_field_name]

            if isinstance(_field_obj, DTOField):
                fields["root"].add(_field_name)
                continue

            if isinstance(_field_obj, DTOListField):
                fields["root"].add(_field_name)
                fields.setdefault(_field_name, set())

                for _related_field in sorted(_field_obj.dto_type.integrity_check_fields_map.keys()):
                    if not _related_field in self._ignored_fields:
                        fields["root"].add(f"{_field_name}.{_related_field}")
                        fields[_field_name].add(_related_field)

        return fields

    def tratar_campos_comparacao(self, dados: dict, campos_ignorados: list):

        keys_to_delete = []
        for chave, valor in dados.items():

            # Remove timezone para comparação
            if isinstance(valor, (datetime.datetime, datetime.date)):
                if valor.tzinfo is not None:
                    dados[chave] = valor.astimezone(self._tz_br).replace(microsecond=0, tzinfo=None)
                else:
                    dados[chave] = valor.replace(microsecond=0, tzinfo=None)

            # Ignora campos não úteis
            if chave in campos_ignorados:
                keys_to_delete.append(chave)

            # Aplica regras em sublistas
            if isinstance(valor, list):
                valor.sort(key=lambda x: x['id'])
                for item in valor:
                    self.tratar_campos_comparacao(item, campos_ignorados)

        for chave in keys_to_delete:
            del dados[chave]


    def converte_dados_para_hash(self, dto, integrity_fields):

        data = dto.convert_to_dict(integrity_fields)

        self.tratar_campos_comparacao(data, self._ignored_fields)

        # concatenated_valors = ''.join(
        #     str(data[chave]) for chave in sorted(data.keys())
        # )
        #concatenated_values = ','.join( "'"+str(data[key])+"'" if (isinstance(data[key], str) or isinstance(data[key], uuid.UUID)) else str(data[key]) for key in sorted(data.keys()))
        concatenated_values = json_dumps(data)

        data['tenant'] = self.tenant

        return {
            'id': str(data[dto.pk_field]),
            'hash': hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest(),
            '_source': data,
            '_source_hash': concatenated_values
        }


    def comparar_dados(self, dados_referencia, dados_comparacao):

        if dados_referencia['campos']['_'] != dados_comparacao['campos']['_']:
            self._log(f"\033[91mExistem diferenças entre os campos comparados:\r\n\r\nLocal: {dados_referencia['campos']['_']}\r\n\r\nWeb  : {dados_comparacao['campos']['_']}\033[0m")

        if dados_referencia['registros'] != dados_comparacao['registros']:
            self._log(f"\033[91mExistem diferenças nas quantidades de dados:\r\n\r\nLocal: {dados_referencia['registros']}\r\n\r\nWeb  : {dados_comparacao['registros']}\033[0m")

        # Índices para facilitar busca por ID
        idx_referencia = {item['id']: item for item in dados_referencia['dados']}
        idx_comparacao = {item['id']: item for item in dados_comparacao['dados']}

        # Inicializar listas de mudanças
        _criar = []
        _atualizar = []
        _excluir = []
        _diff:List[tuple] = []

        # Verificar itens nos dados de referência
        for item_id, item_ref in idx_referencia.items():
            if item_id not in idx_comparacao:
                # Criar se não existe nos dados de comparação
                _criar.append(item_ref['_source'])
            elif item_ref['hash'] != idx_comparacao[item_id]['hash']:
                # Atualizar se o hash é diferente
                _atualizar.append(item_ref['_source'])
                # Adiciona para exibir os dados puros se disponível
                if '_source' in idx_comparacao[item_id]:
                    a = json_loads(item_ref['_source_hash'])  #tr.construir_objeto(dados_referencia['campos']['_'], item_ref['_source_hash'])
                    b = json_loads(idx_comparacao[item_id]['_source']) #tr.construir_objeto(dados_comparacao['campos']['_'], idx_comparacao[item_id]['_source'])
                    _diff.append((a,b))

        # Verificar itens nos dados de comparação
        for item_id in idx_comparacao.keys():
            if item_id not in idx_referencia:
                # Excluir se não existe em A
                _excluir.append(idx_comparacao[item_id]['id'])

        return _criar, _atualizar, _excluir, _diff

    def _log_integridade(self, msg):
        self._detail_check(f'{self._integridade_dir}/log_diferencas_integridade.log', msg)

    def _color(self, text, code, console):
        if console:
            return f"\033[{code}m{text}\033[0m"
        else:
            return text

    def _log_comparacao_objetos(self, id, obj1, obj2, caminho='', console=False):
        _out = self._log if console else self._log_integridade

        if isinstance(obj1, dict) and isinstance(obj2, dict):
            for k in set(obj1.keys()).union(obj2.keys()):
                self._log_comparacao_objetos(id, obj1.get(k), obj2.get(k), f"{caminho}.{k}" if caminho else k)
        elif isinstance(obj1, list) and isinstance(obj2, list):
            max_len = max(len(obj1), len(obj2))
            for i in range(max_len):
                item1 = obj1[i] if i < len(obj1) else None
                item2 = obj2[i] if i < len(obj2) else None
                _id = obj1[i]['id'] if len(obj1) > 0 else obj2[i]['id'] if len(obj2) > 0 else 'indefinido'
                self._log_comparacao_objetos(id, item1, item2, f"{caminho}[{_id}]")
        else:
            s1 = str(obj1)
            s2 = str(obj2)
            if s1 != s2:
                s1_pad = s1.ljust(25)
                s2_pad = s2.ljust(25)
                _id = str(id)

                _out(f"{_id:<40} {caminho:<40} {self._color(s1_pad, '31', console)} {self._color(s2_pad, '32', console)}")

    def _log_diferencas(self, entidade, data_ultima_integracao, console=False):
        _out = self._log if console else self._log_integridade
        _out("/r/n")
        _out("-" * 130)
        _out(f"Entidade: {self._color(entidade, '36', console)}")
        _out(f"Data da última integração: {self._color(data_ultima_integracao, '36', console)}")
        _out(f"{'ID':<40} {'Campo':<40} {'Local':<25} {'Nuvem':<25}")
        _out("-" * 130)

    @medir_tempo("Verificação de integridade")
    def executar_verificacao_integridade(
        self,
        entidades: list,
        parar_caso_diferencas : bool = False,
        detalhar_diferencas: bool = False,
        corrigir_auto: bool = False,
        tenant: int = 0,
        trace: bool = False
    ):
        self._interromper_execucao = False

        assert self._integracao_foi_configurada(), "Integração não configurada!"

        self._log(f"Tenant: {self.tenant} .")

        self._detalhar_diferencas = detalhar_diferencas

        self._trace = trace

        if corrigir_auto:
            assert self.tenant==tenant, "Tenant informado para correção não é igual ao configurado"

        self._integridade_dir = f"verificacao_integridade_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Remover entidades que nao devem ser processadas
        entidades_verificacao = copy.copy(entidades_integracao)
        if entidades:
            for entidade in entidades:
                assert entidade in entidades_integracao, f"Entidade '{entidade}' não consta como entidade para integração!"

            for entidade in entidades_integracao:
                if not entidade in entidades:
                    entidades_verificacao.remove(entidade)


        self._log(f"{len(entidades_verificacao)} entidades para verificar integridade.")

        _diferencas = False
        _idx = 0
        _resumo = defaultdict(list)
        for entidade in reversed(entidades_verificacao):

            # if not entidade in ['persona.adiantamentosavulsos','persona.trabalhadores']:
            #     continue

            if self._interromper_execucao:
                self._log("Processo interrompido pelo usuário.")
                return

            _idx += 1
            self._log(f"Verificando integridade {entidade}, {_idx} de {len(entidades_verificacao)}.")

            # Carregar dados paginados para integrar
            service = self._injector.service_for(entidade, False)

            _count = 0
            current_after = None
            fields = self._fields_to_load(service._dto_class)
            filters = self._filtro_particionamento_de(entidade)
            search_query = None
            _integrity_fields = self.integrity_fields(service._dto_class)
            _dados_locais = []

            self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo dados para comparação.")
            while True:

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _data = service.list(
                    current_after,
                    TAMANHO_PAGINA,
                    fields,
                    None,
                    filters,
                    search_query=search_query,
                )

                _count = _count + len(_data)

                if len(_data)==0:
                    break

                self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")

                # Aponta a leitura para a próxima página
                _last = _data[-1]
                current_after = getattr(_last, _last.pk_field)

                # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                _cp_fields = copy.deepcopy(_integrity_fields)
                while _data:
                    dto = _data.pop(0)
                    _dados_locais.append(self.converte_dados_para_hash(dto, _cp_fields))

                #break


            _dados_locais = {
                'registros' : _count,
                'campos': {
                    "_": ",".join(sorted(_integrity_fields['root'])),
                },
                'dados': _dados_locais
            }

            self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consultando dados da api.")


            # captura os dados de integridade da entidade
            #_acao = entidade.split('.')[1]
            _dados = []
            _ultimo_id = None
            _count = 0
            while True:

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _dados_remotos = self._api_client.consultar_integridade_de(entidade, filters, _ultimo_id, detalhar_diferencas, self.api_key, self.tenant)

                _count = _count + len(_dados_remotos['dados'])

                if len(_dados_remotos['dados']) == 0:
                    break

                self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")

                _dados = _dados + copy.copy(_dados_remotos['dados'])
                _ultimo_id = _dados[-1]['id']

                #break

            _dados_remotos['dados'] = _dados
            _dados_remotos['registros'] = _count

            self._log(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Comparando dados.")

            if self._interromper_execucao:
                self._log("Processo interrompido pelo usuário.")
                return

            # Compara os dados e obtem o que se deve fazer
            para_criar, para_atualizar, para_apagar, _diff = self.comparar_dados(_dados_locais, _dados_remotos)

            if para_criar or para_atualizar or para_apagar:
                _resumo[entidade].append(f"\033[93mLocal: {_dados_locais['registros']}  Web: {_dados_remotos['registros']}\033[0m")

            if para_criar:
                _resumo[entidade].append(f"\033[93mPara criar -> {len(para_criar)}\033[0m")
                self._log(f"\r\n\033[93m{_resumo[entidade][-1]}\033[0m\r\n")
                if corrigir_auto:
                    self._log(f"\r\nCriando dados em {entidade}.\r\n")
                    self._api_client.enviar_dados(para_criar, entidade, self.api_key)

            if self._interromper_execucao:
                self._log("Processo interrompido pelo usuário.")
                return

            if para_atualizar:
                _resumo[entidade].append(f"\033[93mPara atualizar -> {len(para_atualizar)}\033[0m")
                self._log(f"\r\n\033[93m{_resumo[entidade][-1]}\033[0m\r\n")
                if _diff:
                    _dt_ultima_integracao = self._dao_intg.data_ultima_integracao(entidade)
                    self._log_diferencas(entidade, _dt_ultima_integracao)
                    _i : int = 0
                    for _desktop, _web in _diff:
                        _i  += 1
                        self._log_comparacao_objetos(_desktop['id'], _desktop, _web)
                        self._trace_check(f"{self._integridade_dir}/integridade_{entidade.replace('.','_')}_{_desktop['id']}_{_i}_LOCAL.txt", json_dumps(_desktop))
                        self._trace_check(f"{self._integridade_dir}/integridade_{entidade.replace('.','_')}_{_web['id']}_{_i}_REMOTE.txt", json_dumps(_web))
                if corrigir_auto:
                    print(f"\r\nAtualizando dados em {entidade}.\r\n")
                    self._api_client.enviar_dados(para_atualizar, entidade, self.api_key)

            if self._interromper_execucao:
                self._log("Processo interrompido pelo usuário.")
                return

            if para_apagar:
                #self._print(f"\r\n\033[93mPara apagar -> {len(para_apagar)}\033[0m\r\n")
                _resumo[entidade].append(f"\033[93mPara apagar -> {len(para_apagar)}\033[0m")
                self._log(f"\r\n\033[93m{_resumo[entidade][-1]}\033[0m\r\n")
                if corrigir_auto:
                    self._log(f"\r\nRemovendo dados em {entidade}.\r\n")
                    self._api_client.apagar_dados(para_apagar, entidade, self.api_key, self.tenant)

            if not _diferencas:
                _diferencas = para_criar or para_atualizar or para_apagar

            if parar_caso_diferencas and (para_criar or para_atualizar or para_apagar) and not corrigir_auto:
                break

        if _diferencas:
            self._log("\033[93mOcorreram diferenças na checagem da integridade, verifique a saída.\033[0m\r\n")

        if not _diferencas:
            self._log("\033[92mVerificação finalizada sem diferenças!\033[0m\r\n")

        if _resumo:
            self._log("\033[92mResumo da integração:\033[0m\r\n")
            for entidade, detalhes in _resumo.items():
                self._log(f"{entidade}:  " + '\n'.join(detalhes) + "\n")

            if corrigir_auto:
                self._log("\033[92mForam enviados dados de correção durante o processo, verifique a saída.\033[0m\r\n")
