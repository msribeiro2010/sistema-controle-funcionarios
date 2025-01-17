from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from .models import (
    Funcionario, 
    Ferias, 
    Plantao, 
    UsoFolga, 
    Feriado, 
    Documento,
    Presenca,
    Folga
)
from django.utils import timezone
from datetime import date
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html

class FeriadoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'recorrente')
    list_filter = ('tipo', 'recorrente')
    list_editable = ('tipo', 'recorrente')

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

@admin.register(Feriado)
class FeriadoAdmin(admin.ModelAdmin):
    list_display = ['data', 'descricao', 'tipo', 'recorrente']
    list_filter = ['tipo', 'recorrente']
    list_editable = ['tipo', 'recorrente']
    search_fields = ['descricao']
    date_hierarchy = 'data'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        hoje = date.today()
        
        # Filtrar feriados não recorrentes que já passaram
        feriados_nao_recorrentes = Q(recorrente=False) & Q(data__gte=hoje)
        
        # Filtrar feriados recorrentes
        feriados_recorrentes = Q(recorrente=True)
        
        return queryset.filter(feriados_nao_recorrentes | feriados_recorrentes)

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('data', 'descricao', 'tipo', 'recorrente')
        return ('data', 'descricao', 'tipo')

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('data', 'descricao', 'tipo')
        }),
        ('Configurações', {
            'fields': ('recorrente',),
            'description': 'Se marcado como recorrente, o feriado será considerado em todos os anos na mesma data.'
        }),
    )

@admin.register(Ferias)
class FeriasAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data_inicio', 'data_fim', 'data_retorno', 'dias_utilizados', 'status')
    list_filter = ('status', 'data_inicio')
    search_fields = ('funcionario__nome',)
    readonly_fields = ('dias_utilizados', 'data_retorno')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('funcionario', 'status')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim', 'data_retorno', 'dias_utilizados')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(funcionario__usuario=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('funcionario',)
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "funcionario" and not request.user.is_superuser:
            kwargs["queryset"] = Funcionario.objects.filter(usuario=request.user)
            kwargs["initial"] = Funcionario.objects.get(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.funcionario = Funcionario.objects.get(usuario=request.user)
        if obj.data_inicio and obj.data_fim:
            obj.dias_utilizados = (obj.data_fim - obj.data_inicio).days + 1
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

class UsoFolgaInline(admin.TabularInline):
    model = UsoFolga
    extra = 0
    fields = ('data', 'observacoes')

@admin.register(UsoFolga)
class UsoFolgaAdmin(admin.ModelAdmin):
    list_display = ('plantao', 'data', 'get_funcionario')
    list_filter = ('data', 'plantao__funcionario')
    search_fields = ('plantao__funcionario__nome',)
    
    def get_funcionario(self, obj):
        return obj.plantao.funcionario.nome
    get_funcionario.short_description = 'Funcionário'
    get_funcionario.admin_order_field = 'plantao__funcionario__nome'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(plantao__funcionario__usuario=request.user)
        return qs

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.plantao.funcionario.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.plantao.funcionario.usuario == request.user

# Configuração do template admin
class CustomAdminSite(admin.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context['custom_messages'] = messages.get_messages(request)
        return context

admin_site = CustomAdminSite()

# Registre seus modelos no admin personalizado
@admin.register(Plantao)
class PlantaoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'tipo', 'folgas_geradas', 'folgas_utilizadas', 'folgas_restantes')
    list_filter = ('tipo', 'data')
    search_fields = ('funcionario__nome',)
    readonly_fields = ('folgas_geradas', 'folgas_restantes')
    inlines = [UsoFolgaInline]

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
            messages.success(request, 'Plantão salvo com sucesso!')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{error}')
            return False

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('funcionario', 'data', 'tipo')
        }),
        ('Folgas', {
            'fields': ('folgas_geradas', 'folgas_utilizadas', 'folgas_restantes'),
            'description': 'As folgas são geradas automaticamente com base no tipo de plantão.'
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(funcionario__usuario=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('funcionario',)
        return ()

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'funcionario', 'tipo', 'data_upload')
    list_filter = ('tipo', 'data_upload')
    search_fields = ('titulo', 'funcionario__nome')
    date_hierarchy = 'data_upload'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('funcionario', 'titulo', 'tipo', 'arquivo')
        }),
        ('Informações Adicionais', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(funcionario__usuario=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('funcionario',)
        return ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "funcionario" and not request.user.is_superuser:
            kwargs["queryset"] = Funcionario.objects.filter(usuario=request.user)
            kwargs["initial"] = Funcionario.objects.get(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.funcionario_id:
            obj.funcionario = Funcionario.objects.get(usuario=request.user)
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'tipo_trabalho', 'get_actions')
    list_filter = ('tipo_trabalho', 'data')
    search_fields = ('funcionario__nome',)
    
    def get_actions(self, obj):
        if obj:
            return format_html(
                '<a href="{}" class="button">Editar</a> '
                '<a href="{}" class="button" onclick="return confirm(\'Tem certeza que deseja excluir este registro?\')">Excluir</a>',
                reverse('editar_presenca', args=[obj.id]),
                reverse('excluir_presenca', args=[obj.id])
            )
    get_actions.short_description = 'Ações'
    get_actions.allow_tags = True

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
            messages.success(request, 'Registro salvo com sucesso!')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{error}')
            return False

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('funcionario', 'data', 'tipo_trabalho')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(funcionario__usuario=request.user)
        return qs

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.funcionario.usuario == request.user

@admin.register(Folga)
class FolgaAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'tipo_folga', 'get_actions')
    list_filter = ('tipo_folga', 'data')
    search_fields = ('funcionario__nome',)
    
    def get_actions(self, obj):
        if obj:
            return format_html(
                '<a href="{}" class="button">Editar</a> '
                '<a href="{}" class="button" onclick="return confirm(\'Tem certeza que deseja excluir esta folga?\')">Excluir</a>',
                reverse('editar_folga', args=[obj.id]),
                reverse('excluir_folga', args=[obj.id])
            )
    get_actions.short_description = 'Ações'
    get_actions.allow_tags = True

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('funcionario', 'data', 'tipo_folga')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
