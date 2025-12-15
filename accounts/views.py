from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        # 1. Capturar os dados do formulário HTML
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cargo = request.POST.get('cargo') # Vamos salvar isso depois
        senha = request.POST.get('senha')

        # 2. Validações Básicas
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return redirect('register')
        
        # 3. Criar o Usuário no Banco de Dados
        # Estamos usando o email como 'username' para facilitar o login depois
        try:
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome
            user.save()
            
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('register') # Em breve mudaremos para redirect('login')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
            return redirect('register')

    # Se for GET (apenas acessando a página), mostra o HTML
    return render(request, 'accounts/register.html')