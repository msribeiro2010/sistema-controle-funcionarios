#!/usr/bin/env bash
set -o errexit

# Instalar dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

# Criar diretório de arquivos estáticos
mkdir -p staticfiles

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrações
python manage.py migrate --noinput

# Dar permissão ao script de inicialização
chmod +x start.sh

echo "Build completed successfully!" 