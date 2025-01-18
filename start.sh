#!/bin/bash
set -o errexit

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Configurar variáveis de ambiente
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
export PATH=/opt/render/project/src/.venv/bin:$PATH

# Iniciar o servidor
exec waitress-serve --port=$PORT core.wsgi:application 