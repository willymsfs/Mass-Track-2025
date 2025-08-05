from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'intention-types', views.IntentionTypeViewSet)
router.register(r'intention-sources', views.IntentionSourceViewSet)
router.register(r'mass-intentions', views.MassIntentionViewSet, basename='massintention')
router.register(r'personal-intentions', views.PersonalMassIntentionViewSet, basename='personalmassintention')
router.register(r'fixed-date-intentions', views.FixedDateMassIntentionViewSet, basename='fixeddatemassintention')
router.register(r'bulk-intentions', views.BulkMassIntentionViewSet, basename='bulkmassintention')
router.register(r'mass-celebrations', views.MassCelebrationViewSet, basename='masscelebration')
router.register(r'daily-status', views.DailyStatusViewSet, basename='dailystatus')

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/auth/register/", views.register, name="register"),
    path("api/auth/login/", views.login, name="login"),
    path("api/dashboard/", views.dashboard, name="dashboard"),
    path("api/celebrate-mass/", views.celebrate_mass, name="celebrate_mass"),
    path("api/toggle-bulk-mass-pause/", views.toggle_bulk_mass_pause, name="toggle_bulk_mass_pause"),
    path("api/import-excel/", views.import_excel_data, name="import_excel_data"),
]