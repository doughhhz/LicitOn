from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    nome = models.CharField("Nome do Órgão / Cliente", max_length=200)
    cnpj = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    email = models.EmailField("Email do Setor", blank=True, null=True)
    endereco = models.CharField("Endereço / Cidade", max_length=300, blank=True, null=True)
    
    # Informações extras
    portal_padrao = models.CharField("Portal Utilizado", max_length=100, blank=True, null=True, help_text="Ex: Comprasnet")
    observacoes = models.TextField("Observações", blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cliente / Órgão"
        verbose_name_plural = "Clientes / Órgãos"
        ordering = ['nome']

class Licitacao(models.Model):
    # Opções para menus (Dropdowns)
    STATUS_CHOICES = [
        ('novo', 'Novo Edital'),
        ('analise', 'Em Análise'),
        ('documentacao', 'Separando Documentos'),
        ('participando', 'Aguardando Disputa'),
        ('ganhamos', 'Ganhamos! 🏆'),
        ('perdemos', 'Perdemos'),
        ('suspenso', 'Suspenso/Cancelado'),
    ]

    MODALIDADE_CHOICES = [
        ('pregao_eletronico', 'Pregão Eletrônico'),
        ('pregao_presencial', 'Pregão Presencial'),
        ('concorrencia', 'Concorrência'),
        ('dispensa', 'Dispensa de Licitação'),
        ('cotacao', 'Cotação Eletrônica'),
    ]

    # Arquivo Principal (Edital)
    arquivo = models.FileField("Edital / Arquivo", upload_to='editais/', blank=True, null=True)

    # Campos Principais
    titulo = models.CharField("Identificador / Nº Edital", max_length=100, help_text="Ex: PE 90/2025")
    # NOVO CAMPO: Conexão com a tabela de Clientes
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Órgão (Cadastro)")
    orgao = models.CharField("Órgão / Cliente", max_length=200, help_text="Ex: Prefeitura de Ponta Grossa")
    objeto = models.TextField("Objeto da Licitação", help_text="O que está sendo comprado?")
    
    # Detalhes Técnicos
    modalidade = models.CharField(max_length=30, choices=MODALIDADE_CHOICES, default='pregao_eletronico')
    portal = models.CharField("Portal", max_length=100, blank=True, null=True, help_text="Ex: Comprasnet, Licitações-e")
    
    # Datas e Valores
    data_abertura = models.DateTimeField("Data da Disputa")
    valor_estimado = models.DecimalField("Valor Estimado (R$)", max_digits=15, decimal_places=2, blank=True, null=True)
    
    # Gestão
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsável Interno")
    
    # Controle do Sistema
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.orgao}"

    class Meta:
        verbose_name = "Licitação"
        verbose_name_plural = "Licitações"
        ordering = ['-data_abertura']


# --- ATENÇÃO: A CLASSE ANEXO COMEÇA AQUI, ENCOSTADA NA MARGEM ESQUERDA ---
class Anexo(models.Model):
    # O conteúdo da classe tem indentação (TAB)
    licitacao = models.ForeignKey(Licitacao, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField("Arquivo Anexo", upload_to='anexos/')
    descricao = models.CharField("Nome do Arquivo", max_length=100, help_text="Ex: Planilha de Custos, Projeto Básico")
    enviado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descricao