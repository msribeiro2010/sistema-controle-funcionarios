# Generated by Django 5.1.4 on 2025-01-05 14:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("funcionarios", "0007_documento"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ferias",
            name="data_atualizacao",
        ),
        migrations.RemoveField(
            model_name="ferias",
            name="data_criacao",
        ),
        migrations.AlterField(
            model_name="ferias",
            name="data_fim",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="ferias",
            name="data_inicio",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="ferias",
            name="data_retorno",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="ferias",
            name="dias_utilizados",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="ferias",
            name="funcionario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="funcionarios.funcionario",
            ),
        ),
        migrations.AlterField(
            model_name="ferias",
            name="status",
            field=models.CharField(
                choices=[
                    ("AGENDADO", "Agendado"),
                    ("EM_ANDAMENTO", "Em Andamento"),
                    ("USUFRUIDO", "Usufruído"),
                    ("CANCELADO", "Cancelado"),
                ],
                default="AGENDADO",
                max_length=20,
            ),
        ),
    ]
