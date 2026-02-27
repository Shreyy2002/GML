from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        TEAM_MEMBER = 'TEAM_MEMBER', 'Team Member'
        EVALUATOR = 'EVALUATOR', 'Evaluator / Manager'
        ADMIN = 'ADMIN', 'Leadership / Admin'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.TEAM_MEMBER, db_index=True)

    class Meta:
        indexes = [models.Index(fields=['role', 'is_active'])]

    def __str__(self):
        return f'{self.username} ({self.role})'
