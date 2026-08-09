from uuid import UUID
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from src.marketplace.application.use_cases import (
    AuthenticatedProviderMarketplaceService,
    ProviderIdentityNotFound,
    AmbiguousProviderIdentity,
)
from src.marketplace.interfaces.http.factories import (
    build_authenticated_provider_marketplace_service,
)


from src.marketplace.domain.entities import (
    OpportunityPricingUnavailable,
    OpportunityStatus,
)


def _get_service(request: HttpRequest) -> AuthenticatedProviderMarketplaceService:
    """
    Retrieve or construct the AuthenticatedProviderMarketplaceService.
    Can be overridden in tests via request._marketplace_service.
    """
    if hasattr(request, "_marketplace_service") and request._marketplace_service is not None:
        return request._marketplace_service
    return build_authenticated_provider_marketplace_service()


def _handle_domain_exceptions(exc: Exception) -> JsonResponse | None:
    """
    Map known expected business and identity domain exceptions to safe HTTP responses.
    Unexpected exceptions (RuntimeError, DB error, etc.) are NOT handled here
    so they propagate for 500 logging/observability.
    """
    if isinstance(exc, ProviderIdentityNotFound):
        return JsonResponse({"error": "Provider identity not found."}, status=403)
    if isinstance(exc, AmbiguousProviderIdentity):
        return JsonResponse({"error": "Ambiguous provider identity."}, status=403)
    if isinstance(exc, OpportunityPricingUnavailable):
        return JsonResponse({"error": "Invalid operation state."}, status=400)
    if isinstance(exc, ValueError):
        msg = str(exc)
        if "inactive" in msg.lower():
            return JsonResponse({"error": "Provider is inactive."}, status=403)
        if "does not exist" in msg:
            return JsonResponse({"error": "Resource not found."}, status=404)
        if "does not belong" in msg or "Access entitlement missing" in msg:
            return JsonResponse({"error": "Access denied."}, status=403)
        return JsonResponse({"error": "Invalid operation state."}, status=400)
    return None


@require_GET
def preview_opportunity_view(
    request: HttpRequest,
    opportunity_invitation_id: UUID,
) -> HttpResponse:
    """
    GET /api/marketplace/invitations/<uuid:opportunity_invitation_id>/preview/
    Return a sanitized preview of an opportunity.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthenticated."}, status=401)

    service = _get_service(request)
    try:
        preview = service.preview(
            authenticated_user_id=request.user.pk,
            opportunity_invitation_id=opportunity_invitation_id,
        )
    except Exception as exc:
        resp = _handle_domain_exceptions(exc)
        if resp is not None:
            return resp
        raise

    return JsonResponse(
        {
            "opportunity_id": str(preview.opportunity_id),
            "service_request_id": str(preview.service_request_id),
            "service_id": str(preview.service_id),
            "title": preview.title,
            "description": preview.description,
            "status": preview.status.value if hasattr(preview.status, "value") else str(preview.status),
            "created_at": preview.created_at.isoformat(),
        },
        status=200,
    )


@require_GET
def quote_opportunity_unlock_view(
    request: HttpRequest,
    opportunity_invitation_id: UUID,
) -> HttpResponse:
    """
    GET /api/marketplace/invitations/<uuid:opportunity_invitation_id>/quote/
    Return a commercial unlock pricing quote for an opportunity.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthenticated."}, status=401)

    service = _get_service(request)
    try:
        quote = service.quote(
            authenticated_user_id=request.user.pk,
            opportunity_invitation_id=opportunity_invitation_id,
        )
    except Exception as exc:
        resp = _handle_domain_exceptions(exc)
        if resp is not None:
            return resp
        raise

    amount_payload = None
    if quote.amount is not None:
        amount_payload = {
            "amount_minor": quote.amount.amount_minor,
            "currency": quote.amount.currency,
        }

    return JsonResponse(
        {
            "opportunity_id": str(quote.opportunity_id),
            "amount": amount_payload,
            "quote_available": quote.quote_available,
            "already_unlocked": quote.already_unlocked,
            "reason": quote.reason,
        },
        status=200,
    )


