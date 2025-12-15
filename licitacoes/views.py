import json
from datetime import datetime
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import make_aware
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Licitacao, Anexo, Cliente, ItemLicitacao
from .forms import LicitacaoForm, AnexosFormSet, ClienteForm, RelatorioForm, ImportacaoJsonForm
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

def importar_licitacoes(request):
    if request.method == 'POST':
        form = ImportacaoJsonForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo_json']
            
            try:
                dados = json.load(arquivo)
                contador = 0
                
                # Mapa para converter o texto do JSON nas chaves do seu banco
                MAPA_MODALIDADE = {
                    'Pregão Eletrônico': 'pregao_eletronico',
                    'Pregão Presencial': 'pregao_presencial',
                    'Concorrência': 'concorrencia',
                    'Dispensa de Licitação': 'dispensa',
                    'Cotação Eletrônica': 'cotacao'
                }

                for entry in dados:
                    # --- 1. Tratamento de Datas ---
                    # O JSON vem como "24/11/2025 08:00:00"
                    data_abertura = None
                    if entry.get('data_inicial'):
                        try:
                            dt_naive = datetime.strptime(entry.get('data_inicial'), "%d/%m/%Y %H:%M:%S")
                            data_abertura = make_aware(dt_naive) # Adiciona fuso horário
                        except ValueError:
                            pass

                    # --- 2. Busca ou Cria o Cliente ---
                    nome_cliente = entry.get('entidade', 'Desconhecido').upper()
                    # Salva a UF no endereço se o cliente for novo
                    cliente_obj, created = Cliente.objects.get_or_create(
                        nome=nome_cliente,
                        defaults={'endereco': f"UF: {entry.get('uf', '')}"}
                    )

                    # --- 3. Prepara Modalidade ---
                    modalidade_txt = entry.get('modalidade', '')
                    modalidade_db = MAPA_MODALIDADE.get(modalidade_txt, 'pregao_eletronico')

                    # --- 4. Salva a Licitação ---
                    # Usamos update_or_create para não duplicar se importar o mesmo arquivo 2x
                    licitacao, created = Licitacao.objects.update_or_create(
                        titulo=entry.get('pregao'), # Usa o número do pregão como identificador
                        cliente=cliente_obj,
                        defaults={
                            'orgao': nome_cliente,
                            'uasg': entry.get('uasg'),
                            'url_origem': entry.get('url'),
                            'objeto': entry.get('objeto'),
                            'modalidade': modalidade_db,
                            'portal': entry.get('portal'),
                            'data_abertura': data_abertura,
                            'origem': 'IMPORTACAO_JSON',
                            # Se for novo, status é 'novo', senão mantém o atual
                        }
                    )

                    # --- 5. Salva Itens e Anexos ---
                    if licitacao:
                        # Limpa itens/anexos antigos para garantir sincronia com o JSON
                        licitacao.itens.all().delete()
                        licitacao.anexos.all().delete()

                        # Itens
                        for item in entry.get('itens', []):
                            ItemLicitacao.objects.create(
                                licitacao=licitacao,
                                codigo=item.get('codigo'),
                                grupo=item.get('grupo'),
                                objeto=item.get('objeto'),
                                quantidade=item.get('quantidade'),
                                unidade=item.get('unidade')
                            )

                        # Anexos (Links)
                        for anexo in entry.get('anexos', []):
                            Anexo.objects.create(
                                licitacao=licitacao,
                                descricao=anexo.get('nome'),
                                url=anexo.get('url')
                                # Campo 'arquivo' fica vazio pois é link
                            )
                        
                        contador += 1

                messages.success(request, f"Sucesso! {contador} licitações foram importadas/atualizadas.")
                return redirect('dashboard') # Redireciona para sua página inicial

            except json.JSONDecodeError:
                messages.error(request, "O arquivo enviado não é um JSON válido.")
            except Exception as e:
                messages.error(request, f"Erro ao processar: {str(e)}")
    else:
        form = ImportacaoJsonForm()

    return render(request, 'licitacoes/importar.html', {'form': form})

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