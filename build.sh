#!/usr/bin/env bash
set -o errexit

# Instalar dependências
pip install -r requirements.txt

# Criar diretório de arquivos estáticos
mkdir -p staticfiles

# Finalizar build
echo "Build completed successfully!" 