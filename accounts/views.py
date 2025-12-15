from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout # <--- Novos imports

# View de Cadastro (Mantenha como estava)
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Se já estiver logado, joga pro painel (vamos criar em breve)

    if request.method == "POST":
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cargo = request.POST.get('cargo')
        senha = request.POST.get('senha')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return redirect('register')
        
        try:
            # Criamos o usuário usando o email como username
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome
            user.save()
            messages.success(request, 'Conta criada! Faça login.')
            return redirect('login') # Agora redireciona para o login
            
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
            return redirect('register')

    return render(request, 'accounts/register.html')

# --- NOVA VIEW DE LOGIN ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Se já logou, não precisa ver login

    if request.method == "POST":
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # O Django verifica as credenciais
        # Lembra que salvamos o email no campo 'username'? Por isso username=email
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            login(request, user)
            # messages.success(request, f'Bem-vindo, {user.first_name}!')
            return redirect('dashboard') # Vai para a home do sistema (futura)
        else:
            messages.error(request, 'E-mail ou senha inválidos.')
            return redirect('login')

    return render(request, 'accounts/login.html')

# --- NOVA VIEW DE LOGOUT ---
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')