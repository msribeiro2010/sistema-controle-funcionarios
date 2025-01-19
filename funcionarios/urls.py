from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import (
    gerenciar_presenca, editar_ferias, editar_plantao, 
    excluir_plantao, editar_presenca, excluir_presenca, 
    gerenciar_folgas, servidor_dashboard, CustomLoginView, registro
)

app_name = 'funcionarios'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='funcionarios:login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('servidor-dashboard/', servidor_dashboard, name='servidor_dashboard'),
    path('calendario/', views.calendario, name='calendario'),
    path('registrar-ferias/', views.registrar_ferias_funcionario, name='registrar_ferias'),
    path('registrar-plantao/', views.registrar_plantao_funcionario, name='registrar_plantao'),
    path('feriados/', views.feriados, name='feriados'),
    path('gerenciar-presenca/', gerenciar_presenca, name='gerenciar_presenca'),
    path('ferias/editar/<int:ferias_id>/', editar_ferias, name='editar_ferias'),
    path('plantao/editar/<int:plantao_id>/', editar_plantao, name='editar_plantao'),
    path('plantao/excluir/<int:plantao_id>/', excluir_plantao, name='excluir_plantao'),
    path('presenca/editar/<int:presenca_id>/', editar_presenca, name='editar_presenca'),
    path('presenca/excluir/<int:presenca_id>/', excluir_presenca, name='excluir_presenca'),
    path('gerenciar-folgas/', gerenciar_folgas, name='gerenciar_folgas'),
    path('presenca/registrar/', views.registrar_presenca, name='registrar_presenca'),
    path('folga/editar/<int:folga_id>/', views.editar_folga, name='editar_folga'),
    path('folga/excluir/<int:folga_id>/', views.excluir_folga, name='excluir_folga'),
    path('ferias/registrar/', views.registrar_ferias_funcionario, name='registrar_ferias'),
    path('ferias/excluir/<int:ferias_id>/', views.excluir_ferias, name='excluir_ferias'),
    path('escolha-acao/', views.escolha_acao, name='escolha_acao'),
    path('registro/', registro, name='registro'),
]
