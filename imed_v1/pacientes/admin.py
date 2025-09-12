from django.contrib import admin
from .models import Paciente, Antecedente, Alergia, Patologia, ContactoPaciente, SEXO_CHOICES

# Paneles personalizados
from django.contrib import admin
from .models import Paciente, Alergia, Patologia, Antecedente, ContactoPaciente

class AlergiaInline(admin.TabularInline):
    model = Alergia
    extra = 0
    fields = ('nombre', 'descripcion')
    show_change_link = True

class PatologiaInline(admin.TabularInline):
    model = Patologia
    extra = 0
    fields = ('nombre', 'cronica', 'fecha_diagnostico')
    show_change_link = True

class AntecedenteInline(admin.TabularInline):
    model = Antecedente
    extra = 0
    fields = ('tipo', 'descripcion')
    show_change_link = True

class ContactoPacienteInline(admin.TabularInline):
    model = ContactoPaciente
    extra = 0
    fields = ('nombre', 'parentesco', 'telefonos')
    show_change_link = True


class PacienteAdmin(admin.ModelAdmin):
    list_display = ('usuario_nombre', 'sexo_display', 'telefono', 'estatus')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'telefono')
    list_filter = ('sexo', 'estatus')
    ordering = ('usuario__last_name',)

    fieldsets = (
        ('Datos personales', {
            'fields': ('usuario', 'fecha_nacimiento', 'sexo', 'direccion')
        }),
        ('Contacto', {
            'fields': ('telefono', 'contacto_emergencia', 'telefono_emergencia')
        }),
        ('Estado', {
            'fields': ('estatus',)
        }),
    )

    inlines = [AlergiaInline, PatologiaInline, AntecedenteInline, ContactoPacienteInline]

    def usuario_nombre(self, obj):
        return obj.usuario.get_full_name()
    usuario_nombre.short_description = 'Nombre completo'

    def sexo_display(self, obj):
        return dict(SEXO_CHOICES).get(obj.sexo, 'Desconocido')
    sexo_display.short_description = 'Sexo'



# Register your models here.
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Antecedente)
admin.site.register(Alergia)
admin.site.register(Patologia)
admin.site.register(ContactoPaciente)