import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar as settings do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from funcionarios.models import Feriado
from datetime import date, timedelta

def main():
    # Feriados Nacionais
    feriados = [
        ('2025-03-03', 'Carnaval', 'FACULTATIVO'),
        ('2025-03-04', 'Carnaval', 'FACULTATIVO'),
        ('2025-03-05', 'Quarta-feira de Cinzas', 'FACULTATIVO'),
        ('2025-04-16', 'Semana Santa', 'FACULTATIVO'),
        ('2025-04-17', 'Semana Santa', 'FACULTATIVO'),
        ('2025-04-18', 'Sexta-feira Santa', 'NACIONAL'),
        ('2025-04-21', 'Tiradentes', 'NACIONAL'),
        ('2025-05-01', 'Dia do Trabalho', 'NACIONAL'),
        ('2025-05-02', 'Emenda de Feriado', 'FACULTATIVO'),
        ('2025-06-19', 'Corpus Christi', 'FACULTATIVO'),
        ('2025-06-20', 'Emenda de Feriado', 'FACULTATIVO'),
        ('2025-07-09', 'Revolução Constitucionalista', 'ESTADUAL'),
        ('2025-08-11', 'Dia do Estudante', 'FACULTATIVO'),
        ('2025-10-27', 'Dia do Servidor Público', 'FACULTATIVO'),
        ('2025-11-20', 'Dia da Consciência Negra', 'MUNICIPAL'),
        ('2025-11-21', 'Emenda de Feriado', 'FACULTATIVO'),
        ('2025-12-08', 'Dia de Nossa Senhora da Conceição', 'MUNICIPAL'),
    ]

    # Criar os feriados
    for data, descricao, tipo in feriados:
        try:
            Feriado.objects.create(
                data=date.fromisoformat(data),
                descricao=descricao,
                tipo=tipo,
                recorrente=True
            )
            print(f"Criado feriado: {descricao} em {data}")
        except django.db.utils.IntegrityError:
            print(f"Feriado já existe: {descricao} em {data}")

    # Criar o período de recesso (20/12 a 06/01)
    ano = 2025
    mes_inicio = 12
    dia_inicio = 20
    mes_fim = 1
    dia_fim = 6

    data_inicio = date(ano, mes_inicio, dia_inicio)
    data_fim = date(ano + 1, mes_fim, dia_fim)

    dias_recesso = []
    data_atual = data_inicio
    while data_atual <= data_fim:
        dias_recesso.append(data_atual)
        data_atual += timedelta(days=1)

    # Criar os dias de recesso
    for data in dias_recesso:
        try:
            Feriado.objects.create(
                data=data,
                descricao='Recesso de Final de Ano',
                tipo='RECESSO',
                recorrente=True
            )
            print(f"Criado recesso em {data}")
        except django.db.utils.IntegrityError:
            print(f"Recesso já existe em {data}")

    print("\nFeriados e recesso criados com sucesso!")

if __name__ == '__main__':
    main() 