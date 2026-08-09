from datetime import datetime, timezone
import inspect
from uuid import uuid4, UUID

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from src.marketplace.application.ports import OpportunityPricingPolicy, CreditCostPolicy
from src.marketplace.domain.entities import (
    Money,
    OpportunityPricingQuote,
    OpportunityPricingUnavailable,
    OpportunityStatus,
    ServiceRequestStatus,
    CreditLedgerDirection,
    OpportunityInterest,
    OpportunityInvitation,
    Opportunity,
    Provider,
)
from src.marketplace.infrastructure.django.marketplace.models import (
    OpportunityAccessModel,
    OpportunityInvitationModel,
    OpportunityInterestModel,
    OpportunityModel,
    ProviderModel,
    ServiceCategoryModel,
    ServiceModel,
    ServiceRequestModel,
    CreditWalletModel,
    CreditLedgerEntryModel,
    EconomicSettlementModel,
    OpportunityContactReadAuditModel,
)
from src.marketplace.infrastructure.policies import (
    UnconfiguredOpportunityPricingPolicy,
    UnconfiguredCreditCostPolicy,
)
from src.marketplace.interfaces.http import views
from src.marketplace.interfaces.http.factories import (
    build_authenticated_provider_marketplace_service,
)
from src.memberships.infrastructure.django.memberships.models import MembershipModel
from src.organizations.infrastructure.django.organizations.models import OrganizationModel


UserModel = get_user_model()


