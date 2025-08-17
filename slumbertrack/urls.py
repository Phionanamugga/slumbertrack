from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from sleep import views as sleep_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("sleep.api_urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("signup/", sleep_views.signup, name="signup"),
    path("", sleep_views.dashboard, name="dashboard"),
    path("sessions/", sleep_views.session_list, name="session_list"),
    path("sessions/new/", sleep_views.session_create, name="session_create"),
    path("sessions/<int:pk>/edit/", sleep_views.session_edit, name="session_edit"),
    path("goals/", sleep_views.goal_view, name="goal_view"),
    path("import/", sleep_views.import_csv, name="import_csv"),
    path("export/", sleep_views.export_csv, name="export_csv"),
]
