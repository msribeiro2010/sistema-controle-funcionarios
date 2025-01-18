#!/bin/bash
set -o errexit

# Configurar variáveis de ambiente
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
export PATH=/opt/render/project/src/.venv/bin:$PATH

# Iniciar o servidor
exec /opt/render/project/src/.venv/bin/daphne \
    -b 0.0.0.0 \
    -p $PORT \
    core.asgi:application 