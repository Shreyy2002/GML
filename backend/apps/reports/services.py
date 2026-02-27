import csv
from io import BytesIO, StringIO
from django.db.models import Avg, Count
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.goals.models import Goal


def apply_period(queryset, month=None, quarter=None):
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


def to_csv(rows, headers):
    sio = StringIO()
    writer = csv.DictWriter(sio, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return sio.getvalue()


def to_pdf(title, lines):
    bio = BytesIO()
    pdf = canvas.Canvas(bio, pagesize=A4)
    y = 800
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, title)
    y -= 30
    pdf.setFont('Helvetica', 10)
    for line in lines:
        pdf.drawString(40, y, str(line)[:120])
        y -= 16
        if y < 40:
            pdf.showPage()
            y = 800
            pdf.setFont('Helvetica', 10)
    pdf.save()
    bio.seek(0)
    return bio


def individual_report_data(user, month=None, quarter=None):
    goals = apply_period(Goal.objects.filter(owner=user).select_related('owner').order_by('due_date'), month, quarter)
    rows = []
    for g in goals:
        rows.append(
            {
                'goal_id': g.id,
                'title': g.title,
                'status': g.status,
                'completion_percentage': g.completion_percentage,
                'final_score': g.final_score or '',
                'feedback_summary': (
                    (getattr(g, 'member_feedback', None).self_reflection[:50] if hasattr(g, 'member_feedback') else '')
                    + ' | '
                    + (getattr(g, 'evaluator_feedback', None).comment[:50] if hasattr(g, 'evaluator_feedback') else '')
                ),
            }
        )
    return rows


def team_report_data(team_id, month=None, quarter=None):
    goals = apply_period(Goal.objects.filter(team_id=team_id), month, quarter)
    stats = goals.aggregate(total=Count('id'), avg_score=Avg('final_score'), completion_rate=Avg('completion_percentage'))
    top = (
        goals.filter(status=Goal.Status.SCORED)
        .values('owner__username')
        .annotate(avg_score=Avg('final_score'))
        .order_by('-avg_score')[:3]
    )
    bottom = (
        goals.filter(status=Goal.Status.SCORED)
        .values('owner__username')
        .annotate(avg_score=Avg('final_score'))
        .order_by('avg_score')[:3]
    )
    rows = [
        {
            'metric': 'total_goals',
            'value': stats['total'] or 0,
        },
        {
            'metric': 'avg_score',
            'value': round(stats['avg_score'] or 0, 2),
        },
        {
            'metric': 'completion_rate',
            'value': round(stats['completion_rate'] or 0, 2),
        },
        {
            'metric': 'top_performers',
            'value': '; '.join([f"{i['owner__username']}({round(i['avg_score'] or 0,2)})" for i in top]),
        },
        {
            'metric': 'bottom_performers',
            'value': '; '.join([f"{i['owner__username']}({round(i['avg_score'] or 0,2)})" for i in bottom]),
        },
    ]
    return rows


def company_report_data(month=None, quarter=None):
    goals = apply_period(Goal.objects.all(), month, quarter)
    distribution = goals.values('evaluator_feedback__final_rating').annotate(count=Count('id')).order_by('evaluator_feedback__final_rating')
    team_compare = goals.values('team__name').annotate(avg_score=Avg('final_score'), completion_rate=Avg('completion_percentage')).order_by('-avg_score')
    trend = goals.values('created_at__year', 'created_at__month').annotate(avg_score=Avg('final_score')).order_by('created_at__year', 'created_at__month')

    rows = []
    for item in distribution:
        rows.append({'section': 'score_distribution', 'key': item['evaluator_feedback__final_rating'] or 'N/A', 'value': item['count']})
    for item in team_compare:
        rows.append({'section': 'team_comparison', 'key': item['team__name'] or 'No Team', 'value': round(item['avg_score'] or 0, 2)})
    for item in trend:
        rows.append({'section': 'trend', 'key': f"{item['created_at__year']}-{item['created_at__month']}", 'value': round(item['avg_score'] or 0, 2)})
    return rows
