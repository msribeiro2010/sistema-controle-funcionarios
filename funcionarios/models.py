from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

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
        ('AGENDADO', 'Agendado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('USUFRUIDO', 'Usufruído'),
        ('CANCELADO', 'Cancelado'),
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='ferias', verbose_name='Funcionário')
    data_inicio = models.DateField('Data de Início', default=date.today)
    data_fim = models.DateField('Data de Fim', default=date.today)
    dias_utilizados = models.IntegerField('Dias Utilizados')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    data_criacao = models.DateTimeField('Data de Criação', default=timezone.now)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)

    def save(self, *args, **kwargs):
        # Se é uma nova instância (não tem ID ainda)
        if not self.pk:
            # Deduz os dias de férias do saldo do funcionário
            self.funcionario.dias_ferias_disponiveis -= self.dias_utilizados
            self.funcionario.save()
        
        # Atualiza o status baseado nas datas
        hoje = date.today()
        if hoje > self.data_fim:
            self.status = 'USUFRUIDO'
        elif hoje >= self.data_inicio and hoje <= self.data_fim:
            self.status = 'EM_ANDAMENTO'
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Antes de excluir, devolve os dias ao saldo do funcionário
        # Apenas se o status não for 'USUFRUIDO'
        if self.status != 'USUFRUIDO':
            self.funcionario.dias_ferias_disponiveis += self.dias_utilizados
            self.funcionario.save()
        super().delete(*args, **kwargs)

    def clean(self):
        if self.data_inicio and self.data_fim:
            if self.data_inicio > self.data_fim:
                raise ValidationError('A data de início não pode ser posterior à data de fim.')
            
            # Calcula os dias utilizados
            dias = (self.data_fim - self.data_inicio).days + 1
            if dias > self.funcionario.dias_ferias_disponiveis and not self.pk:
                raise ValidationError(
                    f'Dias solicitados ({dias}) excedem os dias disponíveis '
                    f'({self.funcionario.dias_ferias_disponiveis}).'
                )
            self.dias_utilizados = dias

    def __str__(self):
        return f"Férias de {self.funcionario.nome} - {self.get_status_display()}"

    class Meta:
        verbose_name = 'Férias'
        verbose_name_plural = 'Férias'
        ordering = ['-data_inicio']

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
