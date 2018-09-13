from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import gettext as _, gettext_lazy
from django.template.response import TemplateResponse
from django.contrib.admin import helpers
from django.core.validators import EmailValidator
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.models import Group

from .models import CustomUser, CustomGroup
from .forms import EmailForm
from usuarios import SENDER


def verify_emails(emails):
    '''
    Verify if list of emails are valid.
    :param emails:
    :return: Exception if invalid
    '''
    for email in emails:
        val = EmailValidator()
        val(email)


def _sendmail(para, asunto, mensaje):
    email_message = EmailMessage(
        subject=asunto,
        body=mensaje,
        from_email=SENDER,
        to=para,
        )
    email_message.content_subtype = 'text'
    email_message.send()


def sendmail(form, queryset):
    para = form.cleaned_data['para']
    asunto = form.cleaned_data['asunto']
    mensaje = form.cleaned_data['mensaje']
    personalizado = form.cleaned_data['personalizado']

    email_list = para.split(',')
    # Remove whitespaces
    email_list = [x.strip(' ') for x in email_list]
    if personalizado:
        for user in queryset:
            header = 'Hola %s %s.\n\n' % (user.first_name, user.last_name)
            mensaje1 = header + mensaje
            _sendmail([user.email], asunto, mensaje1)
    else:
            _sendmail(email_list, asunto, mensaje)


def sendmail_group(form, queryset):
    para = form.cleaned_data['para']
    asunto = form.cleaned_data['asunto']
    mensaje = form.cleaned_data['mensaje']
    personalizado = form.cleaned_data['personalizado']

    email_list = para.split(',')
    # Remove whitespaces
    email_list = [x.strip(' ') for x in email_list]
    if personalizado:
        for query in queryset:
            for user in query:
                header = 'Hola %s %s.\n\n' % (user.first_name, user.last_name)
                mensaje1 = header + mensaje
                _sendmail([user.email], asunto, mensaje1)
    else:
            _sendmail(email_list, asunto, mensaje)


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

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'pagado', 'groups')
    actions = ['send_email', 'paid', 'not_paid']

    def paid(self, request, queryset):
        try:
            for user in queryset:
                if user.pagado is False:
                    user.pagado = True
                    user.save()
                    self.log_addition(request, user, 'Modificado pagado.')
            self.message_user(request,
                              _('Cambio a PAGADO Correcto'),
                              messages.SUCCESS)

        except Exception as ex:
            self.message_user(request,
                              _('Cambio a PAGADO Erroneo'),
                              messages.ERROR)

    paid.short_description = \
        gettext_lazy("Pagado %(verbose_name_plural)s")

    def not_paid(self, request, queryset):
        try:
            for user in queryset:
                if user.pagado is True:
                    user.pagado = False
                    user.save()
                    self.log_addition(request, user, 'Modificado pagado.')

            self.message_user(request,
                              _('Cambio a NO PAGADO Correcto'),
                              messages.SUCCESS)

        except Exception as ex:
            self.message_user(request,
                              _('Cambio a PAGADO Erroneo'),
                              messages.ERROR)

    not_paid.short_description = \
        gettext_lazy("No pagado %(verbose_name_plural)s")

    def send_email(self, request, queryset):
        """
        Default action which send a email to the selected objects.

        This action first displays a confirmation page which shows
        an email form.

        Next, Sends the email and redirects back to the change list.
        """
        opts = self.model._meta
        title = _('Correo Electronico')

        emails = [user.email for user in queryset]
        str_emails = ', '.join([email for email in emails])

        if request.POST.get('post'):
            # Processing the submit
            form = EmailForm(request.POST)
            if form.is_valid():
                para = form.cleaned_data['para']
                try:
                    email_list = para.split(',')
                    # Remove whitespaces
                    email_list = [x.strip(' ') for x in email_list]
                    verify_emails(email_list)
                    try:
                        sendmail(form, queryset)
                        self.message_user(request,
                                          _('Enviado correo correctamente'),
                                          messages.SUCCESS)

                    except Exception as ex:
                        self.message_user(request,
                                          _('Error Enviando correo'),
                                          messages.ERROR)
                    # Return None to display the change list page again.
                    return None
                except Exception as ex:
                    # if not valid, write a user message and
                    # reload the form.
                    self.message_user(request, _(ex.message), messages.ERROR)
                    data = {'para': para,
                            'asunto': form.cleaned_data['asunto'],
                            'mensaje': form.cleaned_data['mensaje'],
                            'personalizado':
                                form.cleaned_data['personalizado']}
                    form = EmailForm(data)
        else:
            data = {'para': str_emails}
            form = EmailForm(data)

        context = {
            **self.admin_site.each_context(request),
            'title': title,
            'queryset': queryset,
            'opts': opts,
            'emails': emails,
            'form': form,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,

        }

        request.current_app = self.admin_site.name

        # Display the confirmation page
        return TemplateResponse(request, ["admin/send_email.html"], context)

    send_email.short_description = \
        gettext_lazy("Enviar e-mail %(verbose_name_plural)s")

admin.site.register(CustomUser, CustomUserAdmin)


class CustomGroupAdmin(GroupAdmin):
    model = CustomGroup

    actions = ['send_email']

    def send_email(self, request, queryset):
        """
        Default action which send a email to the selected objects.

        This action first displays a confirmation page which shows
        an email form.

        Next, Sends the email and redirects back to the change list.
        """
        opts = self.model._meta
        title = _('Correo Electronico')

        groups = [group for group in queryset]

        users_queries = list()
        all_users = CustomUser.objects.all()
        for group in groups:
            user_query = all_users.filter(groups__name=group.name)
            users_queries.append(user_query)

        emails = list()
        for user_query in users_queries:
            for user in user_query:
                emails.append(user.email)

        str_emails = ', '.join([email for email in emails])

        if request.POST.get('post'):
            # Processing the submit
            form = EmailForm(request.POST)
            if form.is_valid():
                para = form.cleaned_data['para']
                try:
                    email_list = para.split(',')
                    # Remove whitespaces
                    email_list = [x.strip(' ') for x in email_list]
                    verify_emails(email_list)
                    try:
                        sendmail_group(form, users_queries)
                        self.message_user(request,
                                          _('Enviado correo correctamente'),
                                          messages.SUCCESS)

                    except Exception as ex:
                        self.message_user(request,
                                          _('Error Enviando correo'),
                                          messages.ERROR)
                    # Return None to display the change list page again.
                    return None
                except Exception as ex:
                    # if not valid, write a user message and
                    # reload the form.
                    self.message_user(request, _(ex.message), messages.ERROR)
                    data = {'para': para,
                            'asunto': form.cleaned_data['asunto'],
                            'mensaje': form.cleaned_data['mensaje'],
                            'personalizado':
                                form.cleaned_data['personalizado']}
                    form = EmailForm(data)
        else:
            data = {'para': str_emails}
            form = EmailForm(data)

        context = {
            **self.admin_site.each_context(request),
            'title': title,
            'queryset': queryset,
            'opts': opts,
            'emails': emails,
            'form': form,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,

        }

        request.current_app = self.admin_site.name

        # Display the confirmation page
        return TemplateResponse(request, ["admin/send_email.html"], context)

    send_email.short_description = \
        gettext_lazy("Enviar e-mail %(verbose_name_plural)s seleccionados")


admin.site.unregister(Group)
admin.site.register(CustomGroup, CustomGroupAdmin)
