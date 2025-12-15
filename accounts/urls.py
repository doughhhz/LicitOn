from django.urls import path
from .views import register_view

urlpatterns = [
    path('registo/', register_view, name='register'),
]