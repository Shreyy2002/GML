from rest_framework.routers import DefaultRouter
from .views import TeamViewSet

router = DefaultRouter()
router.register('', TeamViewSet, basename='teams')
urlpatterns = router.urls
