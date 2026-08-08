from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4

from django.test import SimpleTestCase

from src.marketplace.domain.entities import (
    MatchingResult,
    Opportunity,
    OpportunityAccess,
    OpportunityInvitation,
    OpportunityInterest,
    OpportunityStatus,
    Provider,
    ProviderService,
    Service,
    ServiceCategory,
    ServiceRequest,
    ServiceRequestStatus,
    AccessEntitlementDecision,
    RequestOpportunityAccessResult,
    Money,
    OpportunityPricingQuote,
    SettlementMethod,
    EconomicSettlement,
    CreditWallet,
    CreditLedgerDirection,
    CreditLedgerEntry,
)


class ServiceCategoryDomainTests(SimpleTestCase):
    def test_valid_creation_normalizes_name_and_slug(self):
        service_category = ServiceCategory(
            id=uuid4(),
            name="  Automacao Industrial  ",
            slug="  AUTOMACAO-INDUSTRIAL  ",
            description="  Categoria principal  ",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertEqual(service_category.name, "Automacao Industrial")
        self.assertEqual(service_category.slug, "automacao-industrial")
        self.assertEqual(service_category.description, "Categoria principal")

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceCategory(
                id=uuid4(),
                name="   ",
                slug="valid-slug",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_empty_slug_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceCategory(
                id=uuid4(),
                name="Valid Name",
                slug="   ",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_activate_and_deactivate(self):
        service_category = ServiceCategory(
            id=uuid4(),
            name="Valid Name",
            slug="valid-slug",
            description="x",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        service_category.deactivate()
        self.assertFalse(service_category.is_active)

        service_category.activate()
        self.assertTrue(service_category.is_active)


class ServiceDomainTests(SimpleTestCase):
    def test_valid_creation_normalizes_fields(self):
        service = Service(
            id=uuid4(),
            category_id=uuid4(),
            name="  Manutencao  ",
            slug="  MANUTENCAO  ",
            description="  Descricao  ",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertEqual(service.name, "Manutencao")
        self.assertEqual(service.slug, "manutencao")
        self.assertEqual(service.description, "Descricao")

    def test_category_id_is_required(self):
        with self.assertRaises(ValueError):
            Service(
                id=uuid4(),
                category_id=None,
                name="Servico",
                slug="servico",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_category_id_must_be_uuid_instance(self):
        with self.assertRaises(ValueError):
            Service(
                id=uuid4(),
                category_id="invalid-uuid",
                name="Servico",
                slug="servico",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            Service(
                id=uuid4(),
                category_id=uuid4(),
                name="   ",
                slug="servico",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_empty_slug_is_rejected(self):
        with self.assertRaises(ValueError):
            Service(
                id=uuid4(),
                category_id=uuid4(),
                name="Servico",
                slug="   ",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_activate_and_deactivate(self):
        service = Service(
            id=uuid4(),
            category_id=uuid4(),
            name="Servico",
            slug="servico",
            description="x",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        service.deactivate()
        self.assertFalse(service.is_active)

        service.activate()
        self.assertTrue(service.is_active)


class ProviderDomainTests(SimpleTestCase):
    def test_valid_creation_normalizes_fields(self):
        provider = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="  ACME Automacao  ",
            slug="  ACME-AUTOMACAO  ",
            description="  Perfil operacional  ",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertEqual(provider.display_name, "ACME Automacao")
        self.assertEqual(provider.slug, "acme-automacao")
        self.assertEqual(provider.description, "Perfil operacional")

    def test_organization_id_is_required(self):
        with self.assertRaises(ValueError):
            Provider(
                id=uuid4(),
                organization_id=None,
                display_name="ACME",
                slug="acme",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_organization_id_must_be_uuid_instance(self):
        with self.assertRaises(ValueError):
            Provider(
                id=uuid4(),
                organization_id="invalid-uuid",
                display_name="ACME",
                slug="acme",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_empty_display_name_is_rejected(self):
        with self.assertRaises(ValueError):
            Provider(
                id=uuid4(),
                organization_id=uuid4(),
                display_name="   ",
                slug="acme",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_empty_slug_is_rejected(self):
        with self.assertRaises(ValueError):
            Provider(
                id=uuid4(),
                organization_id=uuid4(),
                display_name="ACME",
                slug="   ",
                description="x",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_activate_and_deactivate(self):
        provider = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="ACME",
            slug="acme",
            description="x",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        provider.deactivate()
        self.assertFalse(provider.is_active)

        provider.activate()
        self.assertTrue(provider.is_active)


class ProviderServiceDomainTests(SimpleTestCase):
    def test_valid_creation(self):
        provider_service = ProviderService(
            id=uuid4(),
            provider_id=uuid4(),
            service_id=uuid4(),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertTrue(provider_service.is_active)

    def test_provider_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            ProviderService(
                id=uuid4(),
                provider_id=None,
                service_id=uuid4(),
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_provider_id_non_uuid_is_rejected(self):
        with self.assertRaises(ValueError):
            ProviderService(
                id=uuid4(),
                provider_id="invalid-uuid",
                service_id=uuid4(),
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_service_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            ProviderService(
                id=uuid4(),
                provider_id=uuid4(),
                service_id=None,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_service_id_non_uuid_is_rejected(self):
        with self.assertRaises(ValueError):
            ProviderService(
                id=uuid4(),
                provider_id=uuid4(),
                service_id="invalid-uuid",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_activate_and_deactivate(self):
        provider_service = ProviderService(
            id=uuid4(),
            provider_id=uuid4(),
            service_id=uuid4(),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        provider_service.deactivate()
        self.assertFalse(provider_service.is_active)

        provider_service.activate()
        self.assertTrue(provider_service.is_active)


class ServiceRequestDomainTests(SimpleTestCase):
    def test_valid_creation(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="  Manutencao de CLP  ",
            description="  CLP nao inicia  ",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertEqual(service_request.title, "Manutencao de CLP")
        self.assertEqual(service_request.description, "CLP nao inicia")
        self.assertEqual(service_request.status, ServiceRequestStatus.OPEN)

    def test_organization_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=None,
                service_id=uuid4(),
                title="Titulo",
                description="x",
                status=ServiceRequestStatus.OPEN,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_organization_id_non_uuid_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id="invalid-uuid",
                service_id=uuid4(),
                title="Titulo",
                description="x",
                status=ServiceRequestStatus.OPEN,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_service_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=uuid4(),
                service_id=None,
                title="Titulo",
                description="x",
                status=ServiceRequestStatus.OPEN,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_service_id_non_uuid_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=uuid4(),
                service_id="invalid-uuid",
                title="Titulo",
                description="x",
                status=ServiceRequestStatus.OPEN,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_title_empty_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=uuid4(),
                service_id=uuid4(),
                title="   ",
                description="x",
                status=ServiceRequestStatus.OPEN,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_status_must_be_enum(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=uuid4(),
                service_id=uuid4(),
                title="Titulo",
                description="x",
                status="open",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_cancel_open_to_cancelled(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Titulo",
            description="x",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        service_request.cancel()

        self.assertEqual(service_request.status, ServiceRequestStatus.CANCELLED)

    def test_cancel_non_open_is_rejected(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Titulo",
            description="x",
            status=ServiceRequestStatus.CLOSED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with self.assertRaises(ValueError):
            service_request.cancel()

    def test_close_open_to_closed(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Titulo",
            description="x",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        service_request.close()

        self.assertEqual(service_request.status, ServiceRequestStatus.CLOSED)

    def test_close_non_open_is_rejected(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Titulo",
            description="x",
            status=ServiceRequestStatus.CANCELLED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with self.assertRaises(ValueError):
            service_request.close()


class OpportunityDomainTests(SimpleTestCase):
    def test_valid_creation(self):
        opportunity = Opportunity(
            id=uuid4(),
            service_request_id=uuid4(),
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertEqual(opportunity.status, OpportunityStatus.OPEN)
        self.assertEqual(opportunity.max_accesses, 3)

    def test_service_request_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            Opportunity(
                id=uuid4(),
                service_request_id=None,
                status=OpportunityStatus.OPEN,
                max_accesses=3,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_service_request_id_non_uuid_is_rejected(self):
        with self.assertRaises(ValueError):
            Opportunity(
                id=uuid4(),
                service_request_id="invalid-uuid",
                status=OpportunityStatus.OPEN,
                max_accesses=3,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_status_invalid_is_rejected(self):
        with self.assertRaises(ValueError):
            Opportunity(
                id=uuid4(),
                service_request_id=uuid4(),
                status="open",
                max_accesses=3,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_max_accesses_less_than_one_is_rejected(self):
        with self.assertRaises(ValueError):
            Opportunity(
                id=uuid4(),
                service_request_id=uuid4(),
                status=OpportunityStatus.OPEN,
                max_accesses=0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_max_accesses_non_int_is_rejected(self):
        with self.assertRaises(ValueError):
            Opportunity(
                id=uuid4(),
                service_request_id=uuid4(),
                status=OpportunityStatus.OPEN,
                max_accesses="3",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_max_accesses_bool_is_rejected(self):
        with self.assertRaises(ValueError):
            Opportunity(
                id=uuid4(),
                service_request_id=uuid4(),
                status=OpportunityStatus.OPEN,
                max_accesses=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_close_open_to_closed(self):
        opportunity = Opportunity(
            id=uuid4(),
            service_request_id=uuid4(),
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        opportunity.close()
        self.assertEqual(opportunity.status, OpportunityStatus.CLOSED)

    def test_close_non_open_is_rejected(self):
        opportunity = Opportunity(
            id=uuid4(),
            service_request_id=uuid4(),
            status=OpportunityStatus.CANCELLED,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            opportunity.close()

    def test_cancel_open_to_cancelled(self):
        opportunity = Opportunity(
            id=uuid4(),
            service_request_id=uuid4(),
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        opportunity.cancel()
        self.assertEqual(opportunity.status, OpportunityStatus.CANCELLED)

    def test_cancel_non_open_is_rejected(self):
        opportunity = Opportunity(
            id=uuid4(),
            service_request_id=uuid4(),
            status=OpportunityStatus.CLOSED,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            opportunity.cancel()


class OpportunityAccessDomainTests(SimpleTestCase):
    def test_valid_creation(self):
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )
        self.assertIsNotNone(access.id)

    def test_opportunity_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=None,
                provider_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )

    def test_opportunity_id_non_uuid_is_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityAccess(
                id=uuid4(),
                opportunity_id="invalid-uuid",
                provider_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )

    def test_provider_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=uuid4(),
                provider_id=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_provider_id_non_uuid_is_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=uuid4(),
                provider_id="invalid-uuid",
                created_at=datetime.now(timezone.utc),
            )


class MatchingResultDomainTests(SimpleTestCase):
    @staticmethod
    def _valid_provider() -> Provider:
        return Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Test Provider",
            slug="test-provider",
            description="desc",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def test_valid_matching_result(self):
        provider = self._valid_provider()
        res = MatchingResult(
            provider=provider,
            score=100,
            reasons=("technical_service_match",)
        )
        self.assertEqual(res.provider, provider)
        self.assertEqual(res.score, 100)
        self.assertEqual(res.reasons, ("technical_service_match",))

    def test_provider_must_be_provider_instance(self):
        with self.assertRaises(ValueError):
            MatchingResult(
                provider="not-a-provider-object",
                score=100,
                reasons=("technical_service_match",)
            )

    def test_score_below_zero_rejected(self):
        provider = self._valid_provider()
        with self.assertRaises(ValueError):
            MatchingResult(
                provider=provider,
                score=-1,
                reasons=("technical_service_match",)
            )

    def test_score_above_100_rejected(self):
        provider = self._valid_provider()
        with self.assertRaises(ValueError):
            MatchingResult(
                provider=provider,
                score=101,
                reasons=("technical_service_match",)
            )

    def test_score_non_int_rejected(self):
        provider = self._valid_provider()
        with self.assertRaises(ValueError):
            MatchingResult(
                provider=provider,
                score=99.5,
                reasons=("technical_service_match",)
            )

    def test_score_bool_rejected(self):
        provider = self._valid_provider()
        with self.assertRaises(ValueError):
            MatchingResult(
                provider=provider,
                score=True,
                reasons=("technical_service_match",)
            )

    def test_empty_reasons_rejected(self):
        provider = self._valid_provider()
        with self.assertRaises(ValueError):
            MatchingResult(
                provider=provider,
                score=100,
                reasons=()
            )

    def test_blank_reason_rejected(self):
        provider = self._valid_provider()
        with self.assertRaises(ValueError):
            MatchingResult(
                provider=provider,
                score=100,
                reasons=("   ",)
            )

    def test_reasons_normalized_by_stripping_whitespace(self):
        provider = self._valid_provider()
        res = MatchingResult(
            provider=provider,
            score=100,
            reasons=("  technical_service_match  ", " another_reason ")
        )
        self.assertEqual(res.reasons, ("technical_service_match", "another_reason"))

    def test_valid_score_boundary_zero(self):
        provider = self._valid_provider()
        res = MatchingResult(
            provider=provider,
            score=0,
            reasons=("some_reason",)
        )
        self.assertEqual(res.score, 0)

    def test_valid_score_boundary_100(self):
        provider = self._valid_provider()
        res = MatchingResult(
            provider=provider,
            score=100,
            reasons=("some_reason",)
        )
        self.assertEqual(res.score, 100)


class OpportunityInvitationDomainTests(SimpleTestCase):
    def test_valid_creation(self):
        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )
        self.assertIsNotNone(invitation.id)

    def test_id_invalid_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityInvitation(
                id=None,
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            OpportunityInvitation(
                id="invalid-uuid",
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )

    def test_opportunity_id_invalid_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityInvitation(
                id=uuid4(),
                opportunity_id=None,
                provider_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            OpportunityInvitation(
                id=uuid4(),
                opportunity_id="invalid-uuid",
                provider_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )

    def test_provider_id_invalid_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityInvitation(
                id=uuid4(),
                opportunity_id=uuid4(),
                provider_id=None,
                created_at=datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            OpportunityInvitation(
                id=uuid4(),
                opportunity_id=uuid4(),
                provider_id="invalid-uuid",
                created_at=datetime.now(timezone.utc),
            )

    def test_naive_created_at_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityInvitation(
                id=uuid4(),
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                created_at=datetime.now(),
            )


class OpportunityInterestDomainTests(SimpleTestCase):
    def test_valid_opportunity_interest_accepted(self):
        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )
        self.assertIsNotNone(interest.id)

    def test_invalid_id_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityInterest(
                id=None,
                invitation_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            OpportunityInterest(
                id="invalid-uuid",
                invitation_id=uuid4(),
                created_at=datetime.now(timezone.utc),
            )

    def test_invalid_invitation_id_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityInterest(
                id=uuid4(),
                invitation_id=None,
                created_at=datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            OpportunityInterest(
                id=uuid4(),
                invitation_id="invalid-uuid",
                created_at=datetime.now(timezone.utc),
            )

    def test_naive_created_at_rejected(self):
        with self.assertRaises(ValueError):
            OpportunityInterest(
                id=uuid4(),
                invitation_id=uuid4(),
                created_at=datetime.now(),
            )


class AccessEntitlementDecisionTests(SimpleTestCase):
    def test_allowed_true_accepted(self):
        decision = AccessEntitlementDecision(allowed=True, reason="test_allowed")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "test_allowed")

    def test_allowed_false_accepted(self):
        decision = AccessEntitlementDecision(allowed=False, reason="test_denied")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "test_denied")

    def test_non_bool_rejected(self):
        with self.assertRaises(ValueError):
            AccessEntitlementDecision(allowed=None, reason="test")
        with self.assertRaises(ValueError):
            AccessEntitlementDecision(allowed=1, reason="test")

    def test_invalid_reason_rejected(self):
        with self.assertRaises(ValueError):
            AccessEntitlementDecision(allowed=True, reason=None)
        with self.assertRaises(ValueError):
            AccessEntitlementDecision(allowed=True, reason=123)

    def test_empty_reason_rejected(self):
        with self.assertRaises(ValueError):
            AccessEntitlementDecision(allowed=True, reason="")
        with self.assertRaises(ValueError):
            AccessEntitlementDecision(allowed=True, reason="   ")

    def test_reason_stripped(self):
        decision = AccessEntitlementDecision(allowed=True, reason="  test_allowed  ")
        self.assertEqual(decision.reason, "test_allowed")


class RequestOpportunityAccessResultTests(SimpleTestCase):
    def test_allowed_with_access_is_valid(self):
        now = datetime.now(timezone.utc)
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            created_at=now,
        )
        decision = AccessEntitlementDecision(allowed=True, reason="test")
        result = RequestOpportunityAccessResult(decision=decision, access=access)
        self.assertEqual(result.access, access)

    def test_denied_with_no_access_is_valid(self):
        decision = AccessEntitlementDecision(allowed=False, reason="test")
        result = RequestOpportunityAccessResult(decision=decision, access=None)
        self.assertIsNone(result.access)

    def test_allowed_with_no_access_rejected(self):
        decision = AccessEntitlementDecision(allowed=True, reason="test")
        with self.assertRaises(ValueError):
            RequestOpportunityAccessResult(decision=decision, access=None)

    def test_denied_with_access_rejected(self):
        now = datetime.now(timezone.utc)
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            created_at=now,
        )
        decision = AccessEntitlementDecision(allowed=False, reason="test")
        with self.assertRaises(ValueError):
            RequestOpportunityAccessResult(decision=decision, access=access)

    def test_decision_immutability(self):
        decision = AccessEntitlementDecision(allowed=True, reason="test_allowed")
        with self.assertRaises(FrozenInstanceError):
            decision.allowed = False
        with self.assertRaises(FrozenInstanceError):
            decision.reason = "modified"

    def test_result_immutability(self):
        now = datetime.now(timezone.utc)
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            created_at=now,
        )
        decision = AccessEntitlementDecision(allowed=True, reason="test")
        result = RequestOpportunityAccessResult(decision=decision, access=access)
        with self.assertRaises(FrozenInstanceError):
            result.decision = AccessEntitlementDecision(allowed=False, reason="denied")
        with self.assertRaises(FrozenInstanceError):
            result.access = None


class MoneyTests(SimpleTestCase):
    def test_valid_zero_amount(self):
        m = Money(amount_minor=0, currency="BRL")
        self.assertEqual(m.amount_minor, 0)
        self.assertEqual(m.currency, "BRL")

    def test_valid_positive_amount(self):
        m = Money(amount_minor=2500, currency="USD")
        self.assertEqual(m.amount_minor, 2500)
        self.assertEqual(m.currency, "USD")

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            Money(amount_minor=-10, currency="BRL")

    def test_float_amount_rejected(self):
        with self.assertRaises(ValueError):
            Money(amount_minor=25.90, currency="BRL")

    def test_bool_amount_rejected(self):
        with self.assertRaises(ValueError):
            Money(amount_minor=True, currency="BRL")

    def test_none_amount_rejected(self):
        with self.assertRaises(ValueError):
            Money(amount_minor=None, currency="BRL")

    def test_currency_normalized(self):
        m1 = Money(amount_minor=100, currency="brl")
        self.assertEqual(m1.currency, "BRL")
        m2 = Money(amount_minor=100, currency=" USD ")
        self.assertEqual(m2.currency, "USD")

    def test_invalid_currency_rejected(self):
        with self.assertRaises(ValueError):
            Money(amount_minor=100, currency="")
        with self.assertRaises(ValueError):
            Money(amount_minor=100, currency="R$")
        with self.assertRaises(ValueError):
            Money(amount_minor=100, currency="REAL")
        with self.assertRaises(ValueError):
            Money(amount_minor=100, currency=123)
        with self.assertRaises(ValueError):
            Money(amount_minor=100, currency=None)

    def test_immutable_after_creation(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(FrozenInstanceError):
            m.amount_minor = 200
        with self.assertRaises(FrozenInstanceError):
            m.currency = "USD"


class OpportunityPricingQuoteTests(SimpleTestCase):
    def test_valid_quote(self):
        m = Money(amount_minor=2500, currency="BRL")
        quote = OpportunityPricingQuote(amount=m, reason="test_quote")
        self.assertEqual(quote.amount, m)
        self.assertEqual(quote.reason, "test_quote")

    def test_money_required(self):
        with self.assertRaises(ValueError):
            OpportunityPricingQuote(amount=None, reason="test")

    def test_invalid_reason_type_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            OpportunityPricingQuote(amount=m, reason=123)

    def test_empty_reason_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            OpportunityPricingQuote(amount=m, reason="")

    def test_whitespace_reason_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            OpportunityPricingQuote(amount=m, reason="   ")

    def test_reason_normalized(self):
        m = Money(amount_minor=100, currency="BRL")
        quote = OpportunityPricingQuote(amount=m, reason="  test_quote  ")
        self.assertEqual(quote.reason, "test_quote")

    def test_immutable_after_creation(self):
        m1 = Money(amount_minor=100, currency="BRL")
        m2 = Money(amount_minor=200, currency="USD")
        quote = OpportunityPricingQuote(amount=m1, reason="test")
        with self.assertRaises(FrozenInstanceError):
            quote.amount = m2
        with self.assertRaises(FrozenInstanceError):
            quote.reason = "modified"


class EconomicSettlementTests(SimpleTestCase):
    def test_valid_manual_settlement(self):
        m = Money(amount_minor=2500, currency="BRL")
        now = datetime.now(timezone.utc)
        es = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.MANUAL,
            amount=m,
            created_at=now,
        )
        self.assertEqual(es.amount, m)
        self.assertEqual(es.method, SettlementMethod.MANUAL)

    def test_valid_complimentary_zero_settlement(self):
        m = Money(amount_minor=0, currency="BRL")
        now = datetime.now(timezone.utc)
        es = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.COMPLIMENTARY,
            amount=m,
            created_at=now,
        )
        self.assertEqual(es.amount.amount_minor, 0)
        self.assertEqual(es.method, SettlementMethod.COMPLIMENTARY)

    def test_invalid_id_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=None,
                interest_id=uuid4(),
                method=SettlementMethod.MANUAL,
                amount=m,
                created_at=datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id="invalid-uuid",
                interest_id=uuid4(),
                method=SettlementMethod.MANUAL,
                amount=m,
                created_at=datetime.now(timezone.utc),
            )

    def test_invalid_interest_id_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=None,
                method=SettlementMethod.MANUAL,
                amount=m,
                created_at=datetime.now(timezone.utc),
            )

    def test_invalid_method_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method=None,
                amount=m,
                created_at=datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method="invalid-method",
                amount=m,
                created_at=datetime.now(timezone.utc),
            )

    def test_invalid_amount_type_rejected(self):
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method=SettlementMethod.MANUAL,
                amount=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_naive_created_at_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method=SettlementMethod.MANUAL,
                amount=m,
                created_at=datetime.now(),
            )

    def test_immutable_after_creation(self):
        m1 = Money(amount_minor=100, currency="BRL")
        m2 = Money(amount_minor=200, currency="BRL")
        now = datetime.now(timezone.utc)
        es = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.MANUAL,
            amount=m1,
            created_at=now,
        )
        with self.assertRaises(FrozenInstanceError):
            es.amount = m2

    def test_complimentary_positive_amount_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method=SettlementMethod.COMPLIMENTARY,
                amount=m,
                created_at=datetime.now(timezone.utc),
            )


class CreditWalletTests(SimpleTestCase):
    def test_valid_wallet(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.assertTrue(wallet.is_active)
        self.assertEqual(wallet.created_at, now)
        self.assertEqual(wallet.updated_at, now)

    def test_invalid_id_rejected(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            CreditWallet(
                id=None,
                organization_id=uuid4(),
                is_active=True,
                created_at=now,
                updated_at=now,
            )

    def test_invalid_organization_id_rejected(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            CreditWallet(
                id=uuid4(),
                organization_id="invalid-uuid",
                is_active=True,
                created_at=now,
                updated_at=now,
            )

    def test_non_bool_active_rejected(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            CreditWallet(
                id=uuid4(),
                organization_id=uuid4(),
                is_active=1,
                created_at=now,
                updated_at=now,
            )

    def test_naive_created_at_rejected(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            CreditWallet(
                id=uuid4(),
                organization_id=uuid4(),
                is_active=True,
                created_at=datetime.now(),
                updated_at=now,
            )

    def test_naive_updated_at_rejected(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            CreditWallet(
                id=uuid4(),
                organization_id=uuid4(),
                is_active=True,
                created_at=now,
                updated_at=datetime.now(),
            )

    def test_updated_at_before_created_at_rejected(self):
        now = datetime.now(timezone.utc)
        earlier = datetime.fromtimestamp(now.timestamp() - 10, timezone.utc)
        with self.assertRaises(ValueError):
            CreditWallet(
                id=uuid4(),
                organization_id=uuid4(),
                is_active=True,
                created_at=now,
                updated_at=earlier,
            )

    def test_activate_works(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        later = datetime.fromtimestamp(now.timestamp() + 5, timezone.utc)
        wallet.activate(later)
        self.assertTrue(wallet.is_active)
        self.assertEqual(wallet.updated_at, later)

    def test_deactivate_works(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        later = datetime.fromtimestamp(now.timestamp() + 5, timezone.utc)
        wallet.deactivate(later)
        self.assertFalse(wallet.is_active)
        self.assertEqual(wallet.updated_at, later)

    def test_activate_with_naive_time_rejected(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        with self.assertRaises(ValueError):
            wallet.activate(datetime.now())

    def test_deactivate_with_naive_time_rejected(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        with self.assertRaises(ValueError):
            wallet.deactivate(datetime.now())

    def test_activate_with_earlier_time_rejected(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        earlier = datetime.fromtimestamp(now.timestamp() - 5, timezone.utc)
        with self.assertRaises(ValueError):
            wallet.activate(earlier)

    def test_deactivate_with_earlier_time_rejected(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        earlier = datetime.fromtimestamp(now.timestamp() - 5, timezone.utc)
        with self.assertRaises(ValueError):
            wallet.deactivate(earlier)

    def test_monotonic_lifecycle_timestamp_enforcement(self):
        now = datetime.now(timezone.utc)
        created = datetime.fromtimestamp(now.timestamp() - 20, timezone.utc)
        updated = datetime.fromtimestamp(now.timestamp() - 10, timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=True,
            created_at=created,
            updated_at=updated,
        )

        # 1. activate rejects current_time earlier than updated_at
        earlier = datetime.fromtimestamp(updated.timestamp() - 1, timezone.utc)
        with self.assertRaises(ValueError):
            wallet.activate(earlier)

        # 2. deactivate rejects current_time earlier than updated_at
        with self.assertRaises(ValueError):
            wallet.deactivate(earlier)

        # 3. activate with current_time equal to updated_at remains valid
        wallet.activate(updated)
        self.assertEqual(wallet.updated_at, updated)

        # 4. deactivate with current_time equal to updated_at remains valid
        wallet.deactivate(updated)
        self.assertEqual(wallet.updated_at, updated)

        # 5. lifecycle with later timestamp updates updated_at normally
        later = datetime.fromtimestamp(updated.timestamp() + 5, timezone.utc)
        wallet.activate(later)
        self.assertEqual(wallet.updated_at, later)

    def test_no_balance_attribute_exists(self):
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.assertFalse(hasattr(wallet, "balance"))
        self.assertFalse(hasattr(wallet, "current_balance"))
        self.assertFalse(hasattr(wallet, "available_balance"))


class CreditLedgerEntryTests(SimpleTestCase):
    def test_valid_credit(self):
        now = datetime.now(timezone.utc)
        entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=uuid4(),
            direction=CreditLedgerDirection.CREDIT,
            units=100,
            reason="Campaign Bonus",
            reference="promo-123",
            created_at=now,
        )
        self.assertEqual(entry.direction, CreditLedgerDirection.CREDIT)
        self.assertEqual(entry.units, 100)
        self.assertEqual(entry.reason, "Campaign Bonus")
        self.assertEqual(entry.reference, "promo-123")

    def test_valid_debit(self):
        now = datetime.now(timezone.utc)
        entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=uuid4(),
            direction=CreditLedgerDirection.DEBIT,
            units=30,
            reason="Opportunity Access Charge",
            reference=None,
            created_at=now,
        )
        self.assertEqual(entry.direction, CreditLedgerDirection.DEBIT)
        self.assertEqual(entry.units, 30)
        self.assertEqual(entry.reason, "Opportunity Access Charge")
        self.assertIsNone(entry.reference)

    def test_invalid_id(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=None,
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=10,
                reason="Reason",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_invalid_wallet_id(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id="invalid-uuid",
                direction=CreditLedgerDirection.CREDIT,
                units=10,
                reason="Reason",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction="invalid-direction",
                units=10,
                reason="Reason",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_units_zero_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=0,
                reason="Reason",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_units_negative_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=-5,
                reason="Reason",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_units_float_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=10.5,
                reason="Reason",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_units_bool_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=True,
                reason="Reason",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_reason_empty_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=10,
                reason="",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_reason_whitespace_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=10,
                reason="   ",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )

    def test_reason_normalized(self):
        entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=uuid4(),
            direction=CreditLedgerDirection.CREDIT,
            units=10,
            reason="  Normalized Reason  ",
            reference=None,
            created_at=datetime.now(timezone.utc),
        )
        self.assertEqual(entry.reason, "Normalized Reason")

    def test_reference_normalized(self):
        entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=uuid4(),
            direction=CreditLedgerDirection.CREDIT,
            units=10,
            reason="Reason",
            reference="  Normalized Ref  ",
            created_at=datetime.now(timezone.utc),
        )
        self.assertEqual(entry.reference, "Normalized Ref")

    def test_empty_reference_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=10,
                reason="Reason",
                reference="   ",
                created_at=datetime.now(timezone.utc),
            )

    def test_naive_created_at_rejected(self):
        with self.assertRaises(ValueError):
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=uuid4(),
                direction=CreditLedgerDirection.CREDIT,
                units=10,
                reason="Reason",
                reference=None,
                created_at=datetime.now(),
            )

    def test_immutable_after_creation(self):
        entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=uuid4(),
            direction=CreditLedgerDirection.CREDIT,
            units=10,
            reason="Reason",
            reference=None,
            created_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(FrozenInstanceError):
            entry.units = 20
        with self.assertRaises(FrozenInstanceError):
            entry.reason = "Changed"
