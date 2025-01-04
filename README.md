# Sistema de Controle de Funcionários

Sistema web para gerenciamento de funcionários, férias e plantões.

## Funcionalidades

- Cadastro e gerenciamento de funcionários
- Controle de férias com detecção de conflitos
- Gerenciamento de plantões
- Dashboard administrativo
- Controle de saldo de férias
- Status automático de férias (Agendado, Em Andamento, Usufruído)

## Requisitos

- Python 3.8 ou superior
- PostgreSQL
- pip (gerenciador de pacotes Python)

## Instalação em Produção

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/controle-funcionarios.git
cd controle-funcionarios
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com suas configurações:
- Gere uma nova SECRET_KEY
- Configure as credenciais do banco de dados
- Ajuste outras configurações conforme necessário

5. Configure o banco de dados PostgreSQL:
```bash
createdb controle_funcionarios  # Crie o banco de dados
python manage.py migrate  # Execute as migrações
```

6. Colete os arquivos estáticos:
```bash
python manage.py collectstatic
```

7. Crie um superusuário:
```bash
python manage.py createsuperuser
```

8. Inicie o servidor Gunicorn:
```bash
gunicorn controle_funcionarios.wsgi:application
```

## Configuração do Servidor Web (Nginx)

Exemplo de configuração do Nginx:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /caminho/para/seu/projeto;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

## Configuração do Supervisor

Exemplo de configuração do Supervisor para manter o Gunicorn rodando:

```ini
[program:controle-funcionarios]
command=/caminho/para/seu/projeto/.venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock controle_funcionarios.wsgi:application
directory=/caminho/para/seu/projeto
user=seu-usuario
autostart=true
autorestart=true
stderr_logfile=/var/log/controle-funcionarios/gunicorn.err.log
stdout_logfile=/var/log/controle-funcionarios/gunicorn.out.log
```

## Manutenção

### Backup do Banco de Dados
```bash
pg_dump controle_funcionarios > backup.sql
```

### Atualização do Sistema
```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart controle-funcionarios
```

## Segurança

- Mantenha o Django e todas as dependências atualizadas
- Use HTTPS em produção
- Faça backup regularmente
- Monitore os logs do sistema
- Configure corretamente o firewall

## Suporte

Para suporte, entre em contato através de [seu-email@dominio.com]
