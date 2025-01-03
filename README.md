# Sistema de Controle de Funcionários

Sistema desenvolvido em Django para gerenciamento de funcionários, controle de férias e plantões.

## Funcionalidades

- Cadastro e gerenciamento de funcionários
- Registro e controle de férias
- Agendamento de plantões
- Dashboard administrativo com estatísticas
- Painel individual para cada funcionário
- Sistema de autenticação integrado

## Tecnologias Utilizadas

- Python 3.8+
- Django 4.2.7
- Bootstrap 5
- SQLite (banco de dados)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Projeto-Controle-Funcionarios.git
cd Projeto-Controle-Funcionarios
```

2. Crie e ative um ambiente virtual:
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

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

6. Inicie o servidor:
```bash
python manage.py runserver
```

O sistema estará disponível em `http://127.0.0.1:8000/`

## Uso

1. Acesse o painel administrativo em `/admin` e crie os primeiros registros de funcionários
2. Os administradores podem:
   - Registrar férias para funcionários
   - Agendar plantões
   - Visualizar estatísticas gerais
3. Os funcionários podem:
   - Visualizar suas informações
   - Consultar histórico de férias
   - Ver próximos plantões agendados

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
