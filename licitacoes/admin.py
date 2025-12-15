from django.contrib import admin
from .models import Licitacao, Anexo, Cliente # <--- Importe Cliente

class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 1

@admin.register(Licitacao)
class LicitacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'data_abertura', 'status') # Troquei orgao por cliente
    search_fields = ('titulo', 'cliente__nome')
    inlines = [AnexoInline]

# REGISTRA A NOVA TABELA
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'telefone', 'endereco')
    search_fields = ('nome', 'cnpj')