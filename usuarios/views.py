from django.contrib.auth.models import Group
from rest_framework import viewsets
from .serializer import UserSerializer, GroupSerializer, DailyTasksSerializer
from .models import CustomUser, DailyTaskClass


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CustomUser.objects.all().order_by('username')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class DailyTasksViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = DailyTaskClass.objects.all()
    serializer_class = DailyTasksSerializer
