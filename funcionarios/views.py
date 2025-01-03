from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import Funcionario, Ferias, Plantao

def is_admin(user):
    return user.is_superuser

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
    ferias_atuais = Ferias.objects.filter(
        data_inicio__lte=datetime.now().date(),
        data_fim__gte=datetime.now().date()
    )
    proximos_plantoes = Plantao.objects.filter(
        data__gte=datetime.now().date()
    ).order_by('data')[:5]
    
    # Estatísticas
    total_funcionarios = funcionarios.count()
    funcionarios_em_ferias = ferias_atuais.count()
    total_plantoes_mes = Plantao.objects.filter(
        data__year=datetime.now().year,
        data__month=datetime.now().month
    ).count()
    
    context = {
        'funcionarios': funcionarios,
        'ferias_atuais': ferias_atuais,
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
            
        # Verificar se já existe férias no período
        ferias_existentes = Ferias.objects.filter(
            funcionario=funcionario
        ).filter(
            Q(data_inicio__range=(data_inicio, data_fim)) |
            Q(data_fim__range=(data_inicio, data_fim))
        )
        
        if ferias_existentes.exists():
            messages.error(request, 'Já existem férias registradas que conflitam com este período.')
            return redirect('registrar_ferias')
            
        Ferias.objects.create(
            funcionario=funcionario,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_utilizados=dias,
            status='aprovado'  # Férias já são registradas como aprovadas
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
