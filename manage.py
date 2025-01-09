#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging
from pathlib import Path

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verifica as dependências necessárias."""
    try:
        import django
        logger.info(f"Django version: {django.get_version()}")
        return True
    except ImportError:
        logger.error("Django não está instalado!")
        return False

def setup_environment():
    """Configura o ambiente da aplicação."""
    # Definir variáveis de ambiente padrão
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Verificar se está em ambiente de desenvolvimento
    if os.getenv('DJANGO_ENV') == 'development':
        os.environ.setdefault('DEBUG', 'True')
    
    # Configurar timezone se não estiver definido
    if not os.getenv('TZ'):
        os.environ.setdefault('TZ', 'America/Sao_Paulo')

def create_required_directories():
    """Cria diretórios necessários se não existirem."""
    base_dir = Path(__file__).resolve().parent
    dirs = ['logs', 'media', 'static']
    
    for dir_name in dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            logger.info(f"Created directory: {dir_path}")

def main():
    """Run administrative tasks."""
    try:
        # Verificar dependências
        if not check_dependencies():
            sys.exit(1)
        
        # Configurar ambiente
        setup_environment()
        
        # Criar diretórios necessários
        create_required_directories()
        
        # Importar e executar comandos do Django
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc

        # Criar superusuário se estivermos no Railway
        if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
            try:
                from create_superuser import create_superuser
                create_superuser()
                logger.info("Superuser created successfully")
            except Exception as e:
                logger.error(f"Error creating superuser: {e}")

        execute_from_command_line(sys.argv)
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
