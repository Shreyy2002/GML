from django.conf import settings
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='evaluated_teams',
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['name']), models.Index(fields=['evaluator'])]

    def __str__(self):
        return self.name
