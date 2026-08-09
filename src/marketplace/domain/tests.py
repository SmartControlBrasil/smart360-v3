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
    CreditSettlementResult,
    ProtectedCommercialData,
    OpportunityPreview,
    OpportunityUnlockQuote,
    OpportunityUnlockPricingConfiguration,
    OpportunityUnlockResult,
    EconomicAcquisitionReconciliation,
    EconomicAcquisitionReconciliationIssue,
    UnlockedOpportunityContact,
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
            status=ServiceRequestStatus.QUALIFIED,
            raw_description="CLP nao inicia",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertEqual(service_request.title, "Manutencao de CLP")
        self.assertEqual(service_request.description, "CLP nao inicia")
        self.assertEqual(service_request.raw_description, "CLP nao inicia")
        self.assertEqual(service_request.status, ServiceRequestStatus.QUALIFIED)
        self.assertTrue(service_request.is_qualified_for_marketplace())

    def test_organization_id_none_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=None,
                service_id=uuid4(),
                title="Titulo",
                description="x",
                status=ServiceRequestStatus.QUALIFIED,
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

    def test_captured_need_without_service_id_is_valid(self):
        raw = "  Minha maquina CNC parou no eixo Y  "
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=None,
            title="",
            description="",
            status=ServiceRequestStatus.CAPTURED,
            raw_description=raw,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertIsNone(service_request.service_id)
        self.assertEqual(service_request.raw_description, raw)
        self.assertFalse(service_request.is_qualified_for_marketplace())

    def test_qualified_need_without_service_id_is_rejected(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=uuid4(),
                service_id=None,
                title="Titulo",
                description="x",
                status=ServiceRequestStatus.QUALIFIED,
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

    def test_captured_need_requires_raw_description(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=uuid4(),
                service_id=None,
                title="",
                description="",
                status=ServiceRequestStatus.CAPTURED,
                raw_description="   ",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_lifecycle_capture_to_qualifying_to_qualified(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=None,
            title="",
            description="",
            status=ServiceRequestStatus.CAPTURED,
            raw_description="Motor travando quando liga",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        service_request.start_qualification()
        self.assertEqual(service_request.status, ServiceRequestStatus.QUALIFYING)

        service_id = uuid4()
        service_request.qualify(
            service_id=service_id,
            title="Manutencao de motor",
            description="Motor travando",
        )

        self.assertEqual(service_request.status, ServiceRequestStatus.QUALIFIED)
        self.assertEqual(service_request.service_id, service_id)
        self.assertEqual(service_request.title, "Manutencao de motor")
        self.assertEqual(service_request.description, "Motor travando")
        self.assertTrue(service_request.is_qualified_for_marketplace())

    def test_invalid_lifecycle_transitions_are_rejected(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Titulo",
            description="x",
            status=ServiceRequestStatus.QUALIFIED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            service_request.start_qualification()
        with self.assertRaises(ValueError):
            service_request.qualify(service_id=uuid4())

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

    def test_protected_commercial_data_valid_combinations(self):
        # 1. Valid name + email
        data = ProtectedCommercialData(
            requester_name="  Marcelo Silva  ",
            requester_email="  marcelo@example.com  ",
            requester_phone=""
        )
        self.assertEqual(data.requester_name, "Marcelo Silva")
        self.assertEqual(data.requester_email, "marcelo@example.com")
        self.assertEqual(data.requester_phone, "")

        # 2. Valid name + phone
        data2 = ProtectedCommercialData(
            requester_name="Marcelo",
            requester_email="",
            requester_phone="  +55 11 99999-9999  "
        )
        self.assertEqual(data2.requester_name, "Marcelo")
        self.assertEqual(data2.requester_email, "")
        self.assertEqual(data2.requester_phone, "+55 11 99999-9999")

        # 3. Valid name + email + phone
        data3 = ProtectedCommercialData(
            requester_name="Marcelo",
            requester_email="marcelo@example.com",
            requester_phone="12345"
        )
        self.assertEqual(data3.requester_name, "Marcelo")
        self.assertEqual(data3.requester_email, "marcelo@example.com")
        self.assertEqual(data3.requester_phone, "12345")

    def test_protected_commercial_data_invalid(self):
        # Blank name rejected
        with self.assertRaises(ValueError):
            ProtectedCommercialData(
                requester_name="   ",
                requester_email="test@example.com",
                requester_phone=""
            )

        # No contact channels (both email and phone blank) rejected
        with self.assertRaises(ValueError):
            ProtectedCommercialData(
                requester_name="Marcelo",
                requester_email="  ",
                requester_phone=" "
            )

    def test_protected_commercial_data_immutability(self):
        data = ProtectedCommercialData(
            requester_name="Marcelo",
            requester_email="marcelo@example.com",
            requester_phone=""
        )
        with self.assertRaises(FrozenInstanceError):
            data.requester_name = "New Name"  # type: ignore

    def test_service_request_valid_with_contact_data(self):
        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="  Some Requester  ",
            requester_email="  req@example.com  ",
            requester_phone="  9999-8888  "
        )
        self.assertEqual(sr.requester_name, "Some Requester")
        self.assertEqual(sr.requester_email, "req@example.com")
        self.assertEqual(sr.requester_phone, "9999-8888")

    def test_service_request_allows_empty_legacy_contact_data(self):
        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="",
            requester_email="",
            requester_phone=""
        )
        self.assertEqual(sr.requester_name, "")
        self.assertEqual(sr.requester_email, "")
        self.assertEqual(sr.requester_phone, "")


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

    def test_captured_need_requires_raw_description(self):
        with self.assertRaises(ValueError):
            ServiceRequest(
                id=uuid4(),
                organization_id=uuid4(),
                service_id=None,
                title="",
                description="",
                status=ServiceRequestStatus.CAPTURED,
                raw_description="   ",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

    def test_lifecycle_capture_to_qualifying_to_qualified(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=None,
            title="",
            description="",
            status=ServiceRequestStatus.CAPTURED,
            raw_description="Motor travando quando liga",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        service_request.start_qualification()
        self.assertEqual(service_request.status, ServiceRequestStatus.QUALIFYING)

        service_id = uuid4()
        service_request.qualify(
            service_id=service_id,
            title="Manutencao de motor",
            description="Motor travando",
        )

        self.assertEqual(service_request.status, ServiceRequestStatus.QUALIFIED)
        self.assertEqual(service_request.service_id, service_id)
        self.assertEqual(service_request.title, "Manutencao de motor")
        self.assertEqual(service_request.description, "Motor travando")
        self.assertTrue(service_request.is_qualified_for_marketplace())

    def test_invalid_lifecycle_transitions_are_rejected(self):
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Titulo",
            description="x",
            status=ServiceRequestStatus.QUALIFIED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            service_request.start_qualification()
        with self.assertRaises(ValueError):
            service_request.qualify(service_id=uuid4())

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

    def test_pricing_metadata_is_preserved(self):
        config_id = uuid4()
        quote = OpportunityPricingQuote(
            amount=Money(amount_minor=100, currency="BRL"),
            reason="test_quote",
            pricing_source=" configured_policy ",
            pricing_configuration_id=config_id,
        )

        self.assertEqual(quote.pricing_source, "configured_policy")
        self.assertEqual(quote.pricing_configuration_id, config_id)

    def test_invalid_pricing_metadata_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            OpportunityPricingQuote(amount=m, reason="test", pricing_source="   ")
        with self.assertRaises(ValueError):
            OpportunityPricingQuote(amount=m, reason="test", pricing_configuration_id="not-a-uuid")

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

    def test_pricing_snapshot_metadata_is_preserved(self):
        config_id = uuid4()
        resolved_at = datetime.now(timezone.utc)
        settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.CREDIT,
            amount=Money(amount_minor=1500, currency="BRL"),
            created_at=resolved_at,
            pricing_source=" configured_policy ",
            pricing_configuration_id=config_id,
            pricing_resolved_at=resolved_at,
        )

        self.assertEqual(settlement.amount.amount_minor, 1500)
        self.assertEqual(settlement.amount.currency, "BRL")
        self.assertEqual(settlement.pricing_source, "configured_policy")
        self.assertEqual(settlement.pricing_configuration_id, config_id)
        self.assertEqual(settlement.pricing_resolved_at, resolved_at)

    def test_legacy_settlement_without_pricing_source_is_allowed(self):
        settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.CREDIT,
            amount=Money(amount_minor=1000, currency="BRL"),
            created_at=datetime.now(timezone.utc),
        )

        self.assertIsNone(settlement.pricing_source)
        self.assertIsNone(settlement.pricing_configuration_id)
        self.assertIsNone(settlement.pricing_resolved_at)

    def test_invalid_pricing_snapshot_metadata_rejected(self):
        m = Money(amount_minor=100, currency="BRL")
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method=SettlementMethod.CREDIT,
                amount=m,
                created_at=datetime.now(timezone.utc),
                pricing_source="   ",
            )
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method=SettlementMethod.CREDIT,
                amount=m,
                created_at=datetime.now(timezone.utc),
                pricing_configuration_id="not-a-uuid",
            )
        with self.assertRaises(ValueError):
            EconomicSettlement(
                id=uuid4(),
                interest_id=uuid4(),
                method=SettlementMethod.CREDIT,
                amount=m,
                created_at=datetime.now(timezone.utc),
                pricing_resolved_at=datetime.now(),
            )

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


