from django import forms
from django.utils.translation import gettext_lazy as _
from pretix.base.forms import SettingsForm


class PublicRegistrationsSettingsForm(SettingsForm):
    public_registrations_items = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "scrolling-multiple-choice"}
        ),
        label=_("Display public registrations for"),
        required=True,
        choices=[],
    )
    public_registrations_questions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "scrolling-multiple-choice"}
        ),
        label=_("Publicly display answers for"),
        required=True,
        choices=[],
    )
    public_registrations_show_attendee_name = forms.BooleanField(
        label=_("Display attendee name"),
        required=False,
    )
    public_registrations_show_item_name = forms.BooleanField(
        label=_("Display product name"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["public_registrations_items"].choices = [
            (i.pk, i.name) for i in self.obj.items.all()
        ]
        self.fields["public_registrations_questions"].choices = [
            (q.pk, q.question) for q in self.obj.questions.all()
        ]
