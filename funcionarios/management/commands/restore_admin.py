from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Restaura os direitos de administrador para um usuário'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome de usuário do administrador')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Direitos de administrador restaurados para {username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuário {username} não encontrado')) 