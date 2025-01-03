from django.apps import AppConfig


class FuncionariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funcionarios'
    verbose_name = 'Controle de Funcionários'

    def ready(self):
        # Registra os template tags
        from django.template import base
        base.add_to_builtins('django.templatetags.i18n')
        base.autodiscover_modules('templatetags')
