from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model


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
