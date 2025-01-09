from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Funcionario, Ferias, Plantao, UsoFolga, Feriado, Documento

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
    list_display = ('data', 'descricao', 'tipo', 'recorrente')
    list_filter = ('tipo', 'recorrente', 'data')
    search_fields = ('descricao',)
    date_hierarchy = 'data'
    list_editable = ('tipo', 'recorrente')
    ordering = ('data',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('data', 'descricao', 'tipo')
        }),
        ('Configurações', {
            'fields': ('recorrente',),
            'description': 'Se marcado como recorrente, o feriado será considerado em todos os anos na mesma data.'
        }),
    )

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('data', 'descricao', 'tipo', 'recorrente')
        return ('data', 'descricao', 'tipo')

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

@admin.register(Plantao)
class PlantaoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'tipo', 'folgas_geradas', 'folgas_utilizadas', 'folgas_restantes')
    list_filter = ('tipo', 'data')
    search_fields = ('funcionario__nome',)
    readonly_fields = ('folgas_geradas', 'folgas_restantes')
    inlines = [UsoFolgaInline]
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(funcionario__usuario=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('funcionario',)
        return ()

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
