from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminRole
from .models import Team
from .serializers import TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.prefetch_related('members').select_related('evaluator').all().order_by('id')
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['evaluator']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminRole()]

    def get_queryset(self):
        user = self.request.user
        base = super().get_queryset()
        if user.role == User.Roles.ADMIN:
            return base
        if user.role == User.Roles.EVALUATOR:
            return base.filter(evaluator=user)
        return base.filter(members=user)

    def perform_create(self, serializer):
        if self.request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only admin can create teams.')
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only admin can update teams.')
        serializer.save()
