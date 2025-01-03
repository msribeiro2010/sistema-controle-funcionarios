from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import Funcionario, Ferias, Plantao

def is_admin(user):
    return user.is_superuser

def verificar_conflito_ferias(data_inicio, data_fim, cargo, funcionario_atual=None):
    """Verifica se há conflito de férias para funcionários do mesmo cargo."""
    # Verifica se existe alguma sobreposição de datas
    query = Q(
        Q(data_inicio__lte=data_fim, data_fim__gte=data_inicio) |  # Sobreposição completa
        Q(data_inicio__lte=data_inicio, data_fim__gte=data_inicio) |  # Início dentro de outro período
        Q(data_inicio__lte=data_fim, data_fim__gte=data_fim)  # Fim dentro de outro período
    )
    
    ferias_conflitantes = Ferias.objects.filter(
        query,
        funcionario__cargo=cargo
    )
    
    if funcionario_atual:
        ferias_conflitantes = ferias_conflitantes.exclude(funcionario=funcionario_atual)
    
    return ferias_conflitantes

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
        
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        messages.warning(request, 'Por favor, crie um registro de Funcionário no painel administrativo primeiro.')
        return redirect('admin:funcionarios_funcionario_add')

    ferias = Ferias.objects.filter(funcionario=funcionario)
    proximos_plantoes = Plantao.objects.filter(
        funcionario=funcionario,
        data__gte=datetime.now().date()
    ).order_by('data')[:5]

    context = {
        'funcionario': funcionario,
        'ferias': ferias,
        'proximos_plantoes': proximos_plantoes,
    }
    return render(request, 'funcionarios/dashboard.html', context)

@user_passes_test(is_admin)
def admin_dashboard(request):
    funcionarios = Funcionario.objects.all()
    hoje = datetime.now().date()
    
    # Buscar todas as férias atuais e futuras (próximos 30 dias)
    ferias_atuais = Ferias.objects.filter(
        Q(data_inicio__lte=hoje + timedelta(days=30), data_fim__gte=hoje)
    ).select_related('funcionario').order_by('data_inicio')
    
    # Verificar conflitos para cada período de férias
    ferias_com_conflito = set()
    conflitos_por_ferias = {}
    
    for ferias in ferias_atuais:
        # Verificar conflitos com outras férias do mesmo cargo
        outros_conflitos = verificar_conflito_ferias(
            ferias.data_inicio,
            ferias.data_fim,
            ferias.funcionario.cargo
        ).exclude(id=ferias.id)
        
        if outros_conflitos.exists():
            ferias_com_conflito.add(ferias.id)
            conflitos_por_ferias[ferias.id] = [f.funcionario.nome for f in outros_conflitos]
            for conflito in outros_conflitos:
                ferias_com_conflito.add(conflito.id)
                if conflito.id not in conflitos_por_ferias:
                    conflitos_por_ferias[conflito.id] = [ferias.funcionario.nome]
    
    proximos_plantoes = Plantao.objects.filter(
        data__gte=hoje
    ).order_by('data')[:5]
    
    # Estatísticas
    total_funcionarios = funcionarios.count()
    funcionarios_em_ferias = ferias_atuais.filter(data_inicio__lte=hoje, data_fim__gte=hoje).count()
    total_plantoes_mes = Plantao.objects.filter(
        data__year=hoje.year,
        data__month=hoje.month
    ).count()
    
    context = {
        'funcionarios': funcionarios,
        'ferias_atuais': ferias_atuais,
        'ferias_com_conflito': ferias_com_conflito,
        'conflitos_por_ferias': conflitos_por_ferias,
        'proximos_plantoes': proximos_plantoes,
        'total_funcionarios': total_funcionarios,
        'funcionarios_em_ferias': funcionarios_em_ferias,
        'total_plantoes_mes': total_plantoes_mes,
    }
    return render(request, 'funcionarios/admin_dashboard.html', context)

@user_passes_test(is_admin)
def registrar_ferias(request):
    if request.method == 'POST':
        funcionario_id = request.POST.get('funcionario')
        data_inicio = datetime.strptime(request.POST['data_inicio'], '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.POST['data_fim'], '%Y-%m-%d').date()
        dias = (data_fim - data_inicio).days + 1
        
        funcionario = get_object_or_404(Funcionario, id=funcionario_id)
        
        if dias > funcionario.dias_ferias_disponiveis:
            messages.error(request, 'O funcionário não possui dias suficientes de férias disponíveis.')
            return redirect('registrar_ferias')
        
        # Verificar se já existe férias no período para o mesmo funcionário
        ferias_proprio_funcionario = Ferias.objects.filter(
            funcionario=funcionario,
            data_inicio__lte=data_fim,
            data_fim__gte=data_inicio
        )
        
        if ferias_proprio_funcionario.exists():
            messages.error(request, 'Este funcionário já possui férias registradas neste período.')
            return redirect('registrar_ferias')
        
        # Verificar conflitos com outros funcionários do mesmo cargo
        ferias_conflitantes = verificar_conflito_ferias(data_inicio, data_fim, funcionario.cargo)
        
        if ferias_conflitantes.exists():
            funcionarios_conflito = ", ".join([
                f"{f.funcionario.nome} ({f.data_inicio.strftime('%d/%m/%Y')} a {f.data_fim.strftime('%d/%m/%Y')})"
                for f in ferias_conflitantes
            ])
            messages.error(
                request,
                f'ATENÇÃO: Conflito detectado! Os seguintes funcionários do cargo {funcionario.cargo} '
                f'já têm férias registradas que se sobrepõem a este período:\n\n{funcionarios_conflito}\n\n'
                'Por favor, escolha um período diferente para evitar problemas de cobertura.'
            )
            return redirect('registrar_ferias')
            
        Ferias.objects.create(
            funcionario=funcionario,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_utilizados=dias,
            status='aprovado'
        )
        
        # Atualizar dias disponíveis
        funcionario.dias_ferias_disponiveis -= dias
        funcionario.save()
        
        messages.success(request, 'Férias registradas com sucesso!')
        return redirect('admin_dashboard')
        
    funcionarios = Funcionario.objects.all()
    return render(request, 'funcionarios/registrar_ferias.html', {'funcionarios': funcionarios})

@login_required
def calendario(request):
    hoje = datetime.now().date()
    inicio_mes = hoje.replace(day=1)
    if hoje.month == 12:
        fim_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        fim_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    
    ferias = Ferias.objects.filter(
        Q(data_inicio__range=(inicio_mes, fim_mes)) |
        Q(data_fim__range=(inicio_mes, fim_mes))
    )
    
    plantoes = Plantao.objects.filter(
        data__range=(inicio_mes, fim_mes)
    )
    
    context = {
        'ferias': ferias,
        'plantoes': plantoes,
        'inicio_mes': inicio_mes,
        'fim_mes': fim_mes,
    }
    return render(request, 'funcionarios/calendario.html', context)
