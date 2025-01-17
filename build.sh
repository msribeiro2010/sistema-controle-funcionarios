#!/usr/bin/env bash
# exit on error
set -o errexit

# Criar diretórios necessários
echo "Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Instalar dependências
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Configurar variáveis de ambiente para collectstatic
export DJANGO_SETTINGS_MODULE=core.settings
export PYTHONPATH=/opt/render/project/src

# Coletar arquivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Executar migrações
echo "Running migrations..."
python manage.py migrate --no-input

echo "Build completed successfully!" 