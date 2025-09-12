from django.contrib import admin
from citas.models import Cita
from .models import Cita

class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'medico_nombre', 'paciente_nombre', 'motivo')
    list_filter = ('fecha', 'medico')
    search_fields = ('medico__usuario__first_name', 'paciente__usuario__last_name')
    ordering = ('fecha', 'hora')

    def medico_nombre(self, obj):
        return obj.medico.usuario.get_full_name()
    medico_nombre.short_description = 'Médico'

    def paciente_nombre(self, obj):
        return obj.paciente.usuario.get_full_name()
    paciente_nombre.short_description = 'Paciente'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(medico__usuario=request.user)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['listado_url'] = '/admin/citas/listado-del-dia/'
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Cita, CitaAdmin)