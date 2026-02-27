from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.accounts.models import User


class IsGoalVisibleToUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Roles.ADMIN:
            return True
        if user.role == User.Roles.EVALUATOR:
            return obj.evaluator_id == user.id or (obj.team and obj.team.evaluator_id == user.id)
        return obj.owner_id == user.id


class CanModifyGoal(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if user.role == User.Roles.ADMIN:
            return True
        if user.role == User.Roles.EVALUATOR:
            return obj.evaluator_id == user.id
        return obj.owner_id == user.id
