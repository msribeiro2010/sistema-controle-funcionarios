#!/usr/bin/env bash
set -o errexit

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --clear

# Executar migrações
python manage.py migrate --noinput 