class CreditSettlementResultTests(SimpleTestCase):
    def setUp(self):
        self.quote = OpportunityPricingQuote(
            amount=Money(2500, "BRL"),
            reason="Standard Price",
        )
        self.settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.CREDIT,
            amount=Money(2500, "BRL"),
            created_at=datetime.now(timezone.utc),
        )
        self.debit = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=uuid4(),
            direction=CreditLedgerDirection.DEBIT,
            units=25,
            reason="Debit",
            reference=None,
            created_at=datetime.now(timezone.utc),
        )

    def test_valid_positive_credit_result(self):
        res = CreditSettlementResult(
            pricing_quote=self.quote,
            credit_units=25,
            debit_entry=self.debit,
            settlement=self.settlement,
        )
        self.assertEqual(res.credit_units, 25)
        self.assertEqual(res.debit_entry.units, 25)
        self.assertEqual(res.settlement.method, SettlementMethod.CREDIT)

    def test_valid_zero_credit_result(self):
        settlement_zero = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.CREDIT,
            amount=Money(0, "BRL"),
            created_at=datetime.now(timezone.utc),
        )
        res = CreditSettlementResult(
            pricing_quote=self.quote,
            credit_units=0,
            debit_entry=None,
            settlement=settlement_zero,
        )
        self.assertEqual(res.credit_units, 0)
        self.assertIsNone(res.debit_entry)
        self.assertEqual(res.settlement.amount.amount_minor, 0)

    def test_invalid_credit_units_negative(self):
        with self.assertRaises(ValueError):
            CreditSettlementResult(
                pricing_quote=self.quote,
                credit_units=-5,
                debit_entry=self.debit,
                settlement=self.settlement,
            )

    def test_invalid_credit_units_float(self):
        with self.assertRaises(ValueError):
            CreditSettlementResult(
                pricing_quote=self.quote,
                credit_units=25.5,
                debit_entry=self.debit,
                settlement=self.settlement,
            )

    def test_invalid_credit_units_bool(self):
        with self.assertRaises(ValueError):
            CreditSettlementResult(
                pricing_quote=self.quote,
                credit_units=True,
                debit_entry=self.debit,
                settlement=self.settlement,
            )

    def test_positive_units_require_debit_entry(self):
        with self.assertRaises(ValueError):
            CreditSettlementResult(
                pricing_quote=self.quote,
                credit_units=25,
                debit_entry=None,
                settlement=self.settlement,
            )

    def test_zero_units_reject_debit_entry(self):
        with self.assertRaises(ValueError):
            CreditSettlementResult(
                pricing_quote=self.quote,
                credit_units=0,
                debit_entry=self.debit,
                settlement=self.settlement,
            )

    def test_debit_must_be_debit_direction(self):
        credit_entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=uuid4(),
            direction=CreditLedgerDirection.CREDIT,
            units=25,
            reason="Credit",
            reference=None,
            created_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            CreditSettlementResult(
                pricing_quote=self.quote,
                credit_units=25,
                debit_entry=credit_entry,
                settlement=self.settlement,
            )

    def test_settlement_must_use_credit_method(self):
        manual_settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=uuid4(),
            method=SettlementMethod.MANUAL,
            amount=Money(2500, "BRL"),
            created_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            CreditSettlementResult(
                pricing_quote=self.quote,
                credit_units=25,
                debit_entry=self.debit,
                settlement=manual_settlement,
            )

    def test_immutable_result(self):
        res = CreditSettlementResult(
            pricing_quote=self.quote,
            credit_units=25,
            debit_entry=self.debit,
            settlement=self.settlement,
        )
        with self.assertRaises(FrozenInstanceError):
            res.credit_units = 30

    def test_credit_method_value_is_exactly_credit(self):
        self.assertEqual(SettlementMethod.CREDIT.value, "credit")


