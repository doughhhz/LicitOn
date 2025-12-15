from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Licitacao
from .forms import LicitacaoForm

@login_required
def listar_licitacoes(request):
    # Busca todas as licitações ordenadas pela data (da mais nova pra mais velha)
    licitacoes = Licitacao.objects.all().order_by('-data_abertura')
    
    contexto = {
        'licitacoes': licitacoes
    }
    return render(request, 'licitacoes/listar.html', contexto)

@login_required
def criar_licitacao(request):
    if request.method == 'POST':
        form = LicitacaoForm(request.POST)
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
    form = LicitacaoForm(request.POST or None, instance=licitacao)

    if form.is_valid():
        form.save()
        return redirect('listar_licitacoes')

    return render(request, 'licitacoes/editar.html', {'form': form, 'licitacao': licitacao})

@login_required
def excluir_licitacao(request, id):
    licitacao = get_object_or_404(Licitacao, pk=id)
    licitacao.delete() # Deleta do banco de dados
    return redirect('listar_licitacoes') # Volta para a lista