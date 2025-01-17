#!/bin/bash

# Instalar dependências do sistema
apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    python3-dev

# Instalar dependências Python
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt 