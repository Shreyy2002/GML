from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Team

User = get_user_model()


class TeamSerializer(serializers.ModelSerializer):
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='TEAM_MEMBER'), many=True, source='members', write_only=True, required=False
    )
    members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'evaluator', 'members', 'member_ids', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_members(self, obj):
        return [{'id': m.id, 'username': m.username, 'email': m.email} for m in obj.members.all()]

    def validate_evaluator(self, value):
        if value and value.role not in ('EVALUATOR', 'ADMIN'):
            raise serializers.ValidationError('Evaluator must have EVALUATOR or ADMIN role.')
        return value
