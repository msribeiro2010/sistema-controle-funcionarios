"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView, LoginView
from funcionarios.views import (
    dashboard, admin_dashboard, registrar_ferias_funcionario,
    registrar_plantao_funcionario, calendario, feriados,
    servidor_dashboard, cancelar_ferias, verificar_conflitos,
    escolha_acao, gerenciar_presenca
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('login/', LoginView.as_view(template_name='funcionarios/login.html'), name='login'),
    path('escolha-acao/', escolha_acao, name='escolha_acao'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('servidor-dashboard/', servidor_dashboard, name='servidor_dashboard'),
    path('ferias/registrar/', registrar_ferias_funcionario, name='registrar_ferias_funcionario'),
    path('ferias/cancelar/<int:ferias_id>/', cancelar_ferias, name='cancelar_ferias'),
    path('plantao/registrar/', registrar_plantao_funcionario, name='registrar_plantao_funcionario'),
    path('calendario/', calendario, name='calendario'),
    path('feriados/', feriados, name='feriados'),
    path('api/verificar-conflitos/', verificar_conflitos, name='verificar_conflitos'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('gerenciar-presenca/', gerenciar_presenca, name='gerenciar_presenca'),
    path('funcionarios/', include('funcionarios.urls')),
]
