#!/usr/bin/env bash
set -o errexit

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

# Criar diretório de arquivos estáticos
mkdir -p staticfiles

# Verificar estrutura do projeto
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Python path: $(which python)"
echo "Uvicorn path: $(which uvicorn)"

# Configurar PYTHONPATH
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Testar importação
python -c "import core.wsgi; print('WSGI module found')"
python -c "import core.asgi; print('ASGI module found')"

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrações
python manage.py migrate --noinput

echo "Build completed successfully!" 