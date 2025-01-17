# Generated by Django 5.1.4 on 2025-01-05 13:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("funcionarios", "0006_alter_feriado_tipo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Documento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titulo", models.CharField(max_length=100, verbose_name="Título")),
                (
                    "arquivo",
                    models.FileField(
                        upload_to="documentos/%Y/%m/", verbose_name="Arquivo"
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("FERIAS", "Férias"),
                            ("ATESTADO", "Atestado"),
                            ("DECLARACAO", "Declaração"),
                            ("OUTROS", "Outros"),
                        ],
                        max_length=50,
                        verbose_name="Tipo",
                    ),
                ),
                (
                    "data_upload",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Upload"
                    ),
                ),
                (
                    "observacoes",
                    models.TextField(blank=True, null=True, verbose_name="Observações"),
                ),
                (
                    "funcionario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documentos",
                        to="funcionarios.funcionario",
                        verbose_name="Funcionário",
                    ),
                ),
            ],
            options={
                "verbose_name": "Documento",
                "verbose_name_plural": "Documentos",
                "ordering": ["-data_upload"],
            },
        ),
    ]