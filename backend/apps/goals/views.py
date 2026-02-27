from django.db.models import Avg, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.models import User
from .models import Approval, EvaluatorFeedback, Goal, MemberFeedback
from .permissions import CanModifyGoal, IsGoalVisibleToUser
from .serializers import EvaluatorFeedbackSerializer, GoalSerializer, MemberFeedbackSerializer
from .services import calculate_numeric_score, transition


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.select_related('owner', 'evaluator', 'team', 'parent_goal').prefetch_related('sub_tasks').all()
    serializer_class = GoalSerializer
    permission_classes = [CanModifyGoal]
    filterset_fields = ['status', 'level', 'team', 'owner', 'evaluator', 'category']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        base = super().get_queryset().order_by('-created_at')
        if user.role == User.Roles.ADMIN:
            return base
        if user.role == User.Roles.EVALUATOR:
            return base.filter(Q(evaluator=user) | Q(team__evaluator=user)).distinct()
        return base.filter(owner=user)

    def get_object(self):
        obj = super().get_object()
        if not IsGoalVisibleToUser().has_object_permission(self.request, self, obj):
            raise PermissionDenied('Not allowed to access this goal.')
        return obj

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Roles.TEAM_MEMBER:
            serializer.save(owner=user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        goal = self.get_object()
        if goal.owner_id != request.user.id and request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only owner or admin can submit for approval.')
        transition(goal, Goal.Status.PENDING)
        goal.save(update_fields=['status', 'updated_at'])
        return Response({'status': goal.status})

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        goal = self.get_object()
        if request.user.role not in (User.Roles.EVALUATOR, User.Roles.ADMIN):
            raise PermissionDenied('Only evaluator/admin can approve.')
        if goal.evaluator_id and goal.evaluator_id != request.user.id and request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only assigned evaluator can approve this goal.')

        transition(goal, Goal.Status.ACTIVE)
        goal.save(update_fields=['status', 'updated_at'])
        Approval.objects.create(goal=goal, reviewer=request.user, approved=True, comment=request.data.get('comment', ''))
        return Response({'status': goal.status})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        goal = self.get_object()
        comment = request.data.get('comment', '').strip()
        if not comment:
            raise ValidationError({'comment': 'Rejection comment is mandatory.'})
        if request.user.role not in (User.Roles.EVALUATOR, User.Roles.ADMIN):
            raise PermissionDenied('Only evaluator/admin can reject.')
        if goal.evaluator_id and goal.evaluator_id != request.user.id and request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only assigned evaluator can reject this goal.')

        transition(goal, Goal.Status.REJECTED)
        goal.save(update_fields=['status', 'updated_at'])
        Approval.objects.create(goal=goal, reviewer=request.user, approved=False, comment=comment)
        return Response({'status': goal.status})

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        goal = self.get_object()
        if goal.owner_id != request.user.id and request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only owner/admin can mark completion.')
        completion = request.data.get('completion_percentage')
        if completion is not None:
            goal.completion_percentage = int(completion)
        transition(goal, Goal.Status.COMPLETED)
        goal.save(update_fields=['completion_percentage', 'status', 'updated_at'])
        return Response({'status': goal.status, 'completion_percentage': goal.completion_percentage})

    @action(detail=True, methods=['post'], url_path='progress')
    def update_progress(self, request, pk=None):
        goal = self.get_object()
        if goal.owner_id != request.user.id and request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only owner/admin can update progress.')
        if goal.status not in (Goal.Status.ACTIVE, Goal.Status.COMPLETED):
            raise ValidationError('Progress can only be updated in ACTIVE or COMPLETED state.')
        completion = int(request.data.get('completion_percentage', goal.completion_percentage))
        if completion < 0 or completion > 100:
            raise ValidationError('completion_percentage must be between 0 and 100')
        goal.completion_percentage = completion
        goal.save(update_fields=['completion_percentage', 'updated_at'])
        return Response({'completion_percentage': goal.completion_percentage})

    @action(detail=True, methods=['post'], url_path='member-feedback')
    def member_feedback(self, request, pk=None):
        goal = self.get_object()
        if goal.owner_id != request.user.id and request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only owner/admin can submit member feedback.')

        payload = {**request.data, 'goal': goal.id, 'member': goal.owner_id}
        instance = getattr(goal, 'member_feedback', None)
        serializer = MemberFeedbackSerializer(instance=instance, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='evaluator-feedback')
    def evaluator_feedback(self, request, pk=None):
        goal = self.get_object()
        if request.user.role not in (User.Roles.EVALUATOR, User.Roles.ADMIN):
            raise PermissionDenied('Only evaluator/admin can submit evaluator feedback.')
        if goal.evaluator_id and goal.evaluator_id != request.user.id and request.user.role != User.Roles.ADMIN:
            raise PermissionDenied('Only assigned evaluator can submit feedback.')

        payload = {**request.data, 'goal': goal.id, 'evaluator': request.user.id}
        instance = getattr(goal, 'evaluator_feedback', None)
        serializer = EvaluatorFeedbackSerializer(instance=instance, data=payload)
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()
        feedback.numeric_score = calculate_numeric_score(feedback)
        feedback.save(update_fields=['numeric_score', 'updated_at'])
        return Response(EvaluatorFeedbackSerializer(feedback).data)

    @action(detail=True, methods=['post'], url_path='score')
    def score(self, request, pk=None):
        goal = self.get_object()
        if request.user.role not in (User.Roles.EVALUATOR, User.Roles.ADMIN):
            raise PermissionDenied('Only evaluator/admin can score.')
        if goal.status != Goal.Status.COMPLETED:
            raise ValidationError('Scoring is only allowed from COMPLETED state.')
        if not hasattr(goal, 'member_feedback') or not hasattr(goal, 'evaluator_feedback'):
            raise ValidationError('Both member and evaluator feedback are mandatory before scoring.')

        transition(goal, Goal.Status.SCORED)
        goal.final_score = goal.evaluator_feedback.numeric_score
        goal.save(update_fields=['status', 'final_score', 'updated_at'])
        return Response({'status': goal.status, 'final_score': goal.final_score})

    @action(detail=False, methods=['get'], url_path='performance')
    def performance(self, request):
        member_avg = (
            Goal.objects.filter(status=Goal.Status.SCORED)
            .values('owner__id', 'owner__username')
            .annotate(avg_score=Avg('final_score'))
            .order_by('-avg_score')
        )
        team_avg = (
            Goal.objects.filter(status=Goal.Status.SCORED)
            .values('team__id', 'team__name')
            .annotate(avg_score=Avg('final_score'))
            .order_by('-avg_score')
        )
        return Response({'member_avg': list(member_avg), 'team_avg': list(team_avg)})
