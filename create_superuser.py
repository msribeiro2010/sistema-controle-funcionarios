from django.contrib.auth.models import User
from django.core.management import BaseCommand

def create_superuser():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='SuaSenhaSegura123!'
        )
        print('Superuser created successfully!')
    else:
        print('Superuser already exists.')