@require_POST
def unlock_opportunity_view(
    request: HttpRequest,
    opportunity_invitation_id: UUID,
) -> HttpResponse:
    """
    POST /api/marketplace/invitations/<uuid:opportunity_invitation_id>/unlock/
    Atomically unlock an opportunity for the authenticated provider.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthenticated."}, status=401)

    service = _get_service(request)
    try:
        result = service.unlock(
            authenticated_user_id=request.user.pk,
            opportunity_invitation_id=opportunity_invitation_id,
        )
    except Exception as exc:
        resp = _handle_domain_exceptions(exc)
        if resp is not None:
            return resp
        raise

    amount_payload = None
    if result.amount is not None:
        amount_payload = {
            "amount_minor": result.amount.amount_minor,
            "currency": result.amount.currency,
        }

    return JsonResponse(
        {
            "opportunity_id": str(result.access.opportunity_id),
            "already_unlocked": result.already_unlocked,
            "settlement_id": str(result.settlement_id) if result.settlement_id else None,
            "amount": amount_payload,
        },
        status=200,
    )


@require_GET
def get_opportunity_contact_view(
    request: HttpRequest,
    opportunity_id: UUID,
) -> HttpResponse:
    """
    GET /api/marketplace/opportunities/<uuid:opportunity_id>/contact/
    Retrieve protected requester contact data for an unlocked opportunity.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthenticated."}, status=401)

    service = _get_service(request)
    try:
        contact = service.get_contact(
            authenticated_user_id=request.user.pk,
            opportunity_id=opportunity_id,
        )
    except Exception as exc:
        resp = _handle_domain_exceptions(exc)
        if resp is not None:
            return resp
        return JsonResponse({"error": "Internal server error."}, status=500)

    response = JsonResponse(
        {
            "opportunity_id": str(contact.opportunity_id),
            "service_request_id": str(contact.service_request_id),
            "requester_name": contact.requester_name,
            "requester_email": contact.requester_email,
            "requester_phone": contact.requester_phone,
        },
        status=200,
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    return response


@require_GET
def provider_opportunity_inbox_view(
    request: HttpRequest,
) -> HttpResponse:
    """
    GET /api/marketplace/invitations/
    Retrieve paginated opportunity invitations for the authenticated provider's inbox.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthenticated."}, status=401)

    raw_page = request.GET.get("page", "1")
    raw_page_size = request.GET.get("page_size", "20")
    raw_status = request.GET.get("status")

    try:
        page = int(raw_page)
        page_size = int(raw_page_size)
        if page < 1 or page_size < 1 or page_size > 100:
            return JsonResponse({"error": "Invalid pagination parameters."}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid pagination parameters."}, status=400)

    status = None
    if raw_status is not None:
        try:
            status = OpportunityStatus(raw_status)
        except ValueError:
            return JsonResponse({"error": "Invalid status."}, status=400)

    service = _get_service(request)
    try:
        inbox_page = service.inbox(
            authenticated_user_id=request.user.pk,
            page=page,
            page_size=page_size,
            status=status,
        )
    except Exception as exc:
        resp = _handle_domain_exceptions(exc)
        if resp is not None:
            return resp
        raise

    items_payload = [
        {
            "invitation_id": str(item.invitation_id),
            "opportunity_id": str(item.opportunity_id),
            "service_request_id": str(item.service_request_id),
            "service_id": str(item.service_id),
            "title": item.title,
            "description": item.description,
            "status": item.status.value if hasattr(item.status, "value") else str(item.status),
            "created_at": item.created_at.isoformat(),
        }
        for item in inbox_page.items
    ]

    response = JsonResponse(
        {
            "items": items_payload,
            "pagination": {
                "page": inbox_page.page,
                "page_size": inbox_page.page_size,
                "total_items": inbox_page.total_items,
                "total_pages": inbox_page.total_pages,
            },
        },
        status=200,
    )
    response["Cache-Control"] = "private, no-store"
    return response


@require_GET
def provider_unlocked_opportunities_view(
    request: HttpRequest,
) -> HttpResponse:
    """
    GET /api/marketplace/unlocked-opportunities/
    Retrieve paginated historical unlocked opportunities for the authenticated provider.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthenticated."}, status=401)

    raw_page = request.GET.get("page", "1")
    raw_page_size = request.GET.get("page_size", "20")

    try:
        page = int(raw_page)
        page_size = int(raw_page_size)
        if page < 1 or page_size < 1 or page_size > 100:
            return JsonResponse({"error": "Invalid pagination parameters."}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid pagination parameters."}, status=400)

    service = _get_service(request)
    try:
        unlocked_page = service.unlocked_opportunities(
            authenticated_user_id=request.user.pk,
            page=page,
            page_size=page_size,
        )
    except Exception as exc:
        resp = _handle_domain_exceptions(exc)
        if resp is not None:
            return resp
        raise

    items_payload = [
        {
            "opportunity_id": str(item.opportunity_id),
            "service_request_id": str(item.service_request_id),
            "service_id": str(item.service_id),
            "title": item.title,
            "description": item.description,
            "status": item.status.value if hasattr(item.status, "value") else str(item.status),
            "unlocked_at": item.unlocked_at.isoformat(),
        }
        for item in unlocked_page.items
    ]

    response = JsonResponse(
        {
            "items": items_payload,
            "page": unlocked_page.page,
            "page_size": unlocked_page.page_size,
            "total_items": unlocked_page.total_items,
            "total_pages": unlocked_page.total_pages,
        },
        status=200,
    )
    response["Cache-Control"] = "private, no-store"
    return response

