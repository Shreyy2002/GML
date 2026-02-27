from django.http import FileResponse, HttpResponse
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminRole
from .services import company_report_data, individual_report_data, team_report_data, to_csv, to_pdf


class IndividualReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        quarter = request.query_params.get('quarter')
        fmt = request.query_params.get('format', 'json')
        rows = individual_report_data(request.user, month, quarter)
        if fmt == 'csv':
            csv_data = to_csv(rows, ['goal_id', 'title', 'status', 'completion_percentage', 'final_score', 'feedback_summary'])
            resp = HttpResponse(csv_data, content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename="individual_report.csv"'
            return resp
        if fmt == 'pdf':
            pdf = to_pdf('Individual Report', [str(r) for r in rows])
            return FileResponse(pdf, as_attachment=True, filename='individual_report.pdf')
        return Response(rows)


class TeamReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        quarter = request.query_params.get('quarter')
        team_id = request.query_params.get('team_id')
        fmt = request.query_params.get('format', 'json')
        if not team_id:
            raise ValidationError({'team_id': 'team_id is required'})
        if request.user.role == User.Roles.TEAM_MEMBER and not request.user.teams.filter(id=team_id).exists():
            raise PermissionDenied('Not allowed to access this team report.')
        if request.user.role == User.Roles.EVALUATOR and not request.user.evaluated_teams.filter(id=team_id).exists():
            raise PermissionDenied('Not allowed to access this team report.')
        rows = team_report_data(team_id, month, quarter)
        if fmt == 'csv':
            csv_data = to_csv(rows, ['metric', 'value'])
            resp = HttpResponse(csv_data, content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename="team_report.csv"'
            return resp
        if fmt == 'pdf':
            pdf = to_pdf('Team Report', [str(r) for r in rows])
            return FileResponse(pdf, as_attachment=True, filename='team_report.pdf')
        return Response(rows)


class CompanyReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        month = request.query_params.get('month')
        quarter = request.query_params.get('quarter')
        fmt = request.query_params.get('format', 'json')
        rows = company_report_data(month, quarter)
        if fmt == 'csv':
            csv_data = to_csv(rows, ['section', 'key', 'value'])
            resp = HttpResponse(csv_data, content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename="company_report.csv"'
            return resp
        if fmt == 'pdf':
            pdf = to_pdf('Company Report', [str(r) for r in rows])
            return FileResponse(pdf, as_attachment=True, filename='company_report.pdf')
        return Response(rows)
