from django.contrib import admin
from .models import Licitacao

@admin.register(Licitacao)
class LicitacaoAdmin(admin.ModelAdmin):
    # Colunas que vão aparecer na lista
    list_display = ('titulo', 'orgao', 'data_abertura', 'valor_estimado', 'status', 'responsavel')
    
    # Filtros laterais (muito útil!)
    list_filter = ('status', 'modalidade', 'responsavel')
    
    # Barra de pesquisa
    search_fields = ('titulo', 'orgao', 'objeto')
    
    # Navegação por data
    date_hierarchy = 'data_abertura'