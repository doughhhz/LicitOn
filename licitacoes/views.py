from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Licitacao, Anexo, Cliente
from .forms import LicitacaoForm, AnexosFormSet, ClienteForm, RelatorioForm
from django.db.models import Q, Sum

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
    licitacao = get_object_or_404(Licitacao, pk=id)
    
    if request.method == 'POST':
        form = LicitacaoForm(request.POST, request.FILES, instance=licitacao)
        # O FormSet gerencia os anexos vinculados a esta licitação
        formset = AnexosFormSet(request.POST, request.FILES, instance=licitacao)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('listar_licitacoes')
            
    else:
        form = LicitacaoForm(instance=licitacao)
        formset = AnexosFormSet(instance=licitacao)

    return render(request, 'licitacoes/editar.html', {
        'form': form, 
        'formset': formset, # Enviamos o conjunto de anexos para o HTML
        'licitacao': licitacao
    })

@login_required
def excluir_licitacao(request, id):
    licitacao = get_object_or_404(Licitacao, pk=id)
    licitacao.delete() # Deleta do banco de dados
    return redirect('listar_licitacoes') # Volta para a lista

# --- MÓDULO DE CLIENTES ---

@login_required
def listar_clientes(request):
    clientes = Cliente.objects.all().order_by('nome')
    return render(request, 'clientes/listar.html', {'clientes': clientes})

@login_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/cadastrar.html', {'form': form})

@login_required
def relatorios_view(request):
    form = RelatorioForm(request.GET or None)
    licitacoes = Licitacao.objects.all().order_by('data_abertura')
    
    # Variáveis de Totais
    total_itens = 0
    total_valor = 0
    filtro_ativo = False

    # Só aplica filtros se o usuário clicou em "Gerar Relatório" (tem parâmetros GET)
    if request.GET:
        filtro_ativo = True
        
        if form.is_valid():
            data_inicio = form.cleaned_data.get('data_inicio')
            data_fim = form.cleaned_data.get('data_fim')
            status = form.cleaned_data.get('status')
            cliente = form.cleaned_data.get('cliente')

            if data_inicio:
                licitacoes = licitacoes.filter(data_abertura__date__gte=data_inicio)
            if data_fim:
                licitacoes = licitacoes.filter(data_abertura__date__lte=data_fim)
            if status:
                licitacoes = licitacoes.filter(status=status)
            if cliente:
                licitacoes = licitacoes.filter(cliente=cliente)

    # Calcula os totais DEPOIS de filtrar
    total_itens = licitacoes.count()
    total_valor = licitacoes.aggregate(Sum('valor_estimado'))['valor_estimado__sum'] or 0

    return render(request, 'licitacoes/relatorios.html', {
        'form': form,
        'licitacoes': licitacoes,
        'total_itens': total_itens,
        'total_valor': total_valor,
        'filtro_ativo': filtro_ativo
    })