from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Funcionario, Ferias, Plantao

# Register your models here.

class FuncionarioInline(admin.StackedInline):
    model = Funcionario
    can_delete = False
    verbose_name_plural = 'Funcionário'

class CustomUserAdmin(UserAdmin):
    inlines = (FuncionarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

# Desregistrar o UserAdmin padrão
admin.site.unregister(User)
# Registrar o novo UserAdmin com o inline
admin.site.register(User, CustomUserAdmin)

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'cargo', 'dias_ferias_disponiveis')
    search_fields = ('nome', 'matricula')
    list_filter = ('cargo',)

@admin.register(Ferias)
class FeriasAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data_inicio', 'data_fim', 'dias_utilizados', 'status')
    list_filter = ('status', 'data_inicio')
    search_fields = ('funcionario__nome',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('funcionario', 'status')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim', 'dias_utilizados')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Plantao)
class PlantaoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'tipo')
    list_filter = ('tipo', 'data')
    search_fields = ('funcionario__nome',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('funcionario', 'data', 'tipo')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
