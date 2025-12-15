# licitacoes/services.py
import requests
from datetime import datetime, timedelta

class ComprasGovAPI:
    BASE_URL = "https://dadosabertos.compras.gov.br"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'LicitOn-Bot/1.0'
        })

    def buscar_licitacoes_legado(self, data_inicio, data_fim, uasg=None):
        """
        Busca licitações do Módulo Legado (Lei 8.666/93).
        Datas no formato YYYY-MM-DD.
        """
        endpoint = f"{self.BASE_URL}/modulo-legado/1_consultarLicitacao"
        params = {
            'data_publicacao_inicial': data_inicio,
            'data_publicacao_final': data_fim,
            'tamanhoPagina': 50  # Ajuste conforme necessidade
        }
        if uasg:
            params['uasg'] = uasg

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json().get('resultado', [])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar legado: {e}")
            return []

    def buscar_contratacoes_pncp(self, data_inicio, data_fim):
        """
        Busca contratações do PNCP (Lei 14.133/2021).
        Formato de data esperado pela API: YYYYMMDD (Confirmar no teste, o manual sugere YYYY-MM-DD em alguns lugares e texto em outros).
        Vamos tentar o padrão YYYY-MM-DD primeiro.
        """
        endpoint = f"{self.BASE_URL}/modulo-contratacoes/1_consultarContratacoes_PNCP_14133"
        params = {
            'dataPublicacaoPncpInicial': data_inicio.replace("-", ""), # A API PNCP costuma usar YYYYMMDD
            'dataPublicacaoPncpFinal': data_fim.replace("-", ""),
            'tamanhoPagina': 50
        }

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json().get('resultado', [])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar PNCP: {e}")
            return []