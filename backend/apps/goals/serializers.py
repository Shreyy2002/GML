from rest_framework import serializers

from apps.accounts.models import User
from apps.teams.models import Team
from .models import Approval, EvaluatorFeedback, Goal, MemberFeedback, SubTask
from .services import ensure_editable


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ('id', 'title', 'is_done')
        read_only_fields = ('id',)


class GoalSerializer(serializers.ModelSerializer):
    sub_tasks = SubTaskSerializer(many=True, required=False)
    at_risk = serializers.BooleanField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Goal
        fields = (
            'id',
            'title',
            'description',
            'level',
            'status',
            'owner',
            'evaluator',
            'team',
            'parent_goal',
            'due_date',
            'weightage',
            'category',
            'completion_percentage',
            'final_score',
            'at_risk',
            'is_locked',
            'sub_tasks',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('status', 'final_score', 'created_at', 'updated_at')

    def validate(self, attrs):
        level = attrs.get('level', getattr(self.instance, 'level', None))
        team = attrs.get('team', getattr(self.instance, 'team', None))
        owner = attrs.get('owner', getattr(self.instance, 'owner', None))
        evaluator = attrs.get('evaluator', getattr(self.instance, 'evaluator', None))

        if level == Goal.Level.TEAM and not team:
            raise serializers.ValidationError('TEAM goals must have a team.')
        if level == Goal.Level.INDIVIDUAL and not owner:
            raise serializers.ValidationError('INDIVIDUAL goals must have an owner.')
        if evaluator and evaluator.role not in (User.Roles.EVALUATOR, User.Roles.ADMIN):
            raise serializers.ValidationError('Evaluator must be an evaluator or admin.')
        if team and owner and owner not in team.members.all() and owner.role != User.Roles.ADMIN:
            raise serializers.ValidationError('Owner must belong to the selected team.')
        return attrs

    def create(self, validated_data):
        sub_tasks_data = validated_data.pop('sub_tasks', [])
        goal = Goal.objects.create(**validated_data)
        for item in sub_tasks_data:
            SubTask.objects.create(goal=goal, **item)
        return goal

    def update(self, instance, validated_data):
        ensure_editable(instance)
        sub_tasks_data = validated_data.pop('sub_tasks', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if sub_tasks_data is not None:
            instance.sub_tasks.all().delete()
            for item in sub_tasks_data:
                SubTask.objects.create(goal=instance, **item)
        return instance


class ApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = ('id', 'goal', 'reviewer', 'approved', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')


class MemberFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberFeedback
        fields = ('id', 'goal', 'member', 'self_reflection', 'delivered', 'improvement', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class EvaluatorFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluatorFeedback
        fields = (
            'id',
            'goal',
            'evaluator',
            'quality',
            'ownership',
            'communication',
            'timeliness',
            'initiative',
            'comment',
            'final_rating',
            'numeric_score',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'numeric_score', 'created_at', 'updated_at')
