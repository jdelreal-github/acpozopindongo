from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# Validadores

def dni_validator(nif):
    tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
    numeros = "1234567890"
    if (len(nif) == 9):
        letraControl = nif[8].upper()
        dni = nif[:8]
        try:
          int(dni)
        except ValueError:
            raise ValidationError(_('DNI Invalido. Introduce 8 '
                                    'numeros y una letra'))
        if ( len(dni) == len( [n for n in dni if n in numeros] ) ):
            if tabla[int(dni) % 23] != letraControl:
                raise ValidationError(_('DNI Invalido'))
    else:
        raise ValidationError(_('DNI Invalido. Introduce '
                                '8 numeros y una letra'))


def codigo_postal_validator(codigo):
    try:
        codigo_int = int(codigo)
    except ValueError:
        raise ValidationError(_('Codigo Postal Invalido.'))

    if (len(codigo) != 5 or codigo_int < 1000 or codigo_int > 52999):
        raise ValidationError(_('Codigo Postal Invalido.'))


def telefono_validator(tlf):

    try:
        tlf_int = int(tlf)
    except ValueError:
        raise ValidationError(_('Teléfono Invalido.'))

    if (len(tlf) != 9):
        raise ValidationError(_('Teléfono Invalido.'))


# Custom User

class CustomUser(AbstractUser):
    # Override AbstractUser atributes
    #
    first_name = models.CharField(_('first name'), max_length=30, blank=False, null=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False, null=False)

    email = models.EmailField(_('email address'), blank=False, null=False)

    # End Override AbstractUser atributes
    #
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento',
                                        null=False,
                                        blank=False,
                                        default=timezone.now)

    direccion = models.CharField(verbose_name='Dirección',
                                 max_length=100,
                                 null=True,
                                 blank=True)

    ciudad = models.CharField(verbose_name='Ciudad',
                              max_length=60,
                              null=True,
                              blank=True)

    provincia = models.CharField(verbose_name='Provincia',
                                 max_length=30,
                                 null=True,
                                 blank=True)

    pais = models.CharField(verbose_name='País',
                            max_length=50,
                            null=True,
                            blank=True)

    codigo_postal = models.CharField(verbose_name='Código Postal',
                                     max_length=5,
                                     validators=[codigo_postal_validator],
                                     null=True,
                                     blank=True)

    telefono_fijo = models.CharField(verbose_name='Teléfono Fijo',
                                     max_length=9,
                                     validators=[telefono_validator],
                                     null=False,
                                     blank=False)

    telefono_movil = models.CharField(verbose_name='Teléfono Movil',
                                      max_length=9,
                                      validators=[telefono_validator],
                                      null=False,
                                      blank=False)

    pagado = models.BooleanField(verbose_name='Tasa Pagada', default=False)

    dni = models.CharField(verbose_name='DNI',
                           max_length=9,
                           validators=[dni_validator],
                           null=True,
                           blank=True)

    numero_socio = models.IntegerField(verbose_name='Número de Socio',
                                       default=0)

    profesion = models.CharField(verbose_name='Profesión',
                                 max_length=100,
                                 null=True,
                                 blank=True)