class OpportunityPreviewDomainTests(SimpleTestCase):
    def test_valid_opportunity_preview_creation(self):
        opportunity_id = uuid4()
        service_request_id = uuid4()
        service_id = uuid4()
        now = datetime.now(timezone.utc)

        preview = OpportunityPreview(
            opportunity_id=opportunity_id,
            service_request_id=service_request_id,
            service_id=service_id,
            title="  CLP Manutencao  ",
            description="  CLP parou  ",
            status=OpportunityStatus.OPEN,
            created_at=now,
        )

        self.assertEqual(preview.opportunity_id, opportunity_id)
        self.assertEqual(preview.service_request_id, service_request_id)
        self.assertEqual(preview.service_id, service_id)
        self.assertEqual(preview.title, "CLP Manutencao")
        self.assertEqual(preview.description, "CLP parou")
        self.assertEqual(preview.status, OpportunityStatus.OPEN)
        self.assertEqual(preview.created_at, now)

    def test_opportunity_preview_excludes_pii(self):
        preview = OpportunityPreview(
            opportunity_id=uuid4(),
            service_request_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="Desc",
            status=OpportunityStatus.OPEN,
            created_at=datetime.now(timezone.utc),
        )
        self.assertFalse(hasattr(preview, "requester_name"))
        self.assertFalse(hasattr(preview, "requester_email"))
        self.assertFalse(hasattr(preview, "requester_phone"))

    def test_opportunity_preview_invalid_title(self):
        with self.assertRaises(ValueError):
            OpportunityPreview(
                opportunity_id=uuid4(),
                service_request_id=uuid4(),
                service_id=uuid4(),
                title="   ",
                description="Desc",
                status=OpportunityStatus.OPEN,
                created_at=datetime.now(timezone.utc),
            )

    def test_opportunity_preview_immutability(self):
        preview = OpportunityPreview(
            opportunity_id=uuid4(),
            service_request_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="Desc",
            status=OpportunityStatus.OPEN,
            created_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(FrozenInstanceError):
            preview.title = "New Title"  # type: ignore


class OpportunityUnlockQuoteDomainTests(SimpleTestCase):
    def test_valid_opportunity_unlock_quote_creation(self):
        opportunity_id = uuid4()
        provider_id = uuid4()
        price = Money(2500, "BRL")

        quote = OpportunityUnlockQuote(
            opportunity_id=opportunity_id,
            provider_id=provider_id,
            amount=price,
            quote_available=True,
            already_unlocked=False,
            reason="   Quote generated successfully  ",
        )

        self.assertEqual(quote.opportunity_id, opportunity_id)
        self.assertEqual(quote.provider_id, provider_id)
        self.assertEqual(quote.amount, price)
        self.assertTrue(quote.quote_available)
        self.assertFalse(quote.already_unlocked)
        self.assertEqual(quote.reason, "Quote generated successfully")

    def test_quote_unavailable_scenario(self):
        quote = OpportunityUnlockQuote(
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            amount=None,
            quote_available=False,
            already_unlocked=False,
            reason="No commercial pricing configured",
        )
        self.assertIsNone(quote.amount)
        self.assertFalse(quote.quote_available)

    def test_negative_amount_not_allowed(self):
        with self.assertRaises(ValueError):
            OpportunityUnlockQuote(
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                amount=Money(-100, "BRL"),
                quote_available=True,
                already_unlocked=False,
                reason="Invalid negative price",
            )

    def test_reason_empty_not_allowed(self):
        with self.assertRaises(ValueError):
            OpportunityUnlockQuote(
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                amount=None,
                quote_available=False,
                already_unlocked=False,
                reason="   ",
            )

    def test_quote_excludes_pii(self):
        quote = OpportunityUnlockQuote(
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            amount=None,
            quote_available=False,
            already_unlocked=False,
            reason="Safe Reason",
        )
        self.assertFalse(hasattr(quote, "requester_name"))
        self.assertFalse(hasattr(quote, "requester_email"))
        self.assertFalse(hasattr(quote, "requester_phone"))

    def test_quote_immutability(self):
        quote = OpportunityUnlockQuote(
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            amount=None,
            quote_available=False,
            already_unlocked=False,
            reason="Safe Reason",
        )
        with self.assertRaises(FrozenInstanceError):
            quote.reason = "Mutated"  # type: ignore


class EconomicAcquisitionReconciliationTests(SimpleTestCase):
    def test_consistent_result_has_no_issues(self):
        result = EconomicAcquisitionReconciliation(
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            consistent=True,
            issues=(),
            access_id=uuid4(),
            interest_id=uuid4(),
            settlement_id=uuid4(),
            debit_entry_ids=(uuid4(),),
        )

        self.assertTrue(result.consistent)
        self.assertEqual(result.issues, ())

    def test_inconsistent_result_requires_structured_issue(self):
        result = EconomicAcquisitionReconciliation(
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            consistent=False,
            issues=(EconomicAcquisitionReconciliationIssue.ACCESS_WITHOUT_SETTLEMENT,),
        )

        self.assertFalse(result.consistent)
        self.assertEqual(
            result.issues,
            (EconomicAcquisitionReconciliationIssue.ACCESS_WITHOUT_SETTLEMENT,),
        )

    def test_consistent_result_with_issues_is_rejected(self):
        with self.assertRaises(ValueError):
            EconomicAcquisitionReconciliation(
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                consistent=True,
                issues=(EconomicAcquisitionReconciliationIssue.ACCESS_WITHOUT_SETTLEMENT,),
            )

    def test_inconsistent_result_without_issue_is_rejected(self):
        with self.assertRaises(ValueError):
            EconomicAcquisitionReconciliation(
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                consistent=False,
                issues=(),
            )

    def test_invalid_issue_code_rejected(self):
        with self.assertRaises(ValueError):
            EconomicAcquisitionReconciliation(
                opportunity_id=uuid4(),
                provider_id=uuid4(),
                consistent=False,
                issues=("access_without_settlement",),
            )


class OpportunityUnlockResultDomainTests(SimpleTestCase):
    def test_valid_opportunity_unlock_result_creation(self):
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )
        settlement_id = uuid4()
        price = Money(2500, "BRL")

        result = OpportunityUnlockResult(
            access=access,
            already_unlocked=False,
            settlement_id=settlement_id,
            amount=price,
        )

        self.assertEqual(result.access, access)
        self.assertFalse(result.already_unlocked)
        self.assertEqual(result.settlement_id, settlement_id)
        self.assertEqual(result.amount, price)

    def test_quote_excludes_pii(self):
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )
        result = OpportunityUnlockResult(
            access=access,
            already_unlocked=False,
            settlement_id=None,
            amount=None,
        )
        self.assertFalse(hasattr(result, "requester_name"))
        self.assertFalse(hasattr(result, "requester_email"))
        self.assertFalse(hasattr(result, "requester_phone"))


