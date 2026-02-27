from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/teams/', include('apps.teams.urls')),
    path('api/users/', include('apps.accounts.user_urls')),
    path('api/goals/', include('apps.goals.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/reports/', include('apps.reports.urls')),
]
