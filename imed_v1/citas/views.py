from django.shortcuts import render
from django.utils import timezone
from .models import Cita
from medicos.models import Medico
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from medicos.models import Medico


def listado_citas_por_medico(request):
    hoy = timezone.localdate()
    medicos = Medico.objects.all().select_related('usuario')
    citas_por_medico = {
        medico: Cita.objects.filter(medico=medico, fecha=hoy).select_related('paciente__usuario').order_by('hora')
        for medico in medicos
    }
    return render(request, 'citas/listado_citas.html', {
        'fecha': hoy,
        'citas_por_medico': citas_por_medico
    })


@staff_member_required
def listado_citas_admin(request):
    hoy = timezone.localdate()
    medicos = Medico.objects.select_related('usuario')
    citas_por_medico = {
        medico: Cita.objects.filter(medico=medico, fecha=hoy).select_related('paciente__usuario').order_by('hora')
        for medico in medicos
    }
    return render(request, 'admin/citas/listado_citas_admin.html', {
        'fecha': hoy,
        'citas_por_medico': citas_por_medico
    })
