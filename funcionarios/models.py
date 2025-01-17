from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta

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

class Feriado(models.Model):
    TIPO_CHOICES = (
        ('NACIONAL', 'Nacional'),
        ('ESTADUAL', 'Estadual'),
        ('MUNICIPAL', 'Municipal'),
    )
    
    data = models.DateField()
    descricao = models.CharField('Descrição', max_length=255)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='NACIONAL'
    )
    recorrente = models.BooleanField(
        'Feriado Recorrente',
        default=False,
        help_text='Marque se este feriado se repete todos os anos'
    )

    class Meta:
        verbose_name = 'Feriado'
        verbose_name_plural = 'Feriados'
        ordering = ['data']

    def __str__(self):
        return f"{self.descricao} - {self.data.strftime('%d/%m/%Y')}"

    @property
    def ja_passou(self):
        hoje = date.today()
        if self.recorrente:
            feriado_este_ano = date(hoje.year, self.data.month, self.data.day)
            return feriado_este_ano < hoje
        return self.data < hoje

class Ferias(models.Model):
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('USUFRUIDO', 'Usufruído'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    data_retorno = models.DateField(null=True, blank=True)
    dias_utilizados = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    
    def calcular_data_retorno(self):
        """Calcula a data de retorno considerando finais de semana e feriados."""
        data_retorno = self.data_fim + timedelta(days=1)
        
        while True:
            # Verifica se é final de semana (5 = Sábado, 6 = Domingo)
            if data_retorno.weekday() >= 5:
                data_retorno += timedelta(days=1)
                continue
            
            # Verifica se é feriado (incluindo feriados recorrentes)
            feriado_normal = Feriado.objects.filter(data=data_retorno).exists()
            feriado_recorrente = Feriado.objects.filter(
                data__month=data_retorno.month,
                data__day=data_retorno.day,
                recorrente=True
            ).exists()
            
            if feriado_normal or feriado_recorrente:
                data_retorno += timedelta(days=1)
                continue
            
            break
        
        return data_retorno
    
    def verificar_conflitos(self):
        """Verifica se há conflito com outras férias do mesmo cargo."""
        conflitos = Ferias.objects.filter(
            funcionario__cargo=self.funcionario.cargo,
            status__in=['AGENDADO', 'EM_ANDAMENTO'],
            data_inicio__lte=self.data_fim,
            data_fim__gte=self.data_inicio
        ).exclude(id=self.pk)
        return conflitos

    def clean(self):
        """Validação do modelo."""
        if self.data_inicio and self.data_fim:
            if self.data_inicio > self.data_fim:
                raise ValidationError('A data de início não pode ser posterior à data de fim.')
            
            # Calcula os dias utilizados
            dias = (self.data_fim - self.data_inicio).days + 1
            if not self.pk and dias > self.funcionario.dias_ferias_disponiveis:
                raise ValidationError(
                    f'Dias solicitados ({dias}) excedem os dias disponíveis '
                    f'({self.funcionario.dias_ferias_disponiveis}).'
                )
            self.dias_utilizados = dias
            
            # Verifica conflitos
            if self.verificar_conflitos().exists():
                nomes_conflitantes = ', '.join([f.funcionario.nome for f in self.verificar_conflitos()])
                raise ValidationError(
                    f'Conflito de férias com: {nomes_conflitantes}. Já existe outro funcionário do mesmo cargo com férias agendadas neste período.'
                )

    def save(self, *args, **kwargs):
        # Calcula a data de retorno antes de salvar
        self.data_retorno = self.calcular_data_retorno()
        
        # Se é um novo registro (não tem pk ainda)
        if not self.pk:
            self.funcionario.dias_ferias_disponiveis -= self.dias_utilizados
            self.funcionario.save()
        
        # Se está sendo cancelado
        if self.status == 'CANCELADO' and self.pk:
            ferias_anterior = Ferias.objects.get(pk=self.pk)
            if ferias_anterior.status != 'CANCELADO':
                self.funcionario.dias_ferias_disponiveis += self.dias_utilizados
                if self.funcionario.dias_ferias_disponiveis > 30:
                    self.funcionario.dias_ferias_disponiveis = 30
                self.funcionario.save()
        
        # Atualiza o status baseado nas datas
        hoje = date.today()
        if hoje > self.data_fim and self.status != 'CANCELADO':
            self.status = 'USUFRUIDO'
        elif hoje >= self.data_inicio and hoje <= self.data_fim and self.status != 'CANCELADO':
            self.status = 'EM_ANDAMENTO'
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Ao deletar férias, retorna os dias ao funcionário."""
        if self.status != 'CANCELADO':
            self.funcionario.dias_ferias_disponiveis += self.dias_utilizados
            if self.funcionario.dias_ferias_disponiveis > 30:
                self.funcionario.dias_ferias_disponiveis = 30
            self.funcionario.save()
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Férias'
        verbose_name_plural = 'Férias'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"Férias de {self.funcionario.nome} - {self.get_status_display()}"

    def atualizar_status(self):
        """Atualiza manualmente o status das férias com base na data atual."""
        hoje = date.today()
        if hoje > self.data_fim and self.status != 'CANCELADO':
            self.status = 'USUFRUIDO'
        elif hoje >= self.data_inicio and hoje <= self.data_fim and self.status != 'CANCELADO':
            self.status = 'EM_ANDAMENTO'
        self.save()

class Plantao(models.Model):
    TIPO_CHOICES = [
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
        ('fds', 'Fim de Semana Completo'),
        ('feriado', 'Feriado'),
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='plantoes', verbose_name='Funcionário')
    data = models.DateField('Data')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    observacoes = models.TextField('Observações', blank=True, null=True)
    folgas_geradas = models.IntegerField('Folgas Geradas', default=0)
    folgas_utilizadas = models.IntegerField('Folgas Utilizadas', default=0)
    folgas_restantes = models.IntegerField('Folgas Restantes', default=0)

    def clean(self):
        super().clean()
        if self.data:
            # Verifica se já existe plantão nesta data
            plantao_existente = Plantao.objects.filter(data=self.data)
            if self.pk:  # Se está editando um plantão existente
                plantao_existente = plantao_existente.exclude(pk=self.pk)
            
            if plantao_existente.exists():
                funcionarios_com_plantao = ", ".join([p.funcionario.nome for p in plantao_existente])
                raise ValidationError({
                    'data': f'Já existe(m) plantão(ões) registrado(s) nesta data para o(s) funcionário(s): {funcionarios_com_plantao}'
                })

    def save(self, *args, **kwargs):
        self.clean()  # Garante que a validação seja executada
        # Define o número de folgas com base no tipo de plantão
        if not self.pk:  # Apenas na criação
            if self.tipo == 'sabado' or self.tipo == 'domingo':
                self.folgas_geradas = 1
            elif self.tipo == 'fds':
                self.folgas_geradas = 2
            else:
                self.folgas_geradas = 1
            self.folgas_restantes = self.folgas_geradas
        
        # Sempre atualiza folgas restantes
        self.folgas_restantes = self.folgas_geradas - self.folgas_utilizadas
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Plantão'
        verbose_name_plural = 'Plantões'
        ordering = ['data']

    def __str__(self):
        return f"Plantão de {self.funcionario.nome} em {self.data}"

class UsoFolga(models.Model):
    plantao = models.ForeignKey(Plantao, on_delete=models.CASCADE, related_name='usos_folga', verbose_name='Plantão')
    data = models.DateField('Data da Folga')
    observacoes = models.TextField('Observações', blank=True, null=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Se é uma nova folga
            if self.plantao.folgas_restantes <= 0:
                raise ValidationError('Não há folgas disponíveis para este plantão.')
            self.plantao.folgas_utilizadas += 1
            self.plantao.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.plantao.folgas_utilizadas -= 1
        self.plantao.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Uso de Folga'
        verbose_name_plural = 'Usos de Folgas'
        ordering = ['-data']

    def __str__(self):
        return f"Folga de {self.plantao.funcionario.nome} em {self.data}"

class Documento(models.Model):
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='documentos', verbose_name='Funcionário')
    titulo = models.CharField('Título', max_length=100)
    arquivo = models.FileField('Arquivo', upload_to='documentos/%Y/%m/')
    tipo = models.CharField('Tipo', max_length=50, choices=[
        ('FERIAS', 'Férias'),
        ('ATESTADO', 'Atestado'),
        ('DECLARACAO', 'Declaração'),
        ('OUTROS', 'Outros')
    ])
    data_upload = models.DateTimeField('Data de Upload', auto_now_add=True)
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-data_upload']

    def __str__(self):
        return f"{self.titulo} - {self.funcionario.nome}"

class Presenca(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, verbose_name='Funcionário')
    data = models.DateField('Data')
    presente = models.BooleanField('Presente', default=False)
    observacoes = models.TextField('Observações', blank=True, null=True)
    tipo_trabalho = models.CharField('Tipo de Trabalho', max_length=20, choices=[('PRESENCIAL', 'Presencial'), ('TELETRABALHO', 'Teletrabalho')], default='PRESENCIAL')

    class Meta:
        verbose_name = 'Presencial'
        verbose_name_plural = 'Presencial'
        ordering = ['-data']

    def __str__(self):
        return f"Presencial de {self.funcionario.nome} em {self.data}"

class Folga(models.Model):
    TIPO_CHOICES = [
        ('COMPENSATORIA', 'Compensatória'),
        ('LICENCA', 'Licença'),
    ]
    
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, verbose_name='Funcionário')
    data = models.DateField('Data')
    tipo_folga = models.CharField('Tipo de Folga', max_length=20, choices=TIPO_CHOICES, default='COMPENSATORIA')
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Folga'
        verbose_name_plural = 'Folgas'
        ordering = ['-data']

    def __str__(self):
        return f"Folga de {self.funcionario.nome} em {self.data}"
