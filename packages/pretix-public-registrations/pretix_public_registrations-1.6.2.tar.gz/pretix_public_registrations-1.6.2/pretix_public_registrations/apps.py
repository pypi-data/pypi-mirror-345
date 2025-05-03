from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    name = "pretix_public_registrations"
    verbose_name = "Pretix public registrations"

    class PretixPluginMeta:
        name = gettext_lazy("Pretix public registrations")
        author = "Felix Schäfer, Dominik Weitz"
        description = gettext_lazy(
            "This plugin will give the option to attendees of an event to mark their registration as public. "
            "Public registrations will be shown along their answers to questions marked as public by the organizers on "
            "a world-readable page."
        )
        visible = True
        version = __version__
        category = "FEATURE"
        compatibility = "pretix>=2.7.0"
        settings_links = [
            (
                gettext_lazy("Public registrations"),
                "plugins:pretix_public_registrations:settings",
                {},
            ),
        ]

    def ready(self):
        from . import signals  # NOQA
