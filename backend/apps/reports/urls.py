from django.urls import path
from .views import CompanyReportView, IndividualReportView, TeamReportView

urlpatterns = [
    path('individual/', IndividualReportView.as_view(), name='report-individual'),
    path('team/', TeamReportView.as_view(), name='report-team'),
    path('company/', CompanyReportView.as_view(), name='report-company'),
]
