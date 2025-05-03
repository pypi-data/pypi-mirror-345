from django.urls import reverse
from pretix.base.models import Event
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin

from .forms import PublicRegistrationsSettingsForm


class PublicRegistrationsSettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    permission = "can_change_settings"
    form_class = PublicRegistrationsSettingsForm
    template_name = "pretix_public_registrations/settings.html"

    def get_success_url(self, **kwargs):
        return reverse(
            "plugins:pretix_public_registrations:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )
