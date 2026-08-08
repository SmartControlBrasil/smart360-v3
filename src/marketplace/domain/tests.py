from datetime import datetime, timezone
from uuid import uuid4

from django.test import SimpleTestCase

from src.marketplace.domain.entities import (
    MatchingResult,
    Opportunity,
    OpportunityAccess,
    OpportunityInvitation,
    OpportunityStatus,
    Provider,
    ProviderService,
    Service,
    ServiceCategory,
    ServiceRequest,
    ServiceRequestStatus,
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