class UnlockedOpportunityContactDomainTests(SimpleTestCase):
    def test_valid_unlocked_opportunity_contact_creation(self):
        opp_id = uuid4()
        sr_id = uuid4()
        contact = UnlockedOpportunityContact(
            opportunity_id=opp_id,
            service_request_id=sr_id,
            requester_name="  John Doe  ",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )

        self.assertEqual(contact.opportunity_id, opp_id)
        self.assertEqual(contact.service_request_id, sr_id)
        self.assertEqual(contact.requester_name, "John Doe")
        self.assertEqual(contact.requester_email, "john@example.com")
        self.assertEqual(contact.requester_phone, "+5511999999999")

    def test_tolerates_blank_legacy_values(self):
        # Ensure we can create contact with blank fields for legacy compatibility
        contact = UnlockedOpportunityContact(
            opportunity_id=uuid4(),
            service_request_id=uuid4(),
            requester_name="",
            requester_email="",
            requester_phone="",
        )
        self.assertEqual(contact.requester_name, "")
        self.assertEqual(contact.requester_email, "")
        self.assertEqual(contact.requester_phone, "")

    def test_allowlist_regression(self):
        contact = UnlockedOpportunityContact(
            opportunity_id=uuid4(),
            service_request_id=uuid4(),
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )
        # Structural check of fields
        from dataclasses import fields
        field_names = {f.name for f in fields(contact)}
        self.assertEqual(
            field_names,
            {"opportunity_id", "service_request_id", "requester_name", "requester_email", "requester_phone"}
        )

    def test_immutability(self):
        contact = UnlockedOpportunityContact(
            opportunity_id=uuid4(),
            service_request_id=uuid4(),
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )
        with self.assertRaises(FrozenInstanceError):
            contact.requester_name = "Jane"  # type: ignore


class OpportunityUnlockPricingConfigurationDomainTests(SimpleTestCase):
    def test_valid_configuration_requires_positive_money(self):
        now = datetime.now(timezone.utc)
        config = OpportunityUnlockPricingConfiguration(
            id=uuid4(),
            amount=Money(amount_minor=3500, currency="BRL"),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(config.amount.amount_minor, 3500)
        self.assertEqual(config.amount.currency, "BRL")
        self.assertTrue(config.is_active)

    def test_zero_or_negative_amount_rejected(self):
        now = datetime.now(timezone.utc)
        for amount_minor in (0, -1):
            with self.assertRaises(ValueError):
                OpportunityUnlockPricingConfiguration(
                    id=uuid4(),
                    amount=Money(amount_minor=amount_minor, currency="BRL"),
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
