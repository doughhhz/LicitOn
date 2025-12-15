from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from licitacoes.models import Licitacao
from django.db.models import Sum
from django.utils import timezone

# --- 1. FUNÇÕES DE LOGIN/REGISTRO (QUE ESTAVAM FALTANDO) ---

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- 2. FUNÇÃO DO DASHBOARD (COM OS DADOS PARA O GRÁFICO) ---

@login_required
def dashboard_view(request):
    # Totais Gerais
    total_licitacoes = Licitacao.objects.count()
    
    # Soma (tratando caso seja None)
    total_ganho = Licitacao.objects.filter(status='ganhamos').aggregate(Sum('valor_estimado'))['valor_estimado__sum'] or 0
    
    # Contagens para o Gráfico
    em_andamento = Licitacao.objects.filter(status__in=['novo', 'analise', 'participando']).count()
    ganhas_count = Licitacao.objects.filter(status='ganhamos').count()
    perdidas_count = Licitacao.objects.filter(status='perdemos').count()

    # Agenda (Próximas datas)
    proximas_disputas = Licitacao.objects.filter(
        data_abertura__gte=timezone.now(),
        status__in=['novo', 'participando']
    ).order_by('data_abertura')[:5]

    context = {
        'total_licitacoes': total_licitacoes,
        'total_ganho': total_ganho,
        'em_andamento': em_andamento,
        'ganhas_count': ganhas_count,
        'perdidas_count': perdidas_count,
        'andamento_count': em_andamento,
        'proximas_disputas': proximas_disputas
    }
    
    return render(request, 'dashboard.html', context)