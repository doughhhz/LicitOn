from django.urls import path
from .views import criar_licitacao, listar_licitacoes, editar_licitacao, excluir_licitacao, listar_clientes, cadastrar_cliente, relatorios_view
from . import views

urlpatterns = [
    path('', listar_licitacoes, name='listar_licitacoes'),
    path('nova/', criar_licitacao, name='criar_licitacao'),
    path('editar/<int:id>/', editar_licitacao, name='editar_licitacao'),
    path('excluir/<int:id>/', excluir_licitacao, name='excluir_licitacao'),
    path('relatorios/', relatorios_view, name='relatorios'),
    path('importar-json/', views.importar_licitacoes, name='importar_licitacoes'),

    # --- ROTAS DE CLIENTES ---
    path('clientes/', listar_clientes, name='listar_clientes'),
    path('clientes/novo/', cadastrar_cliente, name='cadastrar_cliente'),
]