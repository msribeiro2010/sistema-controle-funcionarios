from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from datetime import datetime, timedelta, date
from .models import Funcionario, Ferias, Plantao, Feriado, Presenca, Folga
from django.contrib.auth import logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import PermissionDenied
import calendar
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

def logout_view(request):
    logout(request)
    return redirect('admin:login')

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

@ensure_csrf_cookie
@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('escolha_acao')

@user_passes_test(is_admin)
def admin_dashboard(request):
    funcionarios = Funcionario.objects.all()
    hoje = datetime.now().date()
    
    # Buscar todas as férias atuais e futuras (próximos 30 dias)
    ferias_atuais = Ferias.objects.filter(
        Q(data_inicio__lte=hoje + timedelta(days=30), data_fim__gte=hoje),
        status__in=['AGENDADO', 'EM_ANDAMENTO']
    ).select_related('funcionario').order_by('data_inicio')
    
    # Verificar conflitos para cada período de férias
    ferias_com_conflito = set()
    conflitos_por_ferias = {}
    
    for ferias in ferias_atuais:
        conflitos = Ferias.objects.filter(
            funcionario__cargo=ferias.funcionario.cargo,
            status__in=['AGENDADO', 'EM_ANDAMENTO'],
            data_inicio__lte=ferias.data_fim,
            data_fim__gte=ferias.data_inicio
        ).exclude(id=ferias.id)
        
        if conflitos.exists():
            ferias_com_conflito.add(ferias.id)
            conflitos_por_ferias[ferias.id] = [f.funcionario.nome for f in conflitos]
            for conflito in conflitos:
                ferias_com_conflito.add(conflito.id)
                if conflito.id not in conflitos_por_ferias:
                    conflitos_por_ferias[conflito.id] = []
                conflitos_por_ferias[conflito.id].append(ferias.funcionario.nome)
    
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
    
    # Filtrar apenas feriados futuros ou do dia atual
    feriados = Feriado.objects.filter(data__gte=date.today()).order_by('data')
    
    context = {
        'funcionarios': funcionarios,
        'ferias_atuais': ferias_atuais,
        'ferias_com_conflito': ferias_com_conflito,
        'conflitos_por_ferias': conflitos_por_ferias,
        'proximos_plantoes': proximos_plantoes,
        'total_funcionarios': total_funcionarios,
        'funcionarios_em_ferias': funcionarios_em_ferias,
        'total_plantoes_mes': total_plantoes_mes,
        'feriados': feriados,
        'hoje': date.today(),
    }
    return render(request, 'funcionarios/admin_dashboard.html', context)

@ensure_csrf_cookie
@login_required
def registrar_ferias_funcionario(request):
    if not request.user.is_authenticated:
        raise PermissionDenied

    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        messages.error(request, 'Funcionário não encontrado.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            data_inicio = datetime.strptime(request.POST['data_inicio'], '%Y-%m-%d').date()
            data_fim = datetime.strptime(request.POST['data_fim'], '%Y-%m-%d').date()
            dias = (data_fim - data_inicio).days + 1

            if dias > funcionario.dias_ferias_disponiveis:
                messages.error(request, 'Você não possui dias suficientes de férias disponíveis.')
                return redirect('registrar_ferias_funcionario')

            # Verificar se já existe férias no período
            ferias_existente = Ferias.objects.filter(
                funcionario=funcionario,
                data_inicio__lte=data_fim,
                data_fim__gte=data_inicio
            )

            if ferias_existente.exists():
                messages.error(request, 'Você já possui férias registradas neste período.')
                return redirect('registrar_ferias_funcionario')

            Ferias.objects.create(
                funcionario=funcionario,
                data_inicio=data_inicio,
                data_fim=data_fim,
                dias_utilizados=dias,
                status='AGENDADO'
            )

            messages.success(request, 'Férias registradas com sucesso!')
            return redirect('dashboard')
        except (ValueError, KeyError) as e:
            messages.error(request, 'Erro ao processar as datas. Por favor, tente novamente.')
            return redirect('registrar_ferias_funcionario')

    response = render(request, 'funcionarios/registrar_ferias.html', {'funcionario': funcionario})
    response.set_cookie('csrftoken', request.META.get('CSRF_COOKIE', ''), samesite='Lax')
    return response

@login_required
def registrar_plantao_funcionario(request):
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        messages.error(request, 'Funcionário não encontrado.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            data = datetime.strptime(request.POST['data'], '%Y-%m-%d').date()
            observacoes = request.POST.get('observacoes', '')
            
            # Determinar o tipo de plantão baseado no dia da semana
            dia_semana = data.weekday()
            if dia_semana == 5:  # Sábado
                tipo = 'sabado'
            elif dia_semana == 6:  # Domingo
                tipo = 'domingo'
            else:
                if Feriado.objects.filter(data=data).exists():
                    tipo = 'feriado'
                else:
                    messages.error(request, 'Data selecionada não é um fim de semana ou feriado.')
                    return redirect('registrar_plantao_funcionario')

            try:
                # Verificar se já existe um plantão para esta data
                plantao_existente = Plantao.objects.filter(
                    funcionario=funcionario,
                    data=data
                ).exists()

                if plantao_existente:
                    messages.error(request, 'Já existe um plantão registrado para esta data.')
                    return redirect('registrar_plantao_funcionario')

                # Criar o plantão
                Plantao.objects.create(
                    funcionario=funcionario,
                    data=data,
                    tipo=tipo,
                    observacoes=observacoes
                )

                messages.success(request, 'Plantão registrado com sucesso!')
                return redirect('servidor_dashboard')

            except Exception as e:
                messages.error(request, f'Erro ao registrar plantão: {str(e)}')
                return redirect('registrar_plantao_funcionario')

        except ValueError:
            messages.error(request, 'Data inválida.')
            return redirect('registrar_plantao_funcionario')

    return render(request, 'funcionarios/registrar_plantao.html', {'funcionario': funcionario})

@login_required
def calendario(request):
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        messages.error(request, 'Funcionário não encontrado.')
        return redirect('dashboard')

    hoje = datetime.now().date()
    inicio_mes = hoje.replace(day=1)
    if hoje.month == 12:
        fim_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        fim_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    
    ferias = Ferias.objects.filter(
        Q(funcionario=funcionario) &
        (Q(data_inicio__range=(inicio_mes, fim_mes)) |
         Q(data_fim__range=(inicio_mes, fim_mes)))
    )
    
    plantoes = Plantao.objects.filter(
        data__range=(inicio_mes, fim_mes)
    )
    
    calendario = []
    for dia in range((fim_mes - inicio_mes).days + 1):
        data_atual = inicio_mes + timedelta(days=dia)
        ferias_dia = ferias.filter(
            Q(data_inicio__lte=data_atual, data_fim__gte=data_atual)
        )
        plantoes_dia = plantoes.filter(data=data_atual)
        if ferias_dia.exists() or plantoes_dia.exists():
            calendario.append({'data': data_atual, 'ferias': ferias_dia, 'plantoes': plantoes_dia})

    context = {
        'calendario': calendario,
        'inicio_mes': inicio_mes,
        'fim_mes': fim_mes,
    }
    return render(request, 'funcionarios/calendario.html', context)

@login_required
def feriados(request):
    ano_atual = datetime.now().year
    feriados = Feriado.objects.filter(data__year=ano_atual).order_by('data')
    return render(request, 'funcionarios/feriados.html', {
        'feriados': feriados,
        'ano': ano_atual
    })

@login_required
def servidor_dashboard(request):
    funcionario = get_object_or_404(Funcionario, usuario=request.user)
    hoje = date.today()
    primeiro_dia_mes = hoje.replace(day=1)
    
    # Buscar presenças
    presencas = Presenca.objects.filter(funcionario=funcionario)
    presencas_mes = presencas.filter(data__gte=primeiro_dia_mes)
    
    # Buscar folgas
    folgas = Folga.objects.filter(funcionario=funcionario)
    folgas_mes = folgas.filter(data__gte=primeiro_dia_mes)
    
    # Buscar férias do funcionário
    ferias = Ferias.objects.filter(
        funcionario=funcionario
    ).order_by('-data_inicio')
    
    # Buscar plantões do funcionário
    plantoes = Plantao.objects.filter(
        funcionario=funcionario
    ).order_by('-data')
    
    # Buscar feriados do mês atual
    feriados = Feriado.objects.filter(
        data__year=hoje.year,
        data__month=hoje.month
    ).order_by('data')
    
    # Verificar conflitos nas férias
    ferias_com_conflito = {}
    for f in ferias:
        if f.status in ['AGENDADO', 'EM_ANDAMENTO']:
            conflitos = Ferias.objects.filter(
                funcionario__cargo=funcionario.cargo,
                status__in=['AGENDADO', 'EM_ANDAMENTO'],
                data_inicio__lte=f.data_fim,
                data_fim__gte=f.data_inicio
            ).exclude(id=f.id)
            
            if conflitos.exists():
                ferias_com_conflito[f.id] = [c.funcionario.nome for c in conflitos]
    
    context = {
        'funcionario': funcionario,
        'ferias': ferias,
        'plantoes': plantoes,
        'presencas': presencas,
        'presencas_mes': presencas_mes,
        'folgas': folgas,
        'folgas_mes': folgas_mes,
        'feriados': feriados,
        'ferias_com_conflito': ferias_com_conflito,
        'dias_ferias_disponiveis': funcionario.dias_ferias_disponiveis,
    }
    return render(request, 'funcionarios/servidor_dashboard.html', context)

@login_required
def cancelar_ferias(request, ferias_id):
    ferias = get_object_or_404(Ferias, id=ferias_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        ferias.funcionario.dias_ferias_disponiveis += ferias.dias_utilizados
        if ferias.funcionario.dias_ferias_disponiveis > 30:
            ferias.funcionario.dias_ferias_disponiveis = 30
        ferias.funcionario.save()
        ferias.delete()
        messages.success(request, 'Férias excluídas com sucesso.')
    
    return redirect('servidor_dashboard')

@login_required
def verificar_conflitos(request):
    try:
        funcionario = request.user.funcionario
        data_inicio = datetime.strptime(request.GET['inicio'], '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.GET['fim'], '%Y-%m-%d').date()
        
        conflitos = verificar_conflito_ferias(data_inicio, data_fim, funcionario.cargo, funcionario)
        
        return JsonResponse({
            'conflitos': [f.funcionario.nome for f in conflitos]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def escolha_acao(request):
    try:
        funcionario = Funcionario.objects.select_related('usuario').get(usuario=request.user)
    except Funcionario.DoesNotExist:
        messages.warning(request, 'Por favor, crie um registro de Funcionário no painel administrativo primeiro.')
        return redirect('admin:funcionarios_funcionario_add')

    total_plantoes = Plantao.objects.filter(funcionario=funcionario).count()
    
    context = {
        'funcionario': funcionario,
        'total_plantoes': total_plantoes,
    }
    return render(request, 'funcionarios/escolha_acao.html', context)

@login_required
def gerenciar_presenca(request):
    funcionario = get_object_or_404(Funcionario, usuario=request.user)
    if request.method == 'POST':
        tipo_trabalho = request.POST.get('tipo_trabalho')
        dias_selecionados = request.POST.getlist('dias')
        observacoes = request.POST.get('observacoes', '')

        for dia in dias_selecionados:
            data = datetime.strptime(dia, '%Y-%m-%d').date()
            Presenca.objects.create(funcionario=funcionario, data=data, tipo_trabalho=tipo_trabalho, observacoes=observacoes)

        messages.success(request, 'Presença registrada com sucesso!')
        return redirect('gerenciar_presenca')

    presencas = Presenca.objects.filter(funcionario=funcionario).order_by('-data')
    return render(request, 'funcionarios/gerenciar_presenca.html', {'presencas': presencas})

@login_required
def editar_ferias(request, ferias_id):
    ferias = get_object_or_404(Ferias, id=ferias_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        
        if data_inicio and data_fim:
            # Repor os dias antes de atualizar
            ferias.funcionario.dias_ferias_disponiveis += ferias.dias_utilizados
            
            ferias.data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            ferias.data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            ferias.dias_utilizados = (ferias.data_fim - ferias.data_inicio).days + 1
            
            # Deduzir os novos dias
            ferias.funcionario.dias_ferias_disponiveis -= ferias.dias_utilizados
            ferias.funcionario.save()
            ferias.save()
            messages.success(request, 'Férias atualizadas com sucesso!')
            return redirect('servidor_dashboard')

    return render(request, 'funcionarios/editar_ferias.html', {'ferias': ferias})

@login_required
def editar_plantao(request, plantao_id):
    plantao = get_object_or_404(Plantao, id=plantao_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        data = request.POST.get('data')
        observacoes = request.POST.get('observacoes')
        
        if data:
            try:
                data = datetime.strptime(data, '%Y-%m-%d').date()
                plantao.data = data
                plantao.observacoes = observacoes
                plantao.save()
                messages.success(request, 'Plantão atualizado com sucesso!')
                return redirect('servidor_dashboard')
            except ValueError:
                messages.error(request, 'Data inválida.')
        else:
            messages.error(request, 'Data é obrigatória.')
    
    return render(request, 'funcionarios/editar_plantao.html', {'plantao': plantao})

@login_required
def excluir_plantao(request, plantao_id):
    plantao = get_object_or_404(Plantao, id=plantao_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        plantao.delete()
        messages.success(request, 'Plantão excluído com sucesso!')
    
    return redirect('servidor_dashboard')

@login_required
def editar_presenca(request, presenca_id):
    presenca = get_object_or_404(Presenca, id=presenca_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        data = request.POST.get('data')
        tipo_trabalho = request.POST.get('tipo_trabalho')
        observacoes = request.POST.get('observacoes', '')
        
        if data and tipo_trabalho:
            presenca.data = datetime.strptime(data, '%Y-%m-%d').date()
            presenca.tipo_trabalho = tipo_trabalho
            presenca.observacoes = observacoes
            presenca.save()
            messages.success(request, 'Presença atualizada com sucesso!')
            return redirect('servidor_dashboard')

    return render(request, 'funcionarios/editar_presenca.html', {'presenca': presenca})

@login_required
def excluir_presenca(request, presenca_id):
    presenca = get_object_or_404(Presenca, id=presenca_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        presenca.delete()
        messages.success(request, 'Presença excluída com sucesso!')
    
    return redirect('servidor_dashboard')

@login_required
def gerenciar_folgas(request):
    funcionario = get_object_or_404(Funcionario, usuario=request.user)
    if request.method == 'POST':
        tipo_folga = request.POST.get('tipo_folga')
        dias_selecionados = request.POST.getlist('dias')
        observacoes = request.POST.get('observacoes', '')

        for dia in dias_selecionados:
            data = datetime.strptime(dia, '%d/%m/%Y').date()
            Folga.objects.create(funcionario=funcionario, data=data, tipo_folga=tipo_folga, observacoes=observacoes)

        messages.success(request, 'Folga registrada com sucesso!')
        return redirect('gerenciar_folgas')

    folgas = Folga.objects.filter(funcionario=funcionario).order_by('-data')
    return render(request, 'funcionarios/gerenciar_folgas.html', {'folgas': folgas})

def painel_funcionario(request):
    # ... código existente ...
    
    # Filtrar apenas feriados futuros ou do dia atual
    feriados = Feriado.objects.filter(data__gte=date.today()).order_by('data')
    
    context = {
        # ... outros dados do context ...
        'feriados': feriados,
        'hoje': date.today(),
    }
    
    return render(request, 'funcionarios/painel.html', context)

@login_required
def registrar_presenca(request):
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except Funcionario.DoesNotExist:
        messages.error(request, 'Funcionário não encontrado.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            data = datetime.strptime(request.POST['data'], '%Y-%m-%d').date()
            tipo_trabalho = request.POST.get('tipo_trabalho')
            observacoes = request.POST.get('observacoes', '')

            presenca = Presenca(
                funcionario=funcionario,
                data=data,
                tipo_trabalho=tipo_trabalho,
                observacoes=observacoes
            )
            presenca.full_clean()
            presenca.save()
            messages.success(request, 'Presença registrada com sucesso!')
            return redirect('historico_presencas')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{error}')
            return redirect('registrar_presenca')

    return render(request, 'funcionarios/registrar_presenca.html', {'funcionario': funcionario})

@login_required
def editar_folga(request, folga_id):
    folga = get_object_or_404(Folga, id=folga_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        data = request.POST.get('data')
        tipo_folga = request.POST.get('tipo_folga')
        observacoes = request.POST.get('observacoes', '')
        
        if data and tipo_folga:
            folga.data = datetime.strptime(data, '%Y-%m-%d').date()
            folga.tipo_folga = tipo_folga
            folga.observacoes = observacoes
            folga.save()
            messages.success(request, 'Folga atualizada com sucesso!')
            return redirect('servidor_dashboard')

    return render(request, 'funcionarios/editar_folga.html', {'folga': folga})

@login_required
def excluir_folga(request, folga_id):
    folga = get_object_or_404(Folga, id=folga_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        folga.delete()
        messages.success(request, 'Folga excluída com sucesso!')
    
    return redirect('servidor_dashboard')

@login_required
def excluir_ferias(request, ferias_id):
    ferias = get_object_or_404(Ferias, id=ferias_id, funcionario__usuario=request.user)
    
    if request.method == 'POST':
        # Verifica se as férias estão no status AGENDADO
        if ferias.status == 'AGENDADO':
            # Restaura os dias de férias disponíveis
            funcionario = ferias.funcionario
            funcionario.dias_ferias_disponiveis += ferias.dias_utilizados
            funcionario.save()
            
            # Exclui o registro de férias
            ferias.delete()
            messages.success(request, 'Férias excluídas com sucesso!')
        else:
            messages.error(request, 'Só é possível excluir férias com status AGENDADO.')
    
    return redirect('servidor_dashboard')

class CustomLoginView(LoginView):
    template_name = 'funcionarios/login.html'
    success_url = reverse_lazy('funcionarios:painel')
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return self.success_url

    def form_invalid(self, form):
        print(f"Login error: {form.errors}")  # Debug
        return super().form_invalid(form)
