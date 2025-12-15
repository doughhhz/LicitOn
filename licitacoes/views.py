from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Licitacao
from .forms import LicitacaoForm
from django.db.models import Q

@login_required
def listar_licitacoes(request):
    # Começa pegando TODAS
    licitacoes = Licitacao.objects.all().order_by('-data_abertura')

    # Captura os filtros da URL (se existirem)
    busca_query = request.GET.get('q')
    status_filter = request.GET.get('status')
    modalidade_filter = request.GET.get('modalidade')

    # 1. Filtro de Texto (Busca por Título, Órgão ou Objeto)
    if busca_query:
        licitacoes = licitacoes.filter(
            Q(titulo__icontains=busca_query) | 
            Q(orgao__icontains=busca_query) |
            Q(objeto__icontains=busca_query)
        )

    # 2. Filtro de Status
    if status_filter:
        licitacoes = licitacoes.filter(status=status_filter)

    # 3. Filtro de Modalidade
    if modalidade_filter:
        licitacoes = licitacoes.filter(modalidade=modalidade_filter)

    contexto = {
        'licitacoes': licitacoes,
        # Devolvemos os valores para o HTML "lembrar" o que foi pesquisado
        'busca_atual': busca_query,
        'status_atual': status_filter,
        'modalidade_atual': modalidade_filter
    }
    
    return render(request, 'licitacoes/listar.html', contexto)

@login_required
def criar_licitacao(request):
    if request.method == 'POST':
        form = LicitacaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_licitacoes') # Volta para a lista depois de salvar
    else:
        form = LicitacaoForm()

    return render(request, 'licitacoes/cadastrar.html', {'form': form})

@login_required
def editar_licitacao(request, id):
    # Tenta buscar a licitação pelo ID. Se não achar, dá erro 404.
    licitacao = get_object_or_404(Licitacao, pk=id)

    # Carrega o formulário PREENCHIDO com os dados que já existem (instance=licitacao)
    form = LicitacaoForm(request.POST, request.FILES, instance=licitacao)

    if form.is_valid():
        form.save()
        return redirect('listar_licitacoes')

    return render(request, 'licitacoes/editar.html', {'form': form, 'licitacao': licitacao})

@login_required
def excluir_licitacao(request, id):
    licitacao = get_object_or_404(Licitacao, pk=id)
    licitacao.delete() # Deleta do banco de dados
    return redirect('listar_licitacoes') # Volta para a lista