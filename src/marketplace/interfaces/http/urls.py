from django.urls import path
from src.marketplace.interfaces.http import views

app_name = "marketplace"

urlpatterns = [
    path(
        "invitations/",
        views.provider_opportunity_inbox_view,
        name="inbox",
    ),
    path(
        "unlocked-opportunities/",
        views.provider_unlocked_opportunities_view,
        name="unlocked_opportunities",
    ),
    path(
        "invitations/<uuid:opportunity_invitation_id>/preview/",
        views.preview_opportunity_view,
        name="preview",
    ),
    path(
        "invitations/<uuid:opportunity_invitation_id>/quote/",
        views.quote_opportunity_unlock_view,
        name="quote",
    ),
    path(
        "invitations/<uuid:opportunity_invitation_id>/unlock/",
        views.unlock_opportunity_view,
        name="unlock",
    ),
    path(
        "opportunities/<uuid:opportunity_id>/contact/",
        views.get_opportunity_contact_view,
        name="contact",
    ),
]
