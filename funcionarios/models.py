from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Funcionario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuário')
    nome = models.CharField('Nome', max_length=100)
    matricula = models.CharField('Matrícula', max_length=20, unique=True)
    cargo = models.CharField('Cargo', max_length=50, blank=True, null=True)
    dias_ferias_disponiveis = models.IntegerField('Dias de Férias Disponíveis', default=30)

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

class Ferias(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('negado', 'Negado'),
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='ferias', verbose_name='Funcionário')
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    dias_utilizados = models.IntegerField('Dias Utilizados')
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Férias'
        verbose_name_plural = 'Férias'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"Férias de {self.funcionario.nome} - {self.data_inicio} até {self.data_fim}"

class Plantao(models.Model):
    TIPO_CHOICES = [
        ('fds', 'Fim de Semana'),
        ('feriado', 'Feriado'),
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='plantoes', verbose_name='Funcionário')
    data = models.DateField('Data')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Plantão'
        verbose_name_plural = 'Plantões'
        ordering = ['data']

    def __str__(self):
        return f"Plantão de {self.funcionario.nome} em {self.data}"
