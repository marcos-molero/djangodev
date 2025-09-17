from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
  model = CustomUser
  fieldsets = UserAdmin.fieldsets + (
    ('Información adicional', {
      'fields': ('fecha_nacimiento', 'lugar_nacimiento', 'direccion', 'telefono')
    }),
  )
  add_fieldsets = UserAdmin.add_fieldsets + (
    ('Información adicional', {
      'fields': ('fecha_nacimiento', 'lugar_nacimiento', 'direccion', 'telefono')
    }),
  )
  list_display = ('username', 'email', 'fecha_nacimiento', 'is_staff', 'is_active')
  search_fields = ('username', 'email', 'telefono')


# Registrar el modelo en AdminPanel.
admin.site.register(CustomUser, CustomUserAdmin)