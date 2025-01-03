from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('registrar-ferias/', views.registrar_ferias, name='registrar_ferias'),
    path('calendario/', views.calendario, name='calendario'),
]
