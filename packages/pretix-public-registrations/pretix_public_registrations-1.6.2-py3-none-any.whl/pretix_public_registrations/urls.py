from django.urls import path

from .views import PublicRegistrationsSettingsView

urlpatterns = [
    path(
        "control/event/<str:organizer>/<str:event>/public_registrations/",
        PublicRegistrationsSettingsView.as_view(),
        name="settings",
    )
]
