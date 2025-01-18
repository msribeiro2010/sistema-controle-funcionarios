"""
WSGI config for core project.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Adicionar o diretório do projeto ao PYTHONPATH
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