class TestOpportunityPricingPolicy(OpportunityPricingPolicy):
    """Test double pricing policy for HTTP contract verification."""
    def __init__(self, amount_minor: int = 2500, currency: str = "BRL", reason: str = "Test pricing"):
        self._amount_minor = amount_minor
        self._currency = currency
        self._reason = reason

    def quote(
        self,
        *,
        interest: OpportunityInterest | None = None,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> OpportunityPricingQuote:
        if self._amount_minor is None:
            raise OpportunityPricingUnavailable("Pricing unavailable in test policy.")
        return OpportunityPricingQuote(
            amount=Money(amount_minor=self._amount_minor, currency=self._currency),
            reason=self._reason,
        )


class TestCreditCostPolicy(CreditCostPolicy):
    """Test double credit cost policy (1 credit per 100 minor units)."""
    def units_required(
        self,
        *,
        price: Money,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> int:
        if price is None or price.amount_minor < 0:
            return 0
        return price.amount_minor // 100


class MarketplaceHTTPDeliveryBoundaryTests(TestCase):
    """
    Complete HTTP Integration Test Suite for Marketplace Endpoints:
        - GET /api/marketplace/invitations/<id>/preview/
        - GET /api/marketplace/invitations/<id>/quote/
        - POST /api/marketplace/invitations/<id>/unlock/
        - GET /api/marketplace/opportunities/<id>/contact/
    """

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.now = datetime.now(timezone.utc)

        # Build test service with explicit test doubles for happy path unlock tests
        self.test_pricing_policy = TestOpportunityPricingPolicy(amount_minor=2500, currency="BRL")
        self.test_cost_policy = TestCreditCostPolicy()
        self.service_with_pricing = build_authenticated_provider_marketplace_service(
            pricing_policy=self.test_pricing_policy,
            credit_cost_policy=self.test_cost_policy,
        )

        # Create Category & Service
        self.category = ServiceCategoryModel.objects.create(
            id=uuid4(),
            name="Consulting",
            slug=f"cat-{uuid4().hex[:8]}",
            description="Desc",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.service = ServiceModel.objects.create(
            id=uuid4(),
            category=self.category,
            name="Tech Strategy",
            slug=f"srv-{uuid4().hex[:8]}",
            description="Desc",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )

        # Create User A + Org A + Provider A + Wallet A
        self.user_a = UserModel.objects.create_user(
            username="user_a",
            email="user_a@test.com",
            password="password",
        )
        self.org_a = OrganizationModel.objects.create(
            id=uuid4(),
            name="Org A",
            slug=f"orga-{uuid4().hex[:8]}",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.membership_a = MembershipModel.objects.create(
            id=uuid4(),
            user=self.user_a,
            organization=self.org_a,
            role="admin",
            is_active=True,
        )
        self.provider_a = ProviderModel.objects.create(
            id=uuid4(),
            organization=self.org_a,
            display_name="Provider A",
            slug=f"pa-{uuid4().hex[:8]}",
            description="Desc A",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.wallet_a = CreditWalletModel.objects.create(
            id=uuid4(),
            organization_id=self.org_a.id,
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        # Fund Wallet A with 50 credits
        CreditLedgerEntryModel.objects.create(
            id=uuid4(),
            wallet_id=self.wallet_a.id,
            direction=CreditLedgerDirection.CREDIT.value,
            units=50,
            reason="Initial deposit",
            reference="dep-1",
            created_at=self.now,
        )

        # Create User B + Org B + Provider B + Wallet B
        self.user_b = UserModel.objects.create_user(
            username="user_b",
            email="user_b@test.com",
            password="password",
        )
        self.org_b = OrganizationModel.objects.create(
            id=uuid4(),
            name="Org B",
            slug=f"orgb-{uuid4().hex[:8]}",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.membership_b = MembershipModel.objects.create(
            id=uuid4(),
            user=self.user_b,
            organization=self.org_b,
            role="admin",
            is_active=True,
        )
        self.provider_b = ProviderModel.objects.create(
            id=uuid4(),
            organization=self.org_b,
            display_name="Provider B",
            slug=f"pb-{uuid4().hex[:8]}",
            description="Desc B",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.wallet_b = CreditWalletModel.objects.create(
            id=uuid4(),
            organization_id=self.org_b.id,
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )

        # Create ServiceRequest + Opportunity
        self.service_request = ServiceRequestModel.objects.create(
            id=uuid4(),
            organization_id=self.org_a.id,
            service=self.service,
            title="Need Architecture Review",
            description="Project migration analysis",
            status=ServiceRequestStatus.OPEN.value,
            requester_name="Alice Requester",
            requester_email="alice@client.com",
            requester_phone="+551199999999",
            created_at=self.now,
            updated_at=self.now,
        )
        self.opportunity = OpportunityModel.objects.create(
            id=uuid4(),
            service_request=self.service_request,
            status=OpportunityStatus.OPEN.value,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )

        # Invitation for Provider A
        self.invitation_a = OpportunityInvitationModel.objects.create(
            id=uuid4(),
            opportunity=self.opportunity,
            provider=self.provider_a,
            created_at=self.now,
        )

    # -----------------------------------------------------------------------
    # 1. AUTHENTICATION TESTS (Anonymous callers denied 401)
    # -----------------------------------------------------------------------

    def test_anonymous_preview_denied(self):
        url = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json(), {"error": "Unauthenticated."})

    def test_anonymous_quote_denied(self):
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json(), {"error": "Unauthenticated."})

    def test_anonymous_unlock_denied(self):
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json(), {"error": "Unauthenticated."})

    def test_anonymous_contact_denied(self):
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json(), {"error": "Unauthenticated."})

    # -----------------------------------------------------------------------
    # 2. PREVIEW ENDPOINT TESTS
    # -----------------------------------------------------------------------

    def test_preview_happy_path(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["opportunity_id"], str(self.opportunity.id))
        self.assertEqual(data["service_request_id"], str(self.service_request.id))
        self.assertEqual(data["service_id"], str(self.service.id))
        self.assertEqual(data["title"], "Need Architecture Review")
        self.assertEqual(data["description"], "Project migration analysis")
        self.assertEqual(data["status"], "open")
        self.assertIn("created_at", data)

    def test_preview_exact_allowlist(self):
        """Confirm response contains only the exact allowed fields."""
        self.client.force_login(self.user_a)
        url = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        expected_keys = {
            "opportunity_id",
            "service_request_id",
            "service_id",
            "title",
            "description",
            "status",
            "created_at",
        }
        self.assertEqual(set(res.json().keys()), expected_keys)

    def test_preview_does_not_contain_pii(self):
        """Confirm preview never leaks requester PII."""
        self.client.force_login(self.user_a)
        url = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        data = res.json()
        self.assertNotIn("requester_name", data)
        self.assertNotIn("requester_email", data)
        self.assertNotIn("requester_phone", data)

    def test_preview_denies_cross_provider(self):
        """User B cannot preview Provider A's invitation."""
        self.client.force_login(self.user_b)
        url = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json(), {"error": "Access denied."})

    def test_preview_unknown_invitation(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": uuid4()})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json(), {"error": "Resource not found."})

    def test_preview_wrong_method_rejected(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 405)

    # -----------------------------------------------------------------------
    # 3. UNLOCK QUOTE ENDPOINT TESTS
    # -----------------------------------------------------------------------

    def test_quote_unconfigured_production_pricing_returns_quote_unavailable(self):
        """
        Default production composition root has NO commercial pricing policy.
        GET quote must return 200 with quote_available=False, amount=None.
        """
        self.client.force_login(self.user_a)
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["opportunity_id"], str(self.opportunity.id))
        self.assertFalse(data["quote_available"])
        self.assertIsNone(data["amount"])
        self.assertFalse(data["already_unlocked"])
        self.assertEqual(data["reason"], "No commercial pricing configured for pre-access unlock.")

    def test_quote_has_no_economic_side_effects(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})

        before_interest_count = OpportunityInterestModel.objects.count()
        before_access_count = OpportunityAccessModel.objects.count()
        before_settlement_count = EconomicSettlementModel.objects.count()
        before_ledger_count = CreditLedgerEntryModel.objects.count()
        before_debit_count = CreditLedgerEntryModel.objects.filter(
            direction=CreditLedgerDirection.DEBIT.value,
        ).count()
        before_wallet_count = CreditWalletModel.objects.count()

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(OpportunityInterestModel.objects.count(), before_interest_count)
        self.assertEqual(OpportunityAccessModel.objects.count(), before_access_count)
        self.assertEqual(EconomicSettlementModel.objects.count(), before_settlement_count)
        self.assertEqual(CreditLedgerEntryModel.objects.count(), before_ledger_count)
        self.assertEqual(
            CreditLedgerEntryModel.objects.filter(
                direction=CreditLedgerDirection.DEBIT.value,
            ).count(),
            before_debit_count,
        )
        self.assertEqual(CreditWalletModel.objects.count(), before_wallet_count)

    def test_quote_with_configured_pricing_policy(self):
        """Quote with explicit test double pricing policy."""
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        req = self.factory.get(url)
        req.user = self.user_a
        req._marketplace_service = self.service_with_pricing
        res = views.quote_opportunity_unlock_view(req, opportunity_invitation_id=self.invitation_a.id)
        self.assertEqual(res.status_code, 200)
        import json
        data = json.loads(res.content)
        self.assertTrue(data["quote_available"])
        self.assertEqual(data["amount"], {"amount_minor": 2500, "currency": "BRL"})

    def test_quote_exact_allowlist(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        expected_keys = {
            "opportunity_id",
            "amount",
            "quote_available",
            "already_unlocked",
            "reason",
        }
        self.assertEqual(set(res.json().keys()), expected_keys)

    def test_quote_denies_cross_provider(self):
        self.client.force_login(self.user_b)
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

    def test_quote_does_not_contain_pii(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        data = res.json()
        self.assertNotIn("requester_name", data)
        self.assertNotIn("requester_email", data)
        self.assertNotIn("requester_phone", data)

    def test_quote_wrong_method_rejected(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 405)

    # -----------------------------------------------------------------------
    # 4. UNLOCK ENDPOINT TESTS
    # -----------------------------------------------------------------------

    def test_unlock_unconfigured_production_pricing_fails_gracefully(self):
        """
        Without commercial pricing configured in production, unlock fails explicitly (400)
        before creating any debit, settlement, or access entitlement.
        """
        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {"error": "Invalid operation state."})
        # Prove no access was created
        self.assertFalse(
            OpportunityAccessModel.objects.filter(
                opportunity_id=self.opportunity.id,
                provider_id=self.provider_a.id,
            ).exists()
        )

    def test_unlock_with_configured_pricing_policy(self):
        """Unlock happy path with test double policies."""
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        req = self.factory.post(url)
        req.user = self.user_a
        req._marketplace_service = self.service_with_pricing
        res = views.unlock_opportunity_view(req, opportunity_invitation_id=self.invitation_a.id)
        self.assertEqual(res.status_code, 200)
        import json
        data = json.loads(res.content)
        self.assertEqual(data["opportunity_id"], str(self.opportunity.id))
        self.assertFalse(data["already_unlocked"])
        self.assertIsNotNone(data["settlement_id"])
        self.assertEqual(data["amount"], {"amount_minor": 2500, "currency": "BRL"})

        # Verify DB effect
        self.assertTrue(
            OpportunityAccessModel.objects.filter(
                opportunity_id=self.opportunity.id,
                provider_id=self.provider_a.id,
            ).exists()
        )

    def test_unlock_retry_idempotent_no_double_charge(self):
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})

        req1 = self.factory.post(url)
        req1.user = self.user_a
        req1._marketplace_service = self.service_with_pricing
        res1 = views.unlock_opportunity_view(req1, opportunity_invitation_id=self.invitation_a.id)
        self.assertEqual(res1.status_code, 200)

        # Retry unlock
        req2 = self.factory.post(url)
        req2.user = self.user_a
        req2._marketplace_service = self.service_with_pricing
        res2 = views.unlock_opportunity_view(req2, opportunity_invitation_id=self.invitation_a.id)
        self.assertEqual(res2.status_code, 200)
        import json
        data2 = json.loads(res2.content)
        self.assertTrue(data2["already_unlocked"])

        # Prove 1 debit entry created
        debit_count = CreditLedgerEntryModel.objects.filter(
            wallet_id=self.wallet_a.id,
            direction=CreditLedgerDirection.DEBIT.value,
        ).count()
        self.assertEqual(debit_count, 1)

    def test_unlock_denies_cross_provider(self):
        self.client.force_login(self.user_b)
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 403)

        # Verify no access created for provider B
        self.assertFalse(
            OpportunityAccessModel.objects.filter(
                opportunity_id=self.opportunity.id,
                provider_id=self.provider_b.id,
            ).exists()
        )

    def test_unlock_inactive_provider_denied(self):
        # Deactivate provider A
        self.provider_a.is_active = False
        self.provider_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json(), {"error": "Provider is inactive."})

    def test_unlock_wrong_method_rejected(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 405)

    # -----------------------------------------------------------------------
    # 5. PROTECTED CONTACT ENDPOINT TESTS
    # -----------------------------------------------------------------------

    def test_contact_happy_path(self):
        # Create access entitlement for Provider A
        OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity_id=self.opportunity.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )
        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["opportunity_id"], str(self.opportunity.id))
        self.assertEqual(data["service_request_id"], str(self.service_request.id))
        self.assertEqual(data["requester_name"], "Alice Requester")
        self.assertEqual(data["requester_email"], "alice@client.com")
        self.assertEqual(data["requester_phone"], "+551199999999")

    def test_contact_exact_allowlist(self):
        OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity_id=self.opportunity.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )
        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        expected_keys = {
            "opportunity_id",
            "service_request_id",
            "requester_name",
            "requester_email",
            "requester_phone",
        }
        self.assertEqual(set(res.json().keys()), expected_keys)

    def test_contact_cache_headers(self):
        OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity_id=self.opportunity.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )
        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertIn("no-store", res.headers.get("Cache-Control", ""))

    def test_contact_without_access_denied(self):
        # No OpportunityAccess created
        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json(), {"error": "Access denied."})

    def test_contact_cross_provider_denied(self):
        # Access exists for Provider A only
        OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity_id=self.opportunity.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )
        # User B tries to get contact
        self.client.force_login(self.user_b)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json(), {"error": "Access denied."})

    def test_contact_inactive_provider_with_access_allowed(self):
        """
        Inactive Provider A with active Membership + pre-existing OpportunityAccess
        MUST be allowed to retrieve historical contact data.
        """
        OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity_id=self.opportunity.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )
        # Deactivate Provider A (Membership remains active)
        self.provider_a.is_active = False
        self.provider_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["requester_name"], "Alice Requester")

    def test_contact_legacy_blank_strings_preserved(self):
        # Create service request with blank contact fields
        sr_blank = ServiceRequestModel.objects.create(
            id=uuid4(),
            organization_id=self.org_a.id,
            service=self.service,
            title="Blank Contact SR",
            description="Blank",
            status=ServiceRequestStatus.OPEN.value,
            requester_name="Bob",
            requester_email="",
            requester_phone="",
            created_at=self.now,
            updated_at=self.now,
        )
        opp_blank = OpportunityModel.objects.create(
            id=uuid4(),
            service_request=sr_blank,
            status=OpportunityStatus.OPEN.value,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )
        OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity_id=opp_blank.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )

        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": opp_blank.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["requester_email"], "")
        self.assertEqual(data["requester_phone"], "")

    def test_contact_wrong_method_rejected(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 405)

    # -----------------------------------------------------------------------
    # 5. INBOX ENDPOINT TESTS
    # -----------------------------------------------------------------------

    def test_anonymous_inbox_denied(self):
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json(), {"error": "Unauthenticated."})

    def test_inbox_happy_path(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["items"]), 1)
        item = data["items"][0]
        self.assertEqual(item["invitation_id"], str(self.invitation_a.id))
        self.assertEqual(item["opportunity_id"], str(self.opportunity.id))
        self.assertEqual(item["title"], "Need Architecture Review")
        self.assertEqual(item["status"], "open")
        self.assertEqual(data["pagination"], {
            "page": 1,
            "page_size": 20,
            "total_items": 1,
            "total_pages": 1,
        })

    def test_inbox_exact_allowlist(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(set(data.keys()), {"items", "pagination"})
        expected_item_keys = {
            "invitation_id",
            "opportunity_id",
            "service_request_id",
            "service_id",
            "title",
            "description",
            "status",
            "created_at",
        }
        self.assertEqual(set(data["items"][0].keys()), expected_item_keys)
        self.assertEqual(set(data["pagination"].keys()), {"page", "page_size", "total_items", "total_pages"})

    def test_inbox_does_not_contain_pii(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        raw_text = res.content.decode("utf-8")
        self.assertNotIn("requester_name", raw_text)
        self.assertNotIn("requester_email", raw_text)
        self.assertNotIn("requester_phone", raw_text)

    def test_inbox_empty_for_provider_without_invitations(self):
        self.client.force_login(self.user_b)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["items"], [])
        self.assertEqual(data["pagination"], {
            "page": 1,
            "page_size": 20,
            "total_items": 0,
            "total_pages": 0,
        })

    def test_inbox_cross_provider_isolation(self):
        """Provider B never receives Invitation A."""
        self.client.force_login(self.user_b)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        inv_ids = [item["invitation_id"] for item in res.json()["items"]]
        self.assertNotIn(str(self.invitation_a.id), inv_ids)

    def test_inbox_external_provider_id_query_param_ignored(self):
        """
        User B passes ?provider_id=<ProviderA_ID>.
        Query param MUST be ignored, returns Provider B inbox (empty).
        """
        self.client.force_login(self.user_b)
        url = f"{reverse('marketplace:inbox')}?provider_id={self.provider_a.id}"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["items"], [])

    def test_inbox_inactive_provider_allowed(self):
        """Inactive Provider A with active membership CAN view inbox history."""
        self.provider_a.is_active = False
        self.provider_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["invitation_id"], str(self.invitation_a.id))

    def test_inbox_inactive_membership_denied(self):
        self.membership_a.is_active = False
        self.membership_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json(), {"error": "Provider identity not found."})

    def test_inbox_pagination_first_and_second_page(self):
        # Create 2 more invitations for Provider A
        sr2 = ServiceRequestModel.objects.create(
            id=uuid4(),
            organization_id=self.org_a.id,
            service=self.service,
            title="SR 2",
            description="Desc 2",
            status=ServiceRequestStatus.OPEN.value,
            requester_name="Req 2",
            created_at=self.now,
            updated_at=self.now,
        )
        opp2 = OpportunityModel.objects.create(
            id=uuid4(),
            service_request=sr2,
            status=OpportunityStatus.OPEN.value,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )
        inv2 = OpportunityInvitationModel.objects.create(
            id=uuid4(),
            opportunity=opp2,
            provider=self.provider_a,
            created_at=self.now,
        )

        sr3 = ServiceRequestModel.objects.create(
            id=uuid4(),
            organization_id=self.org_a.id,
            service=self.service,
            title="SR 3",
            description="Desc 3",
            status=ServiceRequestStatus.OPEN.value,
            requester_name="Req 3",
            created_at=self.now,
            updated_at=self.now,
        )
        opp3 = OpportunityModel.objects.create(
            id=uuid4(),
            service_request=sr3,
            status=OpportunityStatus.OPEN.value,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )
        inv3 = OpportunityInvitationModel.objects.create(
            id=uuid4(),
            opportunity=opp3,
            provider=self.provider_a,
            created_at=self.now,
        )

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")

        # Page 1 (page_size=2)
        res1 = self.client.get(f"{url}?page=1&page_size=2")
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(len(data1["items"]), 2)
        self.assertEqual(data1["pagination"], {
            "page": 1,
            "page_size": 2,
            "total_items": 3,
            "total_pages": 2,
        })

        # Page 2 (page_size=2)
        res2 = self.client.get(f"{url}?page=2&page_size=2")
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(len(data2["items"]), 1)
        self.assertEqual(data2["pagination"], {
            "page": 2,
            "page_size": 2,
            "total_items": 3,
            "total_pages": 2,
        })

    def test_inbox_invalid_pagination_parameters(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")

        for bad_param in ["?page=0", "?page=-1", "?page=abc", "?page_size=0", "?page_size=101", "?page_size=xyz"]:
            res = self.client.get(f"{url}{bad_param}")
            self.assertEqual(res.status_code, 400, f"Failed for {bad_param}")
            self.assertEqual(res.json(), {"error": "Invalid pagination parameters."})

    def test_inbox_cache_headers(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(url)
        self.assertIn("private", res.headers.get("Cache-Control", ""))
        self.assertIn("no-store", res.headers.get("Cache-Control", ""))

    def test_inbox_wrong_method_rejected(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.post(url)
        self.assertEqual(res.status_code, 405)

    def test_inbox_query_count_is_bounded_and_prevents_n_plus_one(self):
        """
        Verify that query count for listing inbox items is independent of item count
        (eliminating N+1 query regression).
        """
        # Create 10 invitations for Provider A
        for i in range(10):
            sr = ServiceRequestModel.objects.create(
                id=uuid4(),
                organization_id=self.org_a.id,
                service=self.service,
                title=f"Bulk SR {i}",
                description=f"Bulk Desc {i}",
                status=ServiceRequestStatus.OPEN.value,
                requester_name=f"Bulk Req {i}",
                created_at=self.now,
                updated_at=self.now,
            )
            opp = OpportunityModel.objects.create(
                id=uuid4(),
                service_request=sr,
                status=OpportunityStatus.OPEN.value,
                max_accesses=3,
                created_at=self.now,
                updated_at=self.now,
            )
            OpportunityInvitationModel.objects.create(
                id=uuid4(),
                opportunity=opp,
                provider=self.provider_a,
                created_at=self.now,
            )

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")

        # Measure queries for 1 item vs 10 items (queries must be bounded & identical)
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        with CaptureQueriesContext(connection) as ctx_1:
            res_1 = self.client.get(f"{url}?page=1&page_size=1")
            self.assertEqual(res_1.status_code, 200)
            self.assertEqual(len(res_1.json()["items"]), 1)

        with CaptureQueriesContext(connection) as ctx_10:
            res_10 = self.client.get(f"{url}?page=1&page_size=10")
            self.assertEqual(res_10.status_code, 200)
            self.assertEqual(len(res_10.json()["items"]), 10)

        # Prove query count for 10 items equals query count for 1 item (0 per-item queries)
        self.assertEqual(
            len(ctx_1.captured_queries),
            len(ctx_10.captured_queries),
            f"Queries for 1 item ({len(ctx_1.captured_queries)}) != Queries for 10 items ({len(ctx_10.captured_queries)})"
        )

    def _create_invitation_with_status(self, provider, status):
        sr = ServiceRequestModel.objects.create(
            id=uuid4(),
            organization_id=self.org_a.id,
            service=self.service,
            title="SR Status Test",
            description="Desc",
            status=ServiceRequestStatus.OPEN.value,
            requester_name="Req",
            created_at=self.now,
            updated_at=self.now,
        )
        opp = OpportunityModel.objects.create(
            id=uuid4(),
            service_request=sr,
            status=status.value,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )
        return OpportunityInvitationModel.objects.create(
            id=uuid4(),
            opportunity=opp,
            provider=provider,
            created_at=self.now,
        )

    def test_inbox_filter_open(self):
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        self._create_invitation_with_status(self.provider_a, OpportunityStatus.OPEN)
        self._create_invitation_with_status(self.provider_a, OpportunityStatus.CLOSED)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(f"{url}?status=open")
        self.assertEqual(res.status_code, 200)
        items = res.json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["status"], "open")
        self.assertEqual(res.json()["pagination"]["total_items"], 1)

    def test_inbox_filter_closed(self):
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        self._create_invitation_with_status(self.provider_a, OpportunityStatus.OPEN)
        self._create_invitation_with_status(self.provider_a, OpportunityStatus.CLOSED)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(f"{url}?status=closed")
        self.assertEqual(res.status_code, 200)
        items = res.json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["status"], "closed")
        self.assertEqual(res.json()["pagination"]["total_items"], 1)

    def test_inbox_filter_cancelled(self):
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        self._create_invitation_with_status(self.provider_a, OpportunityStatus.OPEN)
        self._create_invitation_with_status(self.provider_a, OpportunityStatus.CANCELLED)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(f"{url}?status=cancelled")
        self.assertEqual(res.status_code, 200)
        items = res.json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["status"], "cancelled")
        self.assertEqual(res.json()["pagination"]["total_items"], 1)

    def test_inbox_filter_invalid(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(f"{url}?status=banana")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {"error": "Invalid status."})

    def test_inbox_filter_case_sensitive(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(f"{url}?status=OPEN")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {"error": "Invalid status."})

    def test_inbox_filter_cross_provider(self):
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        # Provider A has one OPEN invitation
        self._create_invitation_with_status(self.provider_a, OpportunityStatus.OPEN)
        # Provider B has one OPEN invitation
        self._create_invitation_with_status(self.provider_b, OpportunityStatus.OPEN)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        # Even with provider_id parameter pointing to B, A should only see A's inbox
        res = self.client.get(f"{url}?status=open&provider_id={self.provider_b.id}")
        self.assertEqual(res.status_code, 200)
        items = res.json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(res.json()["pagination"]["total_items"], 1)

    def test_inbox_filter_pagination(self):
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        # Create 3 open opportunities for Provider A
        for _ in range(3):
            self._create_invitation_with_status(self.provider_a, OpportunityStatus.OPEN)
        # Create 1 closed opportunity
        self._create_invitation_with_status(self.provider_a, OpportunityStatus.CLOSED)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")
        res = self.client.get(f"{url}?status=open&page=1&page_size=2")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["pagination"]["total_items"], 3)
        self.assertEqual(data["pagination"]["total_pages"], 2)

    def test_inbox_filter_query_count_prevents_n_plus_one(self):
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        # Create 10 OPEN opportunities for Provider A
        for _ in range(10):
            self._create_invitation_with_status(self.provider_a, OpportunityStatus.OPEN)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:inbox")

        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        with CaptureQueriesContext(connection) as ctx_1:
            res_1 = self.client.get(f"{url}?status=open&page=1&page_size=1")
            self.assertEqual(res_1.status_code, 200)
            self.assertEqual(len(res_1.json()["items"]), 1)

        with CaptureQueriesContext(connection) as ctx_10:
            res_10 = self.client.get(f"{url}?status=open&page=1&page_size=10")
            self.assertEqual(res_10.status_code, 200)
            self.assertEqual(len(res_10.json()["items"]), 10)

        self.assertEqual(
            len(ctx_1.captured_queries),
            len(ctx_10.captured_queries),
            f"Queries with status filter: 1 item ({len(ctx_1.captured_queries)}) != 10 items ({len(ctx_10.captured_queries)})"
        )

    def _create_access_with_status(self, provider, status):
        sr = ServiceRequestModel.objects.create(
            id=uuid4(),
            organization_id=self.org_a.id,
            service=self.service,
            title="SR Status Test",
            description="Desc",
            status=ServiceRequestStatus.OPEN.value,
            requester_name="Req",
            created_at=self.now,
            updated_at=self.now,
        )
        opp = OpportunityModel.objects.create(
            id=uuid4(),
            service_request=sr,
            status=status.value,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )
        return OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity=opp,
            provider=provider,
            created_at=self.now,
        )

    def _create_access(self, provider, opportunity):
        return OpportunityAccessModel.objects.create(
            id=uuid4(),
            opportunity=opportunity,
            provider=provider,
            created_at=self.now,
        )

    def test_unlocked_opportunities_anonymous_denied(self):
        url = reverse("marketplace:unlocked_opportunities")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 401)

    def test_unlocked_opportunities_happy_path(self):
        OpportunityAccessModel.objects.all().delete()
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        self._create_access_with_status(self.provider_a, OpportunityStatus.OPEN)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        
        data = res.json()
        self.assertEqual(data["total_items"], 1)
        self.assertEqual(len(data["items"]), 1)
        item = data["items"][0]
        # Assert exact response keys allowlist
        self.assertEqual(
            set(item.keys()),
            {
                "opportunity_id",
                "service_request_id",
                "service_id",
                "title",
                "description",
                "status",
                "unlocked_at",
            }
        )
        # Ensure no PII in list
        self.assertFalse(hasattr(item, "requester_name"))
        self.assertFalse(hasattr(item, "requester_email"))
        self.assertFalse(hasattr(item, "requester_phone"))

    def test_unlocked_opportunities_cross_provider_isolation(self):
        OpportunityAccessModel.objects.all().delete()
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        self._create_access_with_status(self.provider_a, OpportunityStatus.OPEN)
        acc_b = self._create_access_with_status(self.provider_b, OpportunityStatus.OPEN)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")
        # Try passing external provider_id in query parameter, should be ignored
        res = self.client.get(f"{url}?provider_id={self.provider_b.id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_items"], 1)
        # Ensure B is excluded
        opp_ids = {it["opportunity_id"] for it in data["items"]}
        self.assertNotIn(str(acc_b.opportunity_id), opp_ids)

    def test_unlocked_opportunities_inactive_provider_allowed(self):
        OpportunityAccessModel.objects.all().delete()
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        self._create_access_with_status(self.provider_a, OpportunityStatus.OPEN)

        # Deactivate provider A
        self.provider_a.is_active = False
        self.provider_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total_items"], 1)

    def test_unlocked_opportunities_inactive_membership_denied(self):
        self.membership_a.is_active = False
        self.membership_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

    def test_unlocked_opportunities_pagination(self):
        OpportunityAccessModel.objects.all().delete()
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        # Create 3 accesses for Provider A
        for _ in range(3):
            self._create_access_with_status(self.provider_a, OpportunityStatus.OPEN)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")
        res = self.client.get(f"{url}?page=1&page_size=2")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["total_items"], 3)
        self.assertEqual(data["total_pages"], 2)

    def test_unlocked_opportunities_cache_control_headers(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")
        res = self.client.get(url)
        self.assertIn("private", res.headers.get("Cache-Control", ""))
        self.assertIn("no-store", res.headers.get("Cache-Control", ""))

    def test_unlocked_opportunities_wrong_method_rejected(self):
        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")
        res = self.client.post(url)
        self.assertEqual(res.status_code, 405)

    def test_unlocked_opportunities_query_count_is_bounded(self):
        OpportunityAccessModel.objects.all().delete()
        OpportunityInvitationModel.objects.all().delete()
        OpportunityModel.objects.all().delete()
        ServiceRequestModel.objects.all().delete()

        # Create 10 accesses for Provider A
        for _ in range(10):
            self._create_access_with_status(self.provider_a, OpportunityStatus.OPEN)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:unlocked_opportunities")

        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        with CaptureQueriesContext(connection) as ctx_1:
            res_1 = self.client.get(f"{url}?page=1&page_size=1")
            self.assertEqual(res_1.status_code, 200)
            self.assertEqual(len(res_1.json()["items"]), 1)

        with CaptureQueriesContext(connection) as ctx_10:
            res_10 = self.client.get(f"{url}?page=1&page_size=10")
            self.assertEqual(res_10.status_code, 200)
            self.assertEqual(len(res_10.json()["items"]), 10)

        # Bounded query count (no N+1 query regression)
        self.assertEqual(
            len(ctx_1.captured_queries),
            len(ctx_10.captured_queries),
            f"N+1 regression: queries for 1 item ({len(ctx_1.captured_queries)}) != queries for 10 items ({len(ctx_10.captured_queries)})"
        )


    # -----------------------------------------------------------------------
    # 6. REGRESSION, PROVENANCE & SECURITY MATRIX TESTS
    # -----------------------------------------------------------------------

    def test_external_provider_id_payload_ignored(self):
        """
        User B sends request containing provider_id of Provider A in query/body.
        Server MUST NOT trust caller payload — User B remains Provider B, and
        the request is denied (403).
        """
        self.client.force_login(self.user_b)
        url = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        res = self.client.post(
            url,
            data={"provider_id": str(self.provider_a.id)},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 403)
        # Verify Provider A was not unlocked by User B
        self.assertFalse(
            OpportunityAccessModel.objects.filter(
                opportunity_id=self.opportunity.id,
                provider_id=self.provider_a.id,
            ).exists()
        )

    def test_knowing_uuids_does_not_authorize(self):
        """
        Provider B knowing Invitation A UUID & Opportunity A UUID is still denied.
        """
        self.client.force_login(self.user_b)

        # 1. Preview
        url_preview = reverse("marketplace:preview", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        self.assertEqual(self.client.get(url_preview).status_code, 403)

        # 2. Quote
        url_quote = reverse("marketplace:quote", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        self.assertEqual(self.client.get(url_quote).status_code, 403)

        # 3. Unlock
        url_unlock = reverse("marketplace:unlock", kwargs={"opportunity_invitation_id": self.invitation_a.id})
        self.assertEqual(self.client.post(url_unlock).status_code, 403)

        # 4. Contact
        url_contact = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        self.assertEqual(self.client.get(url_contact).status_code, 403)

    def test_provenance_audit_production_policies_contain_no_hardcoded_economic_constants(self):
        """
        Verify that production policy implementations in src/marketplace/infrastructure/policies.py
        do NOT contain invented economic defaults (e.g. 2500, amount_minor // 100).
        """
        policies_source = inspect.getsource(UnconfiguredOpportunityPricingPolicy) + inspect.getsource(UnconfiguredCreditCostPolicy)
        self.assertNotIn("2500", policies_source)
        self.assertNotIn("amount_minor // 100", policies_source)
        self.assertNotIn("Standard commercial unlock", policies_source)

    def test_contact_read_audit_success(self):
        OpportunityContactReadAuditModel.objects.all().delete()
        self._create_access(self.provider_a, self.opportunity)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        # Verify exactly 1 audit record created
        audits = list(OpportunityContactReadAuditModel.objects.all())
        self.assertEqual(len(audits), 1)
        audit = audits[0]
        self.assertEqual(audit.authenticated_user_id, self.user_a.id)
        self.assertEqual(audit.provider_id, self.provider_a.id)
        self.assertEqual(audit.opportunity_id, self.opportunity.id)
        self.assertEqual(audit.service_request_id, self.service_request.id)

    def test_contact_read_audit_repeat(self):
        OpportunityContactReadAuditModel.objects.all().delete()
        self._create_access(self.provider_a, self.opportunity)

        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 200)

        # Verify exactly 2 audit records created
        self.assertEqual(OpportunityContactReadAuditModel.objects.count(), 2)

    def test_contact_read_audit_denied(self):
        OpportunityContactReadAuditModel.objects.all().delete()
        # provider_b has NO access to this opportunity

        self.client.force_login(self.user_b)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

        # Verify 0 audit records created
        self.assertEqual(OpportunityContactReadAuditModel.objects.count(), 0)

    def test_contact_read_audit_inactive_provider_allowed(self):
        OpportunityContactReadAuditModel.objects.all().delete()
        self._create_access(self.provider_a, self.opportunity)

        self.provider_a.is_active = False
        self.provider_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        # Verify 1 audit record created
        self.assertEqual(OpportunityContactReadAuditModel.objects.count(), 1)

    def test_contact_read_audit_inactive_membership_denied(self):
        OpportunityContactReadAuditModel.objects.all().delete()
        self._create_access(self.provider_a, self.opportunity)

        self.membership_a.is_active = False
        self.membership_a.save()

        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

        # Verify 0 audit records created
        self.assertEqual(OpportunityContactReadAuditModel.objects.count(), 0)

    def test_contact_read_audit_failure_blocks_pii(self):
        OpportunityContactReadAuditModel.objects.all().delete()
        self._create_access(self.provider_a, self.opportunity)

        from unittest.mock import patch
        self.client.force_login(self.user_a)
        url = reverse("marketplace:contact", kwargs={"opportunity_id": self.opportunity.id})

        with patch("src.marketplace.infrastructure.django.repositories.DjangoProtectedDataReadAuditWriter.record_contact_read", side_effect=RuntimeError("Audit persistence failed")):
            res = self.client.get(url, raise_request_exception=False)
            # Must return a non-2xx failure status (500) and no PII payload in response body
            self.assertEqual(res.status_code, 500)
            data = res.json()
            self.assertNotIn("requester_email", data)
            self.assertNotIn("requester_name", data)
            self.assertNotIn("requester_phone", data)

        # Verify 0 audit records created
        self.assertEqual(OpportunityContactReadAuditModel.objects.count(), 0)
