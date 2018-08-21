from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'email',
                       'numero_socio')
        }),
        ('Datos Personales', {
            'fields': ('first_name', 'last_name', 'direccion',
                       'ciudad', 'codigo_postal',
                       'provincia', 'telefono_fijo', 'telefono_movil',
                       'dni', 'profesion', 'fecha_nacimiento', 'pagado'),
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
