from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import CustomUser, DailyTaskClass
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from datetime import datetime
from usuarios import SENDER


IMPORTANT_DATES = {'christmas': {'month': 12,
                                 'day': 24,
                                 'subject': 'Feliz Navidad'},
                   'new_year': {'month': 1,
                                'day': 1,
                                'subject': 'Feliz Año Nuevo'},
                   }


def verify_if_important_date():
    '''
    Verify if toady is an important date stored in IMPORTANT_DATES
    dictionary
    :return: string with important date. Keys in IMPORTANT_DATES dictionary
    '''
    now = datetime.now()
    for important_date, date in IMPORTANT_DATES.items():
        if now.month == date['month'] and now.day == date['day']:
            return important_date
    return ''


def get_users_birthday(users):
    '''
    Verify if it is a birthday of some user.
    :param users: List of CustomerUser objects
    :return: list of users celebrating the birthday
    '''
    now = datetime.now()
    users_list = list()
    for user in users:
        if user.fecha_nacimiento.strftime("%m-%d") == now.strftime("%m-%d"):
            users_list.append(user)
    return users_list


def remove_paid(users):
    '''
    Remove in all users the field pagado.
    :param users:  List of CustomerUser objects
    '''
    for user in users:
        user.pagado = False
        user.save()


def send_email_birthday(users):
    '''
    Send an email for each user celebrating the birthday
    :param users: List of users celebrating the birthday
                  (CustomerUser objects)
    '''
    now = datetime.now()
    for user in users:
        body = render_to_string(
            'birthday.html', {
                'name': SENDER,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date': now.strftime("%d/%m/%Y")
            },
        )
        email_message = EmailMessage(
            subject='Feliz Cumpleaños',
            body=body,
            from_email=SENDER,
            to=[user.email],
            )
        email_message.content_subtype = 'html'
        email_message.send()


def send_email_important_day(important_date, users):
    '''
    Send an email for all users due to an important date
    :param important_date: String with the important date.
                           Keys of the dictionary IMPORTANT_DATES
    :param users: List of all users (CustomerUser objects)
    '''
    if important_date not in IMPORTANT_DATES:
        return

    emails = list()

    for user in users:
        emails.append(user.email)

    body = render_to_string('%s.html' % important_date, {},)

    email_message = EmailMessage(
        subject=IMPORTANT_DATES[important_date]['subject'],
        body=body,
        from_email=SENDER,
        to=emails,
        )
    email_message.content_subtype = 'html'
    email_message.send()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('url', 'username', 'email', 'password', 'numero_socio',
                  'first_name', 'last_name', 'direccion',
                  'ciudad', 'codigo_postal',
                  'provincia', 'telefono_fijo', 'telefono_movil',
                  'dni', 'profesion', 'fecha_nacimiento', 'pagado',
                  'is_staff')

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class DailyTasksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DailyTaskClass
        fields = ()

    def create(self, validated_data):
        # Get all Users
        users = CustomUser.objects.all()

        # Verify if today is an important date
        important_date = verify_if_important_date()

        # In the case of new_year remove field "pagado" in all users
        if important_date == 'new_year':
            remove_paid(users)

        # In the case of today is an important date, send an email
        # to all users
        send_email_important_day(important_date, users)

        # Get the list of users celebrating the birthday.
        # If there is one o more, send an email to all of them
        users_birthday = get_users_birthday(users)
        if users_birthday:
            send_email_birthday(users_birthday)
        return users
