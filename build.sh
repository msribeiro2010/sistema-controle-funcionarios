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

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrações
python manage.py migrate --noinput

# Verificar instalação
echo "Python path: $(which python)"
echo "Daphne path: $(which daphne)"

echo "Build completed successfully!" 