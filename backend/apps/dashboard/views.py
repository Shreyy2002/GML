from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.goals.models import Goal


def period_filter(queryset, month=None, quarter=None):
    if month:
        year, m = map(int, month.split('-'))
        return queryset.filter(created_at__year=year, created_at__month=m)
    if quarter:
        year, q = quarter.split('-Q')
        year = int(year)
        q = int(q)
        start_month = (q - 1) * 3 + 1
        end_month = start_month + 2
        return queryset.filter(created_at__year=year, created_at__month__gte=start_month, created_at__month__lte=end_month)
    return queryset


class DashboardView(APIView):
    def get(self, request):
        user = request.user
        scope = request.query_params.get('scope', 'individual')
        month = request.query_params.get('month')
        quarter = request.query_params.get('quarter')

        goals = Goal.objects.all()
        goals = period_filter(goals, month, quarter)

        if scope == 'individual':
            goals = goals.filter(owner=user)
        elif scope == 'team':
            if user.role == User.Roles.TEAM_MEMBER:
                team_ids = user.teams.values_list('id', flat=True)
                goals = goals.filter(team_id__in=team_ids)
            elif user.role == User.Roles.EVALUATOR:
                goals = goals.filter(Q(team__evaluator=user) | Q(evaluator=user))
        elif scope == 'company':
            if user.role != User.Roles.ADMIN:
                return Response({'detail': 'Company dashboard is admin-only.'}, status=403)

        total = goals.count() or 1
        status_counts = goals.values('status').annotate(count=Count('id'))
        mapped = {item['status']: item['count'] for item in status_counts}

        overview = {
            'total_goals': total if total != 1 or goals.exists() else 0,
            'active_pct': round((mapped.get(Goal.Status.ACTIVE, 0) / total) * 100, 2),
            'completed_pct': round((mapped.get(Goal.Status.COMPLETED, 0) / total) * 100, 2),
            'pending_pct': round((mapped.get(Goal.Status.PENDING, 0) / total) * 100, 2),
            'rejected_pct': round((mapped.get(Goal.Status.REJECTED, 0) / total) * 100, 2),
        }

        list_data = [
            {
                'id': g.id,
                'title': g.title,
                'status': g.status,
                'completion_percentage': g.completion_percentage,
                'due_date': g.due_date,
                'at_risk': g.at_risk,
            }
            for g in goals.order_by('due_date')[:100]
        ]

        perf_member = (
            goals.filter(status=Goal.Status.SCORED)
            .values('owner__id', 'owner__username')
            .annotate(avg_score=Avg('final_score'))
            .order_by('-avg_score')
        )
        perf_team = (
            goals.filter(status=Goal.Status.SCORED)
            .values('team__id', 'team__name')
            .annotate(avg_score=Avg('final_score'))
            .order_by('-avg_score')
        )

        return Response(
            {
                'overview': overview,
                'status_breakdown': mapped,
                'goals': list(list_data),
                'performance_snapshot': {
                    'avg_score_per_member': list(perf_member),
                    'avg_score_per_team': list(perf_team),
                },
                'generated_at': timezone.now(),
            }
        )
