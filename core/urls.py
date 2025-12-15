from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse # Importe isso

# Função provisória só para teste
def dashboard_temp(request):
    return HttpResponse(f"<h1>Bem-vindo ao Dashboard do LicitOn!</h1><p>Logado como: {request.user}</p><a href='/auth/logout/'>Sair</a>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('dashboard/', dashboard_temp, name='dashboard'), # Rota temporária
]