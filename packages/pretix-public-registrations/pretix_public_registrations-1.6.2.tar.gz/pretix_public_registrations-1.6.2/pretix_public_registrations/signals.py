import hashlib
from django import forms
from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.models import Order, OrderPosition, QuestionAnswer
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import event_copy_data
from pretix.control.signals import nav_event_settings
from pretix.presale.signals import (
    front_page_bottom,
    html_head,
    process_response,
    question_form_fields,
)
from urllib.parse import urlencode

settings_hierarkey.add_default("public_registrations_items", [], list)
settings_hierarkey.add_default("public_registrations_questions", [], list)
settings_hierarkey.add_default("public_registrations_show_attendee_name", False, bool)
settings_hierarkey.add_default("public_registrations_show_item_name", False, bool)


@receiver(html_head, dispatch_uid="public_registrations_html_head")
def add_public_registrations_html_head(sender, request=None, **kwargs):
    url = resolve(request.path_info)
    if "event.index" not in url.url_name:
        return ""
    return sender.cache.get_or_set(
        "public_registrations_html_head",
        get_template("pretix_public_registrations/head.html").render(),
    )


@receiver(question_form_fields, dispatch_uid="public_registration_question")
def add_public_registration_question(sender, position, **kwargs):
    if str(position.item.pk) not in sender.settings.get("public_registrations_items"):
        return {}
    public_questions = sender.questions.filter(
        pk__in=sender.settings.get("public_registrations_questions")
    )
    headers = (
        (
            [_("Product")]
            if sender.settings.get("public_registrations_show_item_name")
            else []
        )
        + (
            [_("Name")]
            if sender.settings.get("public_registrations_show_attendee_name")
            else []
        )
        + [q.question for q in public_questions]
    )
    return {
        "public_registrations_public_registration": forms.BooleanField(
            label=_("Public registration"),
            required=False,
            help_text=_(
                "A gravatar image based on a hash of your e-mail address as well as the answers to "
                "the following questions will be publicly shown: %(qlist)s"
            )
            % {"qlist": ", ".join(str(h) for h in headers)},
        )
    }


@receiver(signal=front_page_bottom, dispatch_uid="public_registrations_table")
def add_public_registrations_table(sender, **kwargs):
    def get_gravatar_url(email, size=40):
        email_encoded = email.lower().encode("utf-8")
        email_hash = hashlib.sha256(email_encoded).hexdigest()
        params = urlencode({"d": "wavatar", "s": str(size), "r": "g"})
        return f"https://gravatar.com/avatar/{email_hash}?{params}"

    if not sender.settings.get("public_registrations_items") and not (
        sender.settings.get("public_registrations_questions")
        and sender.settings.get("public_registrations_show_item_name")
        and sender.settings.get("public_registrations_show_attendee_name")
    ):
        return ""
    public_questions = sender.questions.filter(
        pk__in=sender.settings.get("public_registrations_questions")
    )
    headers = (
        (
            [_("Product")]
            if sender.settings.get("public_registrations_show_item_name")
            else []
        )
        + (
            [_("Name")]
            if sender.settings.get("public_registrations_show_attendee_name")
            else []
        )
        + [q.question for q in public_questions]
    )
    order_positions = (
        OrderPosition.objects.filter(
            order__event=sender,
            item__pk__in=sender.settings.get("public_registrations_items"),
            order__testmode=(sender.testmode),
        )
        .exclude(order__status=Order.STATUS_CANCELED)
        .order_by("order__datetime")
    )
    public_order_positions = [
        op
        for op in order_positions
        if op.meta_info_data.get("question_form_data", {}).get(
            "public_registrations_public_registration"
        )
    ]
    answers = QuestionAnswer.objects.filter(
        orderposition__in=public_order_positions, question__in=public_questions
    )
    public_answers = {(a.orderposition_id, a.question_id): a for a in answers}
    public_registrations = [
        {
            "gr_url": get_gravatar_url(pop.attendee_email or pop.order.code, size=24),
            "fields": (
                [pop.item.name]
                if sender.settings.get("public_registrations_show_item_name")
                else []
            )
            + (
                [pop.attendee_name_cached]
                if sender.settings.get("public_registrations_show_attendee_name")
                else []
            )
            + [
                (
                    public_answers[(pop.pk, pq.pk)].to_string_i18n
                    if public_answers.get((pop.pk, pq.pk))
                    else ""
                )
                for pq in public_questions
            ],
        }
        for pop in public_order_positions
    ]
    template = get_template("pretix_public_registrations/front_page.html")
    return template.render(
        {"headers": headers, "public_registrations": public_registrations}
    )


@receiver(signal=process_response, dispatch_uid="public_registragions_csp_headers")
def add_public_registrations_csp_headers(sender, request=None, response=None, **kwargs):
    if "event.index" in resolve(request.path_info).url_name:
        response["Content-Security-Policy"] = "img-src https://gravatar.com"
    return response


@receiver(signal=nav_event_settings, dispatch_uid="public_registrations_nav_settings")
def navbar_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    return [
        {
            "label": _("Public registrations"),
            "url": reverse(
                "plugins:pretix_public_registrations:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_public_registrations"
            and url.url_name == "settings",
        }
    ]


@receiver(signal=event_copy_data, dispatch_uid="public_registrations_event_copy_data")
def event_copy_public_registrations_data(sender, other, item_map, question_map, **_):
    sender.settings.set(
        "public_registrations_items",
        [
            str(item_map[int(old_id)].pk)
            for old_id in other.settings.get("public_registrations_items")
        ],
    )
    sender.settings.set(
        "public_registrations_questions",
        [
            str(question_map[int(old_id)].pk)
            for old_id in other.settings.get("public_registrations_questions")
        ],
    )
