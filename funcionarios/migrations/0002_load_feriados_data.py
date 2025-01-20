from django.db import migrations

def load_feriados(apps, schema_editor):
    Feriado = apps.get_model('funcionarios', 'Feriado')
    feriados = [
        {
            'data': '2024-01-01',
            'descricao': 'Confraternização Universal',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-02-12',
            'descricao': 'Carnaval',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-02-13',
            'descricao': 'Carnaval',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-03-29',
            'descricao': 'Sexta-feira Santa',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-04-21',
            'descricao': 'Tiradentes',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-05-01',
            'descricao': 'Dia do Trabalho',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-05-30',
            'descricao': 'Corpus Christi',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-09-07',
            'descricao': 'Independência do Brasil',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-10-12',
            'descricao': 'Nossa Senhora Aparecida',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-11-02',
            'descricao': 'Finados',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-11-15',
            'descricao': 'Proclamação da República',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
        {
            'data': '2024-12-25',
            'descricao': 'Natal',
            'tipo': 'NACIONAL',
            'recorrente': True
        },
    ]
    
    for feriado in feriados:
        Feriado.objects.create(**feriado)

def reverse_load_feriados(apps, schema_editor):
    Feriado = apps.get_model('funcionarios', 'Feriado')
    Feriado.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('funcionarios', '0014_alter_funcionario_cargo'),  # Atualizado para a última migration
    ]

    operations = [
        migrations.RunPython(load_feriados, reverse_load_feriados),
    ] 