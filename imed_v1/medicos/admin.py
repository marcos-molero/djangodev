from django.contrib import admin
from .models import Medico, Especialidad, Horario, DIAS_CHOICES


# Modelos para el Admin personalizados.
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('medico', 'descripcion', 'dia', 'hora_inicio', 'hora_fin')
    list_filter = ('dia', 'medico')
    search_fields = ('medico__usuario__first_name', 'medico__usuario__last_name')
    ordering = ('medico__usuario__last_name', 'dia', 'hora_inicio')
    fields = ('medico', 'descripcion', 'dia', 'hora_inicio', 'hora_fin')

    def medico_nombre(self, obj):
        return obj.medico.usuario.get_full_name()
    medico_nombre.short_description = 'Médico'

    def dia_display(self, obj):
        return obj.get_dia_display()
    dia_display.short_description = 'Día'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        dias = dict(DIAS_CHOICES)
        horarios_por_dia = {
            dia: Horario.objects.filter(dia=dia).select_related('medico')
            for dia in dias.keys()
        }
        extra_context['horarios_por_dia'] = horarios_por_dia
        return super().changelist_view(request, extra_context=extra_context)


# Register your models here. 
admin.site.register(Medico)
admin.site.register(Especialidad)
admin.site.register(Horario, HorarioAdmin)