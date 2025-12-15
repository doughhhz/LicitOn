# licitacoes/management/commands/importar_licitacoes.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from licitacoes.models import Licitacao  # Certifique-se que o model existe
from licitacoes.services import ComprasGovAPI

class Command(BaseCommand):
    help = 'Importa licitações do Compras.gov.br'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=1, help='Quantos dias atrás buscar')

    def handle(self, *args, **options):
        dias = options['dias']
        data_fim = timezone.now().date()
        data_inicio = data_fim - timedelta(days=dias)
        
        str_inicio = data_inicio.strftime('%Y-%m-%d')
        str_fim = data_fim.strftime('%Y-%m-%d')

        api = ComprasGovAPI()
        
        self.stdout.write(f"Buscando licitações de {str_inicio} a {str_fim}...")

        # 1. Busca Legado (8.666)
        licitacoes_legado = api.buscar_licitacoes_legado(str_inicio, str_fim)
        self.stdout.write(f"Encontradas {len(licitacoes_legado)} no módulo Legado.")

        for item in licitacoes_legado:
            # Mapeamento dos campos (Ajuste conforme seu models.py)
            Licitacao.objects.get_or_create(
                numero=item.get('numero_aviso'),
                uasg=item.get('uasg'),
                defaults={
                    'objeto': item.get('objeto'),
                    'modalidade': item.get('nome_modalidade'),
                    'data_abertura': item.get('data_abertura_proposta'),
                    'origem': 'COMPRASNET_LEGADO',
                    'situacao': item.get('situacao_aviso')
                }
            )

        # 2. Busca PNCP (14.133)
        contratacoes_pncp = api.buscar_contratacoes_pncp(str_inicio, str_fim)
        self.stdout.write(f"Encontradas {len(contratacoes_pncp)} no módulo PNCP.")

        for item in contratacoes_pncp:
            Licitacao.objects.get_or_create(
                numero=item.get('numeroCompra'),
                uasg=item.get('unidadeOrgaoCodigoUnidade'), # Ou outro ID único
                defaults={
                    'objeto': item.get('objetoCompra'),
                    'valor_estimado': item.get('valorTotalEstimado'),
                    'data_abertura': item.get('dataAberturaPropostaPncp'),
                    'origem': 'PNCP_14133',
                    'link': item.get('linkSistemaOrigem') # Se disponível
                }
            )

        self.stdout.write(self.style.SUCCESS('Importação concluída!'))