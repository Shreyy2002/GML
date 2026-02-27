from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.teams.models import Team


class Goal(models.Model):
    class Level(models.TextChoices):
        COMPANY = 'COMPANY', 'Company'
        TEAM = 'TEAM', 'Team'
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING = 'PENDING', 'Pending'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        SCORED = 'SCORED', 'Scored'
        REJECTED = 'REJECTED', 'Rejected'

    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=Level.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_goals')
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='goals_to_evaluate',
    )
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='goals')
    parent_goal = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='child_goals')

    due_date = models.DateField(db_index=True)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    category = models.CharField(max_length=120, db_index=True)
    completion_percentage = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    final_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'level']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['team', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]

    def __str__(self):
        return f'{self.title} [{self.status}]'

    @property
    def is_locked(self):
        return self.status == Goal.Status.SCORED

    @property
    def at_risk(self):
        today = timezone.now().date()
        total_days = (self.due_date - self.created_at.date()).days
        if total_days <= 0:
            return False
        elapsed_days = (today - self.created_at.date()).days
        elapsed_ratio = max(0, min(elapsed_days / total_days, 1))
        return elapsed_ratio > 0.7 and self.completion_percentage < 50


class SubTask(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='sub_tasks')
    title = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['goal', 'is_done'])]


class Approval(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='approvals')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goal_approvals')
    approved = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['goal', 'created_at']), models.Index(fields=['reviewer'])]


class MemberFeedback(models.Model):
    goal = models.OneToOneField(Goal, on_delete=models.CASCADE, related_name='member_feedback')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member_feedbacks')
    self_reflection = models.TextField()
    delivered = models.TextField()
    improvement = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EvaluatorFeedback(models.Model):
    class FinalRating(models.TextChoices):
        BELOW = 'BELOW', 'Below Expectations'
        MEETS = 'MEETS', 'Meets Expectations'
        ABOVE = 'ABOVE', 'Above Expectations'

    goal = models.OneToOneField(Goal, on_delete=models.CASCADE, related_name='evaluator_feedback')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluator_feedbacks')

    quality = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    ownership = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    timeliness = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    initiative = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    comment = models.TextField()
    final_rating = models.CharField(max_length=10, choices=FinalRating.choices)
    numeric_score = models.DecimalField(max_digits=6, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
