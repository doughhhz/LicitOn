from django.urls import path
from .views import criar_licitacao, listar_licitacoes, editar_licitacao, excluir_licitacao

urlpatterns = [
    path('', listar_licitacoes, name='listar_licitacoes'),
    path('nova/', criar_licitacao, name='criar_licitacao'),
    path('editar/<int:id>/', editar_licitacao, name='editar_licitacao'),
    path('excluir/<int:id>/', excluir_licitacao, name='excluir_licitacao'),
]