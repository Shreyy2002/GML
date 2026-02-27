from decimal import Decimal
from rest_framework.exceptions import ValidationError
from .models import Goal


EDITABLE_STATES = {Goal.Status.DRAFT, Goal.Status.REJECTED}


def ensure_editable(goal: Goal):
    if goal.status not in EDITABLE_STATES:
        raise ValidationError('Only DRAFT and REJECTED goals can be edited.')


def transition(goal: Goal, to_status: str):
    allowed = {
        Goal.Status.DRAFT: {Goal.Status.PENDING},
        Goal.Status.PENDING: {Goal.Status.ACTIVE, Goal.Status.REJECTED},
        Goal.Status.ACTIVE: {Goal.Status.COMPLETED},
        Goal.Status.COMPLETED: {Goal.Status.SCORED},
        Goal.Status.REJECTED: {Goal.Status.PENDING},
        Goal.Status.SCORED: set(),
    }
    if to_status not in allowed.get(goal.status, set()):
        raise ValidationError(f'Invalid transition from {goal.status} to {to_status}.')
    goal.status = to_status


def calculate_numeric_score(feedback) -> Decimal:
    values = [feedback.quality, feedback.ownership, feedback.communication, feedback.timeliness, feedback.initiative]
    average = sum(values) / len(values)
    return Decimal(str(round((average / 5) * 100, 2)))
