#!/bin/bash
set -o errexit

# Ativar ambiente virtual
source .venv/bin/activate

# Configurar variáveis de ambiente
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
export PATH=/opt/render/project/src/.venv/bin:$PATH
export DJANGO_SETTINGS_MODULE=core.settings
export PYTHONUNBUFFERED=1

# Verificar conexão com banco de dados
python manage.py check

# Iniciar o servidor
exec uvicorn core.asgi:application --host 0.0.0.0 --port $PORT --log-level debug 