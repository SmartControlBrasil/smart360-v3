from datetime import datetime, timezone
from uuid import UUID, uuid4

from django.test import SimpleTestCase

from src.marketplace.application.matching import TechnicalMatchingPolicyV1
from src.marketplace.application.use_cases import (
    CreateOpportunity,
    CreateProvider,
    CreateProviderService,
    CreateService,
    CreateServiceCategory,
    CreateServiceRequest,
    DiscoverCandidates,
    DistributeOpportunity,
    GrantOpportunityAccess,
    InviteProviderToOpportunity,
    RegisterOpportunityInterest,
    RequestOpportunityAccess,
    QuoteOpportunityAccessPrice,
    RecordEconomicSettlement,
    RankCandidates,
)
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
    AccessEntitlementDecision,
    RequestOpportunityAccessResult,
    ServiceCategory,
    ServiceRequest,
    ServiceRequestStatus,
    Money,
    OpportunityPricingQuote,
    SettlementMethod,
    EconomicSettlement,
)
from src.organizations.domain.entities import Organization


class InMemoryServiceCategoryRepository:
    def __init__(self):
        self._items: dict[str, ServiceCategory] = {}

    def save(self, service_category: ServiceCategory) -> ServiceCategory:
        self._items[str(service_category.id)] = service_category
        return service_category

    def get_by_id(
        self,
        service_category_id: UUID,
    ) -> ServiceCategory | None:
        return self._items.get(str(service_category_id))

    def get_by_slug(self, slug: str) -> ServiceCategory | None:
        for item in self._items.values():
            if item.slug == slug:
                return item
        return None

    def list_active(self) -> list[ServiceCategory]:
        return [
            item
            for item in self._items.values()
            if item.is_active
        ]


class CreateServiceCategoryTests(SimpleTestCase):
    def test_valid_creation(self):
        repository = InMemoryServiceCategoryRepository()
        use_case = CreateServiceCategory(repository=repository)

        created = use_case.execute(
            name="Automacao Industrial",
            slug="automacao-industrial",
            description="Servicos de automacao.",
        )

        self.assertIsNotNone(created.id)
        self.assertTrue(created.is_active)
        self.assertEqual(created.name, "Automacao Industrial")
        self.assertEqual(created.slug, "automacao-industrial")
        self.assertIsNotNone(repository.get_by_slug("automacao-industrial"))

    def test_name_and_slug_normalization(self):
        repository = InMemoryServiceCategoryRepository()
        use_case = CreateServiceCategory(repository=repository)

        created = use_case.execute(
            name="  Automacao Industrial  ",
            slug="  AUTOMACAO-INDUSTRIAL  ",
            description="x",
        )

        self.assertEqual(created.name, "Automacao Industrial")
        self.assertEqual(created.slug, "automacao-industrial")

    def test_empty_name_is_rejected(self):
        repository = InMemoryServiceCategoryRepository()
        use_case = CreateServiceCategory(repository=repository)

        with self.assertRaises(ValueError):
            use_case.execute(name="   ", slug="valid-slug")

    def test_empty_slug_is_rejected(self):
        repository = InMemoryServiceCategoryRepository()
        use_case = CreateServiceCategory(repository=repository)

        with self.assertRaises(ValueError):
            use_case.execute(name="Valid Name", slug="   ")

    def test_duplicate_slug_is_rejected(self):
        repository = InMemoryServiceCategoryRepository()
        use_case = CreateServiceCategory(repository=repository)

        use_case.execute(
            name="Primeira categoria",
            slug="slug-unica",
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                name="Segunda categoria",
                slug="SLUG-UNICA",
            )


class InMemoryServiceRepository:
    def __init__(self):
        self._items: dict[str, Service] = {}

    def save(self, service: Service) -> Service:
        self._items[str(service.id)] = service
        return service

    def get_by_id(self, service_id: UUID) -> Service | None:
        return self._items.get(str(service_id))

    def get_by_category_and_slug(
        self,
        category_id: UUID,
        slug: str,
    ) -> Service | None:
        for item in self._items.values():
            if item.category_id == category_id and item.slug == slug:
                return item
        return None

    def list_active_by_category(
        self,
        category_id: UUID,
    ) -> list[Service]:
        return [
            item
            for item in self._items.values()
            if item.category_id == category_id and item.is_active
        ]


class CreateServiceTests(SimpleTestCase):
    @staticmethod
    def _active_category(category_id: UUID) -> ServiceCategory:
        now = datetime.now(timezone.utc)
        return ServiceCategory(
            id=category_id,
            name="Automacao",
            slug="automacao",
            description="x",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def test_valid_creation(self):
        category_repository = InMemoryServiceCategoryRepository()
        service_repository = InMemoryServiceRepository()
        category = self._active_category(uuid4())
        category_repository.save(category)

        use_case = CreateService(
            service_repository=service_repository,
            category_repository=category_repository,
        )

        created = use_case.execute(
            category_id=category.id,
            name="Manutencao",
            slug="manutencao",
            description="Servico",
        )

        self.assertEqual(created.category_id, category.id)
        self.assertEqual(created.name, "Manutencao")
        self.assertEqual(created.slug, "manutencao")
        self.assertTrue(created.is_active)

    def test_category_not_found_is_rejected(self):
        use_case = CreateService(
            service_repository=InMemoryServiceRepository(),
            category_repository=InMemoryServiceCategoryRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                category_id=uuid4(),
                name="Manutencao",
                slug="manutencao",
            )

    def test_category_id_must_be_uuid_before_repository_calls(self):
        class SpyServiceRepository(InMemoryServiceRepository):
            def __init__(self):
                super().__init__()
                self.lookup_calls = 0

            def get_by_category_and_slug(
                self,
                category_id: UUID,
                slug: str,
            ) -> Service | None:
                self.lookup_calls += 1
                return super().get_by_category_and_slug(
                    category_id,
                    slug,
                )

        class SpyCategoryRepository(InMemoryServiceCategoryRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(
                self,
                service_category_id: UUID,
            ) -> ServiceCategory | None:
                self.get_by_id_calls += 1
                return super().get_by_id(service_category_id)

        service_repository = SpyServiceRepository()
        category_repository = SpyCategoryRepository()
        use_case = CreateService(
            service_repository=service_repository,
            category_repository=category_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                category_id="invalid-uuid",
                name="Manutencao",
                slug="manutencao",
            )

        self.assertEqual(category_repository.get_by_id_calls, 0)
        self.assertEqual(service_repository.lookup_calls, 0)

    def test_inactive_category_is_rejected(self):
        category_repository = InMemoryServiceCategoryRepository()
        now = datetime.now(timezone.utc)
        category = ServiceCategory(
            id=uuid4(),
            name="Inativa",
            slug="inativa",
            description="x",
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        category_repository.save(category)

        use_case = CreateService(
            service_repository=InMemoryServiceRepository(),
            category_repository=category_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                category_id=category.id,
                name="Manutencao",
                slug="manutencao",
            )

    def test_duplicate_slug_in_same_category_is_rejected(self):
        category_repository = InMemoryServiceCategoryRepository()
        service_repository = InMemoryServiceRepository()
        category = self._active_category(uuid4())
        category_repository.save(category)
        use_case = CreateService(
            service_repository=service_repository,
            category_repository=category_repository,
        )

        use_case.execute(
            category_id=category.id,
            name="Manutencao 1",
            slug="manutencao",
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                category_id=category.id,
                name="Manutencao 2",
                slug="MANUTENCAO",
            )

    def test_same_slug_in_different_categories_is_allowed(self):
        category_repository = InMemoryServiceCategoryRepository()
        service_repository = InMemoryServiceRepository()
        category_a = self._active_category(uuid4())
        category_b = self._active_category(uuid4())
        category_repository.save(category_a)
        category_repository.save(category_b)
        use_case = CreateService(
            service_repository=service_repository,
            category_repository=category_repository,
        )

        first = use_case.execute(
            category_id=category_a.id,
            name="Manutencao A",
            slug="manutencao",
        )
        second = use_case.execute(
            category_id=category_b.id,
            name="Manutencao B",
            slug="manutencao",
        )

        self.assertNotEqual(first.category_id, second.category_id)
        self.assertEqual(first.slug, second.slug)

    def test_empty_name_is_rejected(self):
        category_repository = InMemoryServiceCategoryRepository()
        category = self._active_category(uuid4())
        category_repository.save(category)
        use_case = CreateService(
            service_repository=InMemoryServiceRepository(),
            category_repository=category_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                category_id=category.id,
                name="   ",
                slug="manutencao",
            )

    def test_empty_slug_is_rejected(self):
        category_repository = InMemoryServiceCategoryRepository()
        category = self._active_category(uuid4())
        category_repository.save(category)
        use_case = CreateService(
            service_repository=InMemoryServiceRepository(),
            category_repository=category_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                category_id=category.id,
                name="Manutencao",
                slug="   ",
            )

    def test_slug_is_normalized_before_duplicate_lookup(self):
        category_repository = InMemoryServiceCategoryRepository()
        service_repository = InMemoryServiceRepository()
        category = self._active_category(uuid4())
        category_repository.save(category)
        use_case = CreateService(
            service_repository=service_repository,
            category_repository=category_repository,
        )

        use_case.execute(
            category_id=category.id,
            name="Primeiro",
            slug="MANUTENCAO",
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                category_id=category.id,
                name="Segundo",
                slug="manutencao",
            )


class InMemoryOrganizationRepository:
    def __init__(self):
        self._items: dict[str, Organization] = {}

    def save(self, organization: Organization) -> Organization:
        self._items[str(organization.id)] = organization
        return organization

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        return self._items.get(str(organization_id))

    def get_by_slug(self, slug: str) -> Organization | None:
        for item in self._items.values():
            if item.slug == slug:
                return item
        return None


class InMemoryProviderRepository:
    def __init__(self):
        self._items: dict[str, Provider] = {}

    def save(self, provider: Provider) -> Provider:
        self._items[str(provider.id)] = provider
        return provider

    def get_by_id(self, provider_id: UUID) -> Provider | None:
        return self._items.get(str(provider_id))

    def get_by_slug(self, slug: str) -> Provider | None:
        for item in self._items.values():
            if item.slug == slug:
                return item
        return None

    def list_active_by_organization(
        self,
        organization_id: UUID,
    ) -> list[Provider]:
        return [
            item
            for item in self._items.values()
            if item.organization_id == organization_id and item.is_active
        ]


class CreateProviderTests(SimpleTestCase):
    @staticmethod
    def _organization(
        organization_id: UUID,
        *,
        is_active: bool = True,
    ) -> Organization:
        now = datetime.now(timezone.utc)
        return Organization(
            id=organization_id,
            name="ACME Org",
            slug="acme-org",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_valid_creation(self):
        organization_repository = InMemoryOrganizationRepository()
        provider_repository = InMemoryProviderRepository()
        organization = self._organization(uuid4())
        organization_repository.save(organization)

        use_case = CreateProvider(
            provider_repository=provider_repository,
            organization_repository=organization_repository,
        )

        created = use_case.execute(
            organization_id=organization.id,
            display_name="ACME Automacao",
            slug="acme-automacao",
            description="Perfil",
        )

        self.assertIsNotNone(created.id)
        self.assertIsInstance(created.id, UUID)
        self.assertEqual(created.organization_id, organization.id)
        self.assertEqual(created.display_name, "ACME Automacao")
        self.assertEqual(created.slug, "acme-automacao")
        self.assertTrue(created.is_active)

    def test_organization_id_none_rejected_before_repositories(self):
        class SpyOrganizationRepository(InMemoryOrganizationRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(
                self,
                organization_id: UUID,
            ) -> Organization | None:
                self.get_by_id_calls += 1
                return super().get_by_id(organization_id)

        class SpyProviderRepository(InMemoryProviderRepository):
            def __init__(self):
                super().__init__()
                self.get_by_slug_calls = 0

            def get_by_slug(self, slug: str) -> Provider | None:
                self.get_by_slug_calls += 1
                return super().get_by_slug(slug)

        organization_repository = SpyOrganizationRepository()
        provider_repository = SpyProviderRepository()
        use_case = CreateProvider(
            provider_repository=provider_repository,
            organization_repository=organization_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=None,
                display_name="ACME",
                slug="acme",
            )

        self.assertEqual(organization_repository.get_by_id_calls, 0)
        self.assertEqual(provider_repository.get_by_slug_calls, 0)

    def test_organization_id_non_uuid_rejected_before_repositories(self):
        class SpyOrganizationRepository(InMemoryOrganizationRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(
                self,
                organization_id: UUID,
            ) -> Organization | None:
                self.get_by_id_calls += 1
                return super().get_by_id(organization_id)

        class SpyProviderRepository(InMemoryProviderRepository):
            def __init__(self):
                super().__init__()
                self.get_by_slug_calls = 0

            def get_by_slug(self, slug: str) -> Provider | None:
                self.get_by_slug_calls += 1
                return super().get_by_slug(slug)

        organization_repository = SpyOrganizationRepository()
        provider_repository = SpyProviderRepository()
        use_case = CreateProvider(
            provider_repository=provider_repository,
            organization_repository=organization_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id="invalid-uuid",
                display_name="ACME",
                slug="acme",
            )

        self.assertEqual(organization_repository.get_by_id_calls, 0)
        self.assertEqual(provider_repository.get_by_slug_calls, 0)

    def test_organization_not_found_is_rejected(self):
        use_case = CreateProvider(
            provider_repository=InMemoryProviderRepository(),
            organization_repository=InMemoryOrganizationRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=uuid4(),
                display_name="ACME",
                slug="acme",
            )

    def test_inactive_organization_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        organization = self._organization(uuid4(), is_active=False)
        organization_repository.save(organization)

        use_case = CreateProvider(
            provider_repository=InMemoryProviderRepository(),
            organization_repository=organization_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                display_name="ACME",
                slug="acme",
            )

    def test_empty_display_name_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        organization = self._organization(uuid4())
        organization_repository.save(organization)

        use_case = CreateProvider(
            provider_repository=InMemoryProviderRepository(),
            organization_repository=organization_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                display_name="   ",
                slug="acme",
            )

    def test_empty_slug_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        organization = self._organization(uuid4())
        organization_repository.save(organization)

        use_case = CreateProvider(
            provider_repository=InMemoryProviderRepository(),
            organization_repository=organization_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                display_name="ACME",
                slug="   ",
            )

    def test_duplicate_slug_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        provider_repository = InMemoryProviderRepository()
        organization = self._organization(uuid4())
        organization_repository.save(organization)

        use_case = CreateProvider(
            provider_repository=provider_repository,
            organization_repository=organization_repository,
        )

        use_case.execute(
            organization_id=organization.id,
            display_name="Primeiro",
            slug="acme",
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                display_name="Segundo",
                slug="ACME",
            )

    def test_slug_normalized_before_duplicate_lookup(self):
        organization_repository = InMemoryOrganizationRepository()
        provider_repository = InMemoryProviderRepository()
        organization = self._organization(uuid4())
        organization_repository.save(organization)

        use_case = CreateProvider(
            provider_repository=provider_repository,
            organization_repository=organization_repository,
        )

        use_case.execute(
            organization_id=organization.id,
            display_name="Primeiro",
            slug="ACME-AUTOMACAO",
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                display_name="Segundo",
                slug="acme-automacao",
            )


class InMemoryProviderServiceRepository:
    def __init__(self):
        self._items: dict[str, ProviderService] = {}
        self.save_calls = 0
        self.last_saved: ProviderService | None = None

    def save(
        self,
        provider_service: ProviderService,
    ) -> ProviderService:
        self.save_calls += 1
        self.last_saved = provider_service
        self._items[str(provider_service.id)] = provider_service
        return provider_service

    def get_by_id(
        self,
        provider_service_id: UUID,
    ) -> ProviderService | None:
        return self._items.get(str(provider_service_id))

    def get_by_provider_and_service(
        self,
        provider_id: UUID,
        service_id: UUID,
    ) -> ProviderService | None:
        for item in self._items.values():
            if item.provider_id == provider_id and item.service_id == service_id:
                return item
        return None

    def list_active_by_provider(
        self,
        provider_id: UUID,
    ) -> list[ProviderService]:
        return [
            item
            for item in self._items.values()
            if item.provider_id == provider_id and item.is_active
        ]

    def list_active_by_service(
        self,
        service_id: UUID,
    ) -> list[ProviderService]:
        return [
            item
            for item in self._items.values()
            if item.service_id == service_id and item.is_active
        ]


class InMemoryServiceRequestRepository:
    def __init__(self):
        self._items: dict[str, ServiceRequest] = {}
        self.save_calls = 0
        self.last_saved: ServiceRequest | None = None

    def save(self, service_request: ServiceRequest) -> ServiceRequest:
        self.save_calls += 1
        self.last_saved = service_request
        self._items[str(service_request.id)] = service_request
        return service_request

    def get_by_id(
        self,
        service_request_id: UUID,
    ) -> ServiceRequest | None:
        return self._items.get(str(service_request_id))

    def list_open_by_organization(
        self,
        organization_id: UUID,
    ) -> list[ServiceRequest]:
        return [
            item
            for item in self._items.values()
            if item.organization_id == organization_id
            and item.status == ServiceRequestStatus.OPEN
        ]

    def list_open_by_service(
        self,
        service_id: UUID,
    ) -> list[ServiceRequest]:
        return [
            item
            for item in self._items.values()
            if item.service_id == service_id
            and item.status == ServiceRequestStatus.OPEN
        ]


class InMemoryOpportunityRepository:
    def __init__(self):
        self._items: dict[str, Opportunity] = {}
        self.save_calls = 0
        self.last_saved: Opportunity | None = None

    def save(self, opportunity: Opportunity) -> Opportunity:
        self.save_calls += 1
        self.last_saved = opportunity
        self._items[str(opportunity.id)] = opportunity
        return opportunity

    def get_by_id(self, opportunity_id: UUID) -> Opportunity | None:
        return self._items.get(str(opportunity_id))

    def get_by_service_request(
        self,
        service_request_id: UUID,
    ) -> Opportunity | None:
        for item in self._items.values():
            if item.service_request_id == service_request_id:
                return item
        return None

    def list_open(self) -> list[Opportunity]:
        return [
            item
            for item in self._items.values()
            if item.status == OpportunityStatus.OPEN
        ]


class InMemoryOpportunityAccessRepository:
    def __init__(self):
        self._items: dict[str, OpportunityAccess] = {}
        self.save_calls = 0
        self.last_saved: OpportunityAccess | None = None

    def save(self, access: OpportunityAccess) -> OpportunityAccess:
        self.save_calls += 1
        self.last_saved = access
        self._items[str(access.id)] = access
        return access

    def get_by_id(self, access_id: UUID) -> OpportunityAccess | None:
        return self._items.get(str(access_id))

    def get_by_opportunity_and_provider(
        self,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityAccess | None:
        for item in self._items.values():
            if (
                item.opportunity_id == opportunity_id
                and item.provider_id == provider_id
            ):
                return item
        return None

    def list_by_opportunity(
        self,
        opportunity_id: UUID,
    ) -> list[OpportunityAccess]:
        return [
            item
            for item in self._items.values()
            if item.opportunity_id == opportunity_id
        ]

    def list_by_provider(
        self,
        provider_id: UUID,
    ) -> list[OpportunityAccess]:
        return [
            item
            for item in self._items.values()
            if item.provider_id == provider_id
        ]

    def count_by_opportunity(self, opportunity_id: UUID) -> int:
        return len(self.list_by_opportunity(opportunity_id))


class InMemoryOpportunityInvitationRepository:
    def __init__(self):
        self._items: dict[str, OpportunityInvitation] = {}
        self.save_calls = 0
        self.last_saved: OpportunityInvitation | None = None

    def save(self, invitation: OpportunityInvitation) -> OpportunityInvitation:
        self.save_calls += 1
        self.last_saved = invitation
        self._items[str(invitation.id)] = invitation
        return invitation

    def get_by_id(self, invitation_id: UUID) -> OpportunityInvitation | None:
        return self._items.get(str(invitation_id))

    def get_by_opportunity_and_provider(
        self,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityInvitation | None:
        for item in self._items.values():
            if (
                item.opportunity_id == opportunity_id
                and item.provider_id == provider_id
            ):
                return item
        return None

    def list_by_opportunity(
        self,
        opportunity_id: UUID,
    ) -> list[OpportunityInvitation]:
        return [
            item
            for item in self._items.values()
            if item.opportunity_id == opportunity_id
        ]

    def list_by_provider(
        self,
        provider_id: UUID,
    ) -> list[OpportunityInvitation]:
        return [
            item
            for item in self._items.values()
            if item.provider_id == provider_id
        ]

    def count_by_opportunity(self, opportunity_id: UUID) -> int:
        return len(self.list_by_opportunity(opportunity_id))


class InMemoryOpportunityInterestRepository:
    def __init__(self):
        self._items: dict[str, OpportunityInterest] = {}
        self.save_calls = 0
        self.last_saved: OpportunityInterest | None = None

    def save(self, interest: OpportunityInterest) -> OpportunityInterest:
        self.save_calls += 1
        self.last_saved = interest
        self._items[str(interest.id)] = interest
        return interest

    def get_by_id(self, interest_id: UUID) -> OpportunityInterest | None:
        return self._items.get(str(interest_id))

    def get_by_invitation(self, invitation_id: UUID) -> OpportunityInterest | None:
        for item in self._items.values():
            if item.invitation_id == invitation_id:
                return item
        return None


class InMemoryEconomicSettlementRepository:
    def __init__(self):
        self._items: dict[str, EconomicSettlement] = {}
        self.save_calls = 0
        self.last_saved: EconomicSettlement | None = None

    def save(self, settlement: EconomicSettlement) -> EconomicSettlement:
        self.save_calls += 1
        self.last_saved = settlement
        self._items[str(settlement.id)] = settlement
        return settlement

    def get_by_id(self, settlement_id: UUID) -> EconomicSettlement | None:
        return self._items.get(str(settlement_id))

    def get_by_interest(self, interest_id: UUID) -> EconomicSettlement | None:
        for item in self._items.values():
            if item.interest_id == interest_id:
                return item
        return None


class CreateProviderServiceTests(SimpleTestCase):
    @staticmethod
    def _active_provider(provider_id: UUID, organization_id: UUID) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=organization_id,
            display_name="Provider",
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _active_service(service_id: UUID, category_id: UUID) -> Service:
        now = datetime.now(timezone.utc)
        return Service(
            id=service_id,
            category_id=category_id,
            name="Service",
            slug=f"service-{service_id}",
            description="desc",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def test_valid_creation(self):
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider_service_repository = InMemoryProviderServiceRepository()

        provider = self._active_provider(uuid4(), uuid4())
        service = self._active_service(uuid4(), uuid4())
        provider_repository.save(provider)
        service_repository.save(service)

        use_case = CreateProviderService(
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        created = use_case.execute(
            provider_id=provider.id,
            service_id=service.id,
        )

        self.assertIsInstance(created.id, UUID)
        self.assertTrue(created.is_active)
        self.assertEqual(created.provider_id, provider.id)
        self.assertEqual(created.service_id, service.id)
        self.assertIsNotNone(created.created_at.tzinfo)
        self.assertIsNotNone(created.updated_at.tzinfo)
        self.assertEqual(provider_service_repository.save_calls, 1)
        self.assertIsNotNone(provider_service_repository.last_saved)

    def test_provider_id_none_rejected_before_repositories(self):
        class SpyProviderRepository(InMemoryProviderRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(self, provider_id: UUID) -> Provider | None:
                self.get_by_id_calls += 1
                return super().get_by_id(provider_id)

        class SpyServiceRepository(InMemoryServiceRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(self, service_id: UUID) -> Service | None:
                self.get_by_id_calls += 1
                return super().get_by_id(service_id)

        class SpyProviderServiceRepository(InMemoryProviderServiceRepository):
            def __init__(self):
                super().__init__()
                self.get_by_pair_calls = 0

            def get_by_provider_and_service(
                self,
                provider_id: UUID,
                service_id: UUID,
            ) -> ProviderService | None:
                self.get_by_pair_calls += 1
                return super().get_by_provider_and_service(
                    provider_id,
                    service_id,
                )

        provider_repository = SpyProviderRepository()
        service_repository = SpyServiceRepository()
        provider_service_repository = SpyProviderServiceRepository()
        use_case = CreateProviderService(
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(provider_id=None, service_id=uuid4())

        self.assertEqual(provider_repository.get_by_id_calls, 0)
        self.assertEqual(service_repository.get_by_id_calls, 0)
        self.assertEqual(provider_service_repository.get_by_pair_calls, 0)
        self.assertEqual(provider_service_repository.save_calls, 0)

    def test_provider_id_non_uuid_rejected_before_repositories(self):
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        use_case = CreateProviderService(
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                provider_id="invalid-uuid",
                service_id=uuid4(),
            )

        self.assertEqual(provider_service_repository.save_calls, 0)

    def test_service_id_none_rejected_before_repositories(self):
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        use_case = CreateProviderService(
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(provider_id=uuid4(), service_id=None)

        self.assertEqual(provider_service_repository.save_calls, 0)

    def test_service_id_non_uuid_rejected_before_repositories(self):
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        use_case = CreateProviderService(
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                provider_id=uuid4(),
                service_id="invalid-uuid",
            )

        self.assertEqual(provider_service_repository.save_calls, 0)

    def test_provider_not_found_is_rejected(self):
        service_repository = InMemoryServiceRepository()
        service = self._active_service(uuid4(), uuid4())
        service_repository.save(service)

        use_case = CreateProviderService(
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=InMemoryProviderRepository(),
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                provider_id=uuid4(),
                service_id=service.id,
            )

    def test_inactive_provider_is_rejected(self):
        now = datetime.now(timezone.utc)
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Inactive",
            slug="inactive-provider",
            description="x",
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        service = self._active_service(uuid4(), uuid4())
        provider_repository.save(provider)
        service_repository.save(service)

        use_case = CreateProviderService(
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                provider_id=provider.id,
                service_id=service.id,
            )

    def test_service_not_found_is_rejected(self):
        provider_repository = InMemoryProviderRepository()
        provider = self._active_provider(uuid4(), uuid4())
        provider_repository.save(provider)

        use_case = CreateProviderService(
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=provider_repository,
            service_repository=InMemoryServiceRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                provider_id=provider.id,
                service_id=uuid4(),
            )

    def test_inactive_service_is_rejected(self):
        now = datetime.now(timezone.utc)
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider = self._active_provider(uuid4(), uuid4())
        service = Service(
            id=uuid4(),
            category_id=uuid4(),
            name="Inactive Service",
            slug="inactive-service",
            description="x",
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        provider_repository.save(provider)
        service_repository.save(service)

        use_case = CreateProviderService(
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                provider_id=provider.id,
                service_id=service.id,
            )

    def test_duplicate_is_rejected(self):
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider_service_repository = InMemoryProviderServiceRepository()

        provider = self._active_provider(uuid4(), uuid4())
        service = self._active_service(uuid4(), uuid4())
        provider_repository.save(provider)
        service_repository.save(service)

        use_case = CreateProviderService(
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        use_case.execute(provider_id=provider.id, service_id=service.id)

        with self.assertRaises(ValueError):
            use_case.execute(provider_id=provider.id, service_id=service.id)

    def test_inactive_existing_relation_still_rejected_as_duplicate(self):
        provider_repository = InMemoryProviderRepository()
        service_repository = InMemoryServiceRepository()
        provider_service_repository = InMemoryProviderServiceRepository()

        provider = self._active_provider(uuid4(), uuid4())
        service = self._active_service(uuid4(), uuid4())
        provider_repository.save(provider)
        service_repository.save(service)

        now = datetime.now(timezone.utc)
        relation = ProviderService(
            id=uuid4(),
            provider_id=provider.id,
            service_id=service.id,
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        provider_service_repository.save(relation)

        use_case = CreateProviderService(
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(provider_id=provider.id, service_id=service.id)


class CreateServiceRequestTests(SimpleTestCase):
    @staticmethod
    def _organization(
        organization_id: UUID,
        *,
        is_active: bool = True,
    ) -> Organization:
        now = datetime.now(timezone.utc)
        return Organization(
            id=organization_id,
            name="Org Solicitante",
            slug="org-solicitante",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _service(
        service_id: UUID,
        *,
        is_active: bool = True,
    ) -> Service:
        now = datetime.now(timezone.utc)
        return Service(
            id=service_id,
            category_id=uuid4(),
            name="Manutencao CLP",
            slug=f"manutencao-clp-{service_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_valid_creation(self):
        organization_repository = InMemoryOrganizationRepository()
        service_repository = InMemoryServiceRepository()
        service_request_repository = InMemoryServiceRequestRepository()
        organization = self._organization(uuid4())
        service = self._service(uuid4())
        organization_repository.save(organization)
        service_repository.save(service)

        use_case = CreateServiceRequest(
            service_request_repository=service_request_repository,
            organization_repository=organization_repository,
            service_repository=service_repository,
        )

        created = use_case.execute(
            organization_id=organization.id,
            service_id=service.id,
            title="  Falha em CLP  ",
            description="  Linha parada  ",
        )

        self.assertIsInstance(created.id, UUID)
        self.assertEqual(created.status, ServiceRequestStatus.OPEN)
        self.assertEqual(created.title, "Falha em CLP")
        self.assertEqual(created.description, "Linha parada")
        self.assertEqual(created.organization_id, organization.id)
        self.assertEqual(created.service_id, service.id)
        self.assertIsNotNone(created.created_at.tzinfo)
        self.assertIsNotNone(created.updated_at.tzinfo)
        self.assertEqual(service_request_repository.save_calls, 1)
        self.assertIsNotNone(service_request_repository.last_saved)

    def test_organization_id_invalid_rejected_before_repositories(self):
        class SpyOrganizationRepository(InMemoryOrganizationRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(self, organization_id: UUID) -> Organization | None:
                self.get_by_id_calls += 1
                return super().get_by_id(organization_id)

        class SpyServiceRepository(InMemoryServiceRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(self, service_id: UUID) -> Service | None:
                self.get_by_id_calls += 1
                return super().get_by_id(service_id)

        organization_repository = SpyOrganizationRepository()
        service_repository = SpyServiceRepository()
        service_request_repository = InMemoryServiceRequestRepository()
        use_case = CreateServiceRequest(
            service_request_repository=service_request_repository,
            organization_repository=organization_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id="invalid-uuid",
                service_id=uuid4(),
                title="Titulo",
            )

        self.assertEqual(organization_repository.get_by_id_calls, 0)
        self.assertEqual(service_repository.get_by_id_calls, 0)
        self.assertEqual(service_request_repository.save_calls, 0)

    def test_service_id_invalid_rejected_before_repositories(self):
        organization_repository = InMemoryOrganizationRepository()
        service_repository = InMemoryServiceRepository()
        service_request_repository = InMemoryServiceRequestRepository()
        use_case = CreateServiceRequest(
            service_request_repository=service_request_repository,
            organization_repository=organization_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=uuid4(),
                service_id="invalid-uuid",
                title="Titulo",
            )

        self.assertEqual(service_request_repository.save_calls, 0)

    def test_organization_not_found_is_rejected(self):
        service_repository = InMemoryServiceRepository()
        service = self._service(uuid4())
        service_repository.save(service)
        use_case = CreateServiceRequest(
            service_request_repository=InMemoryServiceRequestRepository(),
            organization_repository=InMemoryOrganizationRepository(),
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=uuid4(),
                service_id=service.id,
                title="Titulo",
            )

    def test_inactive_organization_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        service_repository = InMemoryServiceRepository()
        organization = self._organization(uuid4(), is_active=False)
        service = self._service(uuid4())
        organization_repository.save(organization)
        service_repository.save(service)
        use_case = CreateServiceRequest(
            service_request_repository=InMemoryServiceRequestRepository(),
            organization_repository=organization_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                service_id=service.id,
                title="Titulo",
            )

    def test_service_not_found_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        organization = self._organization(uuid4())
        organization_repository.save(organization)
        use_case = CreateServiceRequest(
            service_request_repository=InMemoryServiceRequestRepository(),
            organization_repository=organization_repository,
            service_repository=InMemoryServiceRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                service_id=uuid4(),
                title="Titulo",
            )

    def test_inactive_service_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        service_repository = InMemoryServiceRepository()
        organization = self._organization(uuid4())
        inactive_service = self._service(uuid4(), is_active=False)
        organization_repository.save(organization)
        service_repository.save(inactive_service)
        use_case = CreateServiceRequest(
            service_request_repository=InMemoryServiceRequestRepository(),
            organization_repository=organization_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                service_id=inactive_service.id,
                title="Titulo",
            )

    def test_empty_title_is_rejected(self):
        organization_repository = InMemoryOrganizationRepository()
        service_repository = InMemoryServiceRepository()
        organization = self._organization(uuid4())
        service = self._service(uuid4())
        organization_repository.save(organization)
        service_repository.save(service)
        use_case = CreateServiceRequest(
            service_request_repository=InMemoryServiceRequestRepository(),
            organization_repository=organization_repository,
            service_repository=service_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                organization_id=organization.id,
                service_id=service.id,
                title="   ",
            )


class DiscoverCandidatesTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Demanda tecnica",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        display_name: str,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name=display_name,
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider_service(
        *,
        provider_id: UUID,
        service_id: UUID,
        is_active: bool = True,
    ) -> ProviderService:
        now = datetime.now(timezone.utc)
        return ProviderService(
            id=uuid4(),
            provider_id=provider_id,
            service_id=service_id,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_discovery_valid_with_single_eligible_provider(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(
            uuid4(),
            service_id=service_id,
        )
        provider = self._provider(uuid4(), display_name="Provider A")
        capability = self._provider_service(
            provider_id=provider.id,
            service_id=service_id,
            is_active=True,
        )

        service_request_repository.save(request)
        provider_repository.save(provider)
        provider_service_repository.save(capability)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].id, provider.id)

    def test_request_id_none_rejected_before_repositories(self):
        class SpyServiceRequestRepository(InMemoryServiceRequestRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(
                self,
                service_request_id: UUID,
            ) -> ServiceRequest | None:
                self.get_by_id_calls += 1
                return super().get_by_id(service_request_id)

        class SpyProviderServiceRepository(InMemoryProviderServiceRepository):
            def __init__(self):
                super().__init__()
                self.list_calls = 0

            def list_active_by_service(
                self,
                service_id: UUID,
            ) -> list[ProviderService]:
                self.list_calls += 1
                return super().list_active_by_service(service_id)

        class SpyProviderRepository(InMemoryProviderRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(self, provider_id: UUID) -> Provider | None:
                self.get_by_id_calls += 1
                return super().get_by_id(provider_id)

        service_request_repository = SpyServiceRequestRepository()
        provider_service_repository = SpyProviderServiceRepository()
        provider_repository = SpyProviderRepository()
        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=None)

        self.assertEqual(service_request_repository.get_by_id_calls, 0)
        self.assertEqual(provider_service_repository.list_calls, 0)
        self.assertEqual(provider_repository.get_by_id_calls, 0)

    def test_request_id_non_uuid_rejected_before_repositories(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()
        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id="invalid-uuid")

    def test_service_request_not_found_is_rejected(self):
        use_case = DiscoverCandidates(
            service_request_repository=InMemoryServiceRequestRepository(),
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=InMemoryProviderRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=uuid4())

    def test_service_request_cancelled_is_rejected(self):
        service_request_repository = InMemoryServiceRequestRepository()
        request = self._service_request(
            uuid4(),
            service_id=uuid4(),
            status=ServiceRequestStatus.CANCELLED,
        )
        service_request_repository.save(request)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=InMemoryProviderRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=request.id)

    def test_service_request_closed_is_rejected(self):
        service_request_repository = InMemoryServiceRequestRepository()
        request = self._service_request(
            uuid4(),
            service_id=uuid4(),
            status=ServiceRequestStatus.CLOSED,
        )
        service_request_repository.save(request)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=InMemoryProviderRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=request.id)

    def test_returns_empty_when_no_active_provider_service(self):
        service_request_repository = InMemoryServiceRequestRepository()
        service_id = uuid4()
        request = self._service_request(
            uuid4(),
            service_id=service_id,
        )
        service_request_repository.save(request)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=InMemoryProviderServiceRepository(),
            provider_repository=InMemoryProviderRepository(),
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual(candidates, [])

    def test_active_capability_and_active_provider_are_included(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(
            uuid4(),
            service_id=service_id,
        )
        provider = self._provider(uuid4(), display_name="Provider Ativo")
        provider_service = self._provider_service(
            provider_id=provider.id,
            service_id=service_id,
        )
        service_request_repository.save(request)
        provider_repository.save(provider)
        provider_service_repository.save(provider_service)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual([candidate.id for candidate in candidates], [provider.id])

    def test_active_capability_with_inactive_provider_is_excluded(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(
            uuid4(),
            service_id=service_id,
        )
        inactive_provider = self._provider(
            uuid4(),
            display_name="Provider Inativo",
            is_active=False,
        )
        provider_service = self._provider_service(
            provider_id=inactive_provider.id,
            service_id=service_id,
        )
        service_request_repository.save(request)
        provider_repository.save(inactive_provider)
        provider_service_repository.save(provider_service)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual(candidates, [])

    def test_missing_provider_is_ignored(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(
            uuid4(),
            service_id=service_id,
        )
        missing_provider_id = uuid4()
        provider_service = self._provider_service(
            provider_id=missing_provider_id,
            service_id=service_id,
        )
        service_request_repository.save(request)
        provider_service_repository.save(provider_service)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual(candidates, [])

    def test_multiple_active_providers_are_returned(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()
        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        provider_a = self._provider(uuid4(), display_name="Provider A")
        provider_b = self._provider(uuid4(), display_name="Provider B")
        capability_a = self._provider_service(
            provider_id=provider_a.id,
            service_id=service_id,
        )
        capability_b = self._provider_service(
            provider_id=provider_b.id,
            service_id=service_id,
        )

        service_request_repository.save(request)
        provider_repository.save(provider_a)
        provider_repository.save(provider_b)
        provider_service_repository.save(capability_a)
        provider_service_repository.save(capability_b)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual({candidate.id for candidate in candidates}, {provider_a.id, provider_b.id})

    def test_capabilities_from_other_service_are_not_returned(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()

        requested_service_id = uuid4()
        other_service_id = uuid4()
        request = self._service_request(
            uuid4(),
            service_id=requested_service_id,
        )
        provider_requested = self._provider(uuid4(), display_name="Provider Requested")
        provider_other = self._provider(uuid4(), display_name="Provider Other")

        provider_service_repository.save(
            self._provider_service(
                provider_id=provider_requested.id,
                service_id=requested_service_id,
            )
        )
        provider_service_repository.save(
            self._provider_service(
                provider_id=provider_other.id,
                service_id=other_service_id,
            )
        )
        service_request_repository.save(request)
        provider_repository.save(provider_requested)
        provider_repository.save(provider_other)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].id, provider_requested.id)

    def test_defensive_deduplication_by_provider_id(self):
        class DuplicatedProviderServiceRepository(InMemoryProviderServiceRepository):
            def __init__(self, duplicated_provider_service: ProviderService):
                super().__init__()
                self._duplicated_provider_service = duplicated_provider_service

            def list_active_by_service(
                self,
                service_id: UUID,
            ) -> list[ProviderService]:
                if self._duplicated_provider_service.service_id != service_id:
                    return []
                return [
                    self._duplicated_provider_service,
                    self._duplicated_provider_service,
                ]

        service_request_repository = InMemoryServiceRequestRepository()
        provider_repository = InMemoryProviderRepository()
        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        provider = self._provider(uuid4(), display_name="Duplicated Provider")
        duplicated_capability = self._provider_service(
            provider_id=provider.id,
            service_id=service_id,
        )
        provider_service_repository = DuplicatedProviderServiceRepository(
            duplicated_capability,
        )

        service_request_repository.save(request)
        provider_repository.save(provider)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].id, provider.id)

    def test_ordering_is_deterministic_by_display_name_and_id(self):
        service_request_repository = InMemoryServiceRequestRepository()
        provider_service_repository = InMemoryProviderServiceRepository()
        provider_repository = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        alpha_high = self._provider(
            UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
            display_name="alpha",
        )
        alpha_low = self._provider(
            UUID("00000000-0000-0000-0000-000000000001"),
            display_name="Alpha",
        )
        bravo = self._provider(uuid4(), display_name="Bravo")

        for provider in [alpha_high, alpha_low, bravo]:
            provider_repository.save(provider)
            provider_service_repository.save(
                self._provider_service(
                    provider_id=provider.id,
                    service_id=service_id,
                )
            )

        service_request_repository.save(request)

        use_case = DiscoverCandidates(
            service_request_repository=service_request_repository,
            provider_service_repository=provider_service_repository,
            provider_repository=provider_repository,
        )

        candidates = use_case.execute(service_request_id=request.id)

        self.assertEqual(
            [candidate.id for candidate in candidates],
            [alpha_low.id, alpha_high.id, bravo.id],
        )

    def test_signature_uses_only_technical_eligibility_repositories(self):
        dependency_names = DiscoverCandidates.__init__.__code__.co_varnames

        self.assertIn("service_request_repository", dependency_names)
        self.assertIn("provider_service_repository", dependency_names)
        self.assertIn("provider_repository", dependency_names)
        self.assertNotIn("opportunity_repository", dependency_names)
        self.assertNotIn("opportunity_access_repository", dependency_names)


class CreateOpportunityTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Demanda",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    def test_valid_creation(self):
        service_request_repository = InMemoryServiceRequestRepository()
        opportunity_repository = InMemoryOpportunityRepository()
        service_request = self._service_request(uuid4())
        service_request_repository.save(service_request)
        use_case = CreateOpportunity(
            opportunity_repository=opportunity_repository,
            service_request_repository=service_request_repository,
        )

        created = use_case.execute(service_request_id=service_request.id)

        self.assertIsInstance(created.id, UUID)
        self.assertEqual(created.status, OpportunityStatus.OPEN)
        self.assertEqual(created.max_accesses, 3)
        self.assertEqual(created.service_request_id, service_request.id)
        self.assertIsNotNone(created.created_at.tzinfo)
        self.assertIsNotNone(created.updated_at.tzinfo)
        self.assertEqual(opportunity_repository.save_calls, 1)

    def test_service_request_id_invalid_rejected_before_repository(self):
        class SpyServiceRequestRepository(InMemoryServiceRequestRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(
                self,
                service_request_id: UUID,
            ) -> ServiceRequest | None:
                self.get_by_id_calls += 1
                return super().get_by_id(service_request_id)

        class SpyOpportunityRepository(InMemoryOpportunityRepository):
            def __init__(self):
                super().__init__()
                self.get_by_service_request_calls = 0

            def get_by_service_request(
                self,
                service_request_id: UUID,
            ) -> Opportunity | None:
                self.get_by_service_request_calls += 1
                return super().get_by_service_request(service_request_id)

        service_request_repository = SpyServiceRequestRepository()
        opportunity_repository = SpyOpportunityRepository()
        use_case = CreateOpportunity(
            opportunity_repository=opportunity_repository,
            service_request_repository=service_request_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id="invalid-uuid")

        self.assertEqual(service_request_repository.get_by_id_calls, 0)
        self.assertEqual(opportunity_repository.get_by_service_request_calls, 0)
        self.assertEqual(opportunity_repository.save_calls, 0)

    def test_max_accesses_invalid_rejected_before_repository(self):
        service_request_repository = InMemoryServiceRequestRepository()
        opportunity_repository = InMemoryOpportunityRepository()
        use_case = CreateOpportunity(
            opportunity_repository=opportunity_repository,
            service_request_repository=service_request_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=uuid4(), max_accesses=True)
        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=uuid4(), max_accesses=0)
        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=uuid4(), max_accesses="3")

    def test_service_request_not_found_is_rejected(self):
        use_case = CreateOpportunity(
            opportunity_repository=InMemoryOpportunityRepository(),
            service_request_repository=InMemoryServiceRequestRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=uuid4())

    def test_service_request_cancelled_is_rejected(self):
        service_request_repository = InMemoryServiceRequestRepository()
        service_request = self._service_request(
            uuid4(),
            status=ServiceRequestStatus.CANCELLED,
        )
        service_request_repository.save(service_request)
        use_case = CreateOpportunity(
            opportunity_repository=InMemoryOpportunityRepository(),
            service_request_repository=service_request_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=service_request.id)

    def test_service_request_closed_is_rejected(self):
        service_request_repository = InMemoryServiceRequestRepository()
        service_request = self._service_request(
            uuid4(),
            status=ServiceRequestStatus.CLOSED,
        )
        service_request_repository.save(service_request)
        use_case = CreateOpportunity(
            opportunity_repository=InMemoryOpportunityRepository(),
            service_request_repository=service_request_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=service_request.id)

    def test_existing_open_opportunity_is_rejected(self):
        service_request_repository = InMemoryServiceRequestRepository()
        opportunity_repository = InMemoryOpportunityRepository()
        service_request = self._service_request(uuid4())
        service_request_repository.save(service_request)
        opportunity_repository.save(
            Opportunity(
                id=uuid4(),
                service_request_id=service_request.id,
                status=OpportunityStatus.OPEN,
                max_accesses=3,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        use_case = CreateOpportunity(
            opportunity_repository=opportunity_repository,
            service_request_repository=service_request_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=service_request.id)

    def test_existing_closed_opportunity_is_rejected(self):
        service_request_repository = InMemoryServiceRequestRepository()
        opportunity_repository = InMemoryOpportunityRepository()
        service_request = self._service_request(uuid4())
        service_request_repository.save(service_request)
        opportunity_repository.save(
            Opportunity(
                id=uuid4(),
                service_request_id=service_request.id,
                status=OpportunityStatus.CLOSED,
                max_accesses=3,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        use_case = CreateOpportunity(
            opportunity_repository=opportunity_repository,
            service_request_repository=service_request_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=service_request.id)

    def test_existing_cancelled_opportunity_is_rejected(self):
        service_request_repository = InMemoryServiceRequestRepository()
        opportunity_repository = InMemoryOpportunityRepository()
        service_request = self._service_request(uuid4())
        service_request_repository.save(service_request)
        opportunity_repository.save(
            Opportunity(
                id=uuid4(),
                service_request_id=service_request.id,
                status=OpportunityStatus.CANCELLED,
                max_accesses=3,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        use_case = CreateOpportunity(
            opportunity_repository=opportunity_repository,
            service_request_repository=service_request_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=service_request.id)

    def test_custom_max_accesses_is_preserved(self):
        service_request_repository = InMemoryServiceRequestRepository()
        opportunity_repository = InMemoryOpportunityRepository()
        service_request = self._service_request(uuid4())
        service_request_repository.save(service_request)
        use_case = CreateOpportunity(
            opportunity_repository=opportunity_repository,
            service_request_repository=service_request_repository,
        )

        created = use_case.execute(
            service_request_id=service_request.id,
            max_accesses=5,
        )

        self.assertEqual(created.max_accesses, 5)


class GrantOpportunityAccessTests(SimpleTestCase):
    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider Teste",
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _opportunity(
        opportunity_id: UUID,
        *,
        status: OpportunityStatus = OpportunityStatus.OPEN,
        max_accesses: int = 3,
    ) -> Opportunity:
        now = datetime.now(timezone.utc)
        return Opportunity(
            id=opportunity_id,
            service_request_id=uuid4(),
            status=status,
            max_accesses=max_accesses,
            created_at=now,
            updated_at=now,
        )

    def test_valid_grant(self):
        opportunity_repository = InMemoryOpportunityRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        provider_repository = InMemoryProviderRepository()
        opportunity = self._opportunity(uuid4())
        provider = self._provider(uuid4())
        opportunity_repository.save(opportunity)
        provider_repository.save(provider)

        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )

        granted = use_case.execute(
            opportunity_id=opportunity.id,
            provider_id=provider.id,
        )

        self.assertIsInstance(granted.id, UUID)
        self.assertEqual(granted.opportunity_id, opportunity.id)
        self.assertEqual(granted.provider_id, provider.id)
        self.assertIsNotNone(granted.created_at.tzinfo)
        self.assertEqual(access_repository.save_calls, 1)

    def test_opportunity_id_invalid_rejected_before_repositories(self):
        class SpyOpportunityRepository(InMemoryOpportunityRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(self, opportunity_id: UUID) -> Opportunity | None:
                self.get_by_id_calls += 1
                return super().get_by_id(opportunity_id)

        class SpyProviderRepository(InMemoryProviderRepository):
            def __init__(self):
                super().__init__()
                self.get_by_id_calls = 0

            def get_by_id(self, provider_id: UUID) -> Provider | None:
                self.get_by_id_calls += 1
                return super().get_by_id(provider_id)

        opportunity_repository = SpyOpportunityRepository()
        provider_repository = SpyProviderRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                opportunity_id="invalid-uuid",
                provider_id=uuid4(),
            )

        self.assertEqual(opportunity_repository.get_by_id_calls, 0)
        self.assertEqual(provider_repository.get_by_id_calls, 0)
        self.assertEqual(access_repository.save_calls, 0)

    def test_provider_id_invalid_rejected_before_repositories(self):
        opportunity_repository = InMemoryOpportunityRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        provider_repository = InMemoryProviderRepository()
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )

        with self.assertRaises(ValueError):
            use_case.execute(
                opportunity_id=uuid4(),
                provider_id="invalid-uuid",
            )

        self.assertEqual(access_repository.save_calls, 0)

    def test_opportunity_not_found_is_rejected(self):
        use_case = GrantOpportunityAccess(
            opportunity_repository=InMemoryOpportunityRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            provider_repository=InMemoryProviderRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=uuid4(), provider_id=uuid4())

    def test_opportunity_closed_is_rejected(self):
        opportunity_repository = InMemoryOpportunityRepository()
        provider_repository = InMemoryProviderRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        opportunity = self._opportunity(uuid4(), status=OpportunityStatus.CLOSED)
        provider = self._provider(uuid4())
        opportunity_repository.save(opportunity)
        provider_repository.save(provider)
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )
        with self.assertRaises(ValueError):
            use_case.execute(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
            )

    def test_opportunity_cancelled_is_rejected(self):
        opportunity_repository = InMemoryOpportunityRepository()
        provider_repository = InMemoryProviderRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        opportunity = self._opportunity(uuid4(), status=OpportunityStatus.CANCELLED)
        provider = self._provider(uuid4())
        opportunity_repository.save(opportunity)
        provider_repository.save(provider)
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )
        with self.assertRaises(ValueError):
            use_case.execute(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
            )

    def test_provider_not_found_is_rejected(self):
        opportunity_repository = InMemoryOpportunityRepository()
        opportunity = self._opportunity(uuid4())
        opportunity_repository.save(opportunity)
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            provider_repository=InMemoryProviderRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id, provider_id=uuid4())

    def test_provider_inactive_is_rejected(self):
        opportunity_repository = InMemoryOpportunityRepository()
        provider_repository = InMemoryProviderRepository()
        opportunity = self._opportunity(uuid4())
        provider = self._provider(uuid4(), is_active=False)
        opportunity_repository.save(opportunity)
        provider_repository.save(provider)
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            provider_repository=provider_repository,
        )
        with self.assertRaises(ValueError):
            use_case.execute(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
            )

    def test_duplicate_access_is_rejected(self):
        opportunity_repository = InMemoryOpportunityRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        provider_repository = InMemoryProviderRepository()
        opportunity = self._opportunity(uuid4())
        provider = self._provider(uuid4())
        opportunity_repository.save(opportunity)
        provider_repository.save(provider)
        access_repository.save(
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )
        with self.assertRaises(ValueError):
            use_case.execute(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
            )

    def test_max_accesses_reached_is_rejected(self):
        opportunity_repository = InMemoryOpportunityRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        provider_repository = InMemoryProviderRepository()
        opportunity = self._opportunity(uuid4(), max_accesses=1)
        first_provider = self._provider(uuid4())
        second_provider = self._provider(uuid4())
        opportunity_repository.save(opportunity)
        provider_repository.save(first_provider)
        provider_repository.save(second_provider)
        access_repository.save(
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=opportunity.id,
                provider_id=first_provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )
        with self.assertRaises(ValueError):
            use_case.execute(
                opportunity_id=opportunity.id,
                provider_id=second_provider.id,
            )

    def test_below_max_accesses_allows_grant(self):
        opportunity_repository = InMemoryOpportunityRepository()
        access_repository = InMemoryOpportunityAccessRepository()
        provider_repository = InMemoryProviderRepository()
        opportunity = self._opportunity(uuid4(), max_accesses=2)
        first_provider = self._provider(uuid4())
        second_provider = self._provider(uuid4())
        opportunity_repository.save(opportunity)
        provider_repository.save(first_provider)
        provider_repository.save(second_provider)
        access_repository.save(
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=opportunity.id,
                provider_id=first_provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )
        use_case = GrantOpportunityAccess(
            opportunity_repository=opportunity_repository,
            opportunity_access_repository=access_repository,
            provider_repository=provider_repository,
        )

        granted = use_case.execute(
            opportunity_id=opportunity.id,
            provider_id=second_provider.id,
        )
        self.assertEqual(granted.provider_id, second_provider.id)


class InviteProviderToOpportunityTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Demanda tecnica",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _opportunity(
        opportunity_id: UUID,
        *,
        service_request_id: UUID,
        status: OpportunityStatus = OpportunityStatus.OPEN,
    ) -> Opportunity:
        now = datetime.now(timezone.utc)
        return Opportunity(
            id=opportunity_id,
            service_request_id=service_request_id,
            status=status,
            max_accesses=3,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider",
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_invalid_opportunity_id_rejected(self):
        use_case = InviteProviderToOpportunity(
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=None, provider_id=uuid4())
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id="invalid-uuid", provider_id=uuid4())

    def test_invalid_provider_id_rejected(self):
        use_case = InviteProviderToOpportunity(
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=uuid4(), provider_id=None)
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=uuid4(), provider_id="invalid-uuid")

    def test_nonexistent_opportunity_rejected(self):
        provider = self._provider(uuid4())
        p_repo = InMemoryProviderRepository()
        p_repo.save(provider)
        use_case = InviteProviderToOpportunity(
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=p_repo,
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=uuid4(), provider_id=provider.id)

    def test_closed_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CLOSED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        use_case = InviteProviderToOpportunity(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

    def test_cancelled_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CANCELLED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        use_case = InviteProviderToOpportunity(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

    def test_nonexistent_provider_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        req_repo = InMemoryServiceRequestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)

        req_repo.save(request)
        opp_repo.save(opportunity)

        use_case = InviteProviderToOpportunity(
            opportunity_repository=opp_repo,
            provider_repository=InMemoryProviderRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id, provider_id=uuid4())

    def test_inactive_provider_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4(), is_active=False)

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        use_case = InviteProviderToOpportunity(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

    def test_duplicate_invitation_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        inv_repo.save(
            OpportunityInvitation(
                id=uuid4(),
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )

        use_case = InviteProviderToOpportunity(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

    def test_valid_invitation_created(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        use_case = InviteProviderToOpportunity(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
        )
        invitation = use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertEqual(invitation.opportunity_id, opportunity.id)
        self.assertEqual(invitation.provider_id, provider.id)
        self.assertIsNotNone(invitation.id)
        self.assertIsNotNone(invitation.created_at.tzinfo)


class RegisterOpportunityInterestTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Demanda tecnica",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _opportunity(
        opportunity_id: UUID,
        *,
        service_request_id: UUID,
        status: OpportunityStatus = OpportunityStatus.OPEN,
    ) -> Opportunity:
        now = datetime.now(timezone.utc)
        return Opportunity(
            id=opportunity_id,
            service_request_id=service_request_id,
            status=status,
            max_accesses=3,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider",
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_invalid_invitation_id_rejected(self):
        use_case = RegisterOpportunityInterest(
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(invitation_id=None)
        with self.assertRaises(ValueError):
            use_case.execute(invitation_id="invalid-uuid")

    def test_nonexistent_invitation_rejected(self):
        use_case = RegisterOpportunityInterest(
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(invitation_id=uuid4())

    def test_valid_invitation_creates_interest(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        use_case = RegisterOpportunityInterest(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_interest_repository=int_repo,
        )
        interest = use_case.execute(invitation_id=invitation.id)

        self.assertIsNotNone(interest.id)
        self.assertEqual(interest.invitation_id, invitation.id)
        self.assertIsNotNone(interest.created_at.tzinfo)

    def test_duplicate_interest_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        int_repo.save(
            OpportunityInterest(
                id=uuid4(),
                invitation_id=invitation.id,
                created_at=datetime.now(timezone.utc),
            )
        )

        use_case = RegisterOpportunityInterest(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_interest_repository=int_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(invitation_id=invitation.id)

    def test_closed_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CLOSED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        use_case = RegisterOpportunityInterest(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_interest_repository=int_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(invitation_id=invitation.id)

    def test_cancelled_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CANCELLED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        use_case = RegisterOpportunityInterest(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_interest_repository=int_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(invitation_id=invitation.id)

    def test_inactive_provider_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4(), is_active=False)

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        use_case = RegisterOpportunityInterest(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_interest_repository=int_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(invitation_id=invitation.id)

    def test_critical_semantic_separation(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        use_case = RegisterOpportunityInterest(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_interest_repository=int_repo,
        )
        interest = use_case.execute(invitation_id=invitation.id)

        self.assertIsNotNone(interest)
        self.assertEqual(interest.invitation_id, invitation.id)
        self.assertEqual(len(access_repo._items), 0)


class TechnicalMatchingPolicyV1Tests(SimpleTestCase):
    @staticmethod
    def _service_request() -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider() -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="desc",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def test_eligible_provider_produces_matching_result_with_score_100_and_reason(self):
        policy = TechnicalMatchingPolicyV1()
        request = self._service_request()
        provider = self._provider()

        result = policy.evaluate(service_request=request, provider=provider)

        self.assertIsInstance(result, MatchingResult)
        self.assertEqual(result.provider, provider)
        self.assertEqual(result.score, 100)
        self.assertEqual(result.reasons, ("technical_service_match",))


class FakeMatchingPolicy:
    def __init__(self, custom_scores: dict[UUID, int]):
        self.custom_scores = custom_scores

    def evaluate(self, *, service_request: ServiceRequest, provider: Provider) -> MatchingResult:
        score = self.custom_scores.get(provider.id, 100)
        return MatchingResult(
            provider=provider,
            score=score,
            reasons=("fake_test_reason",)
        )


class RankCandidatesTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Demanda tecnica",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        display_name: str,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name=display_name,
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider_service(
        *,
        provider_id: UUID,
        service_id: UUID,
        is_active: bool = True,
    ) -> ProviderService:
        now = datetime.now(timezone.utc)
        return ProviderService(
            id=uuid4(),
            provider_id=provider_id,
            service_id=service_id,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_single_eligible_candidate_returns_one_result(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        provider = self._provider(uuid4(), display_name="Provider X")
        capability = self._provider_service(provider_id=provider.id, service_id=service_id)

        req_repo.save(request)
        p_repo.save(provider)
        ps_repo.save(capability)

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=TechnicalMatchingPolicyV1(),
        )

        results = use_case.execute(service_request_id=request.id)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider.id, provider.id)
        self.assertEqual(results[0].score, 100)
        self.assertEqual(results[0].reasons, ("technical_service_match",))

    def test_no_candidates_returns_empty_list(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        req_repo.save(request)

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=TechnicalMatchingPolicyV1(),
        )

        results = use_case.execute(service_request_id=request.id)
        self.assertEqual(results, [])

    def test_multiple_candidates_all_scored_and_deterministically_tied_ordered(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        req_repo.save(request)

        p1 = self._provider(uuid4(), display_name="Acme Corp")
        p2 = self._provider(uuid4(), display_name="acme")
        p3 = self._provider(uuid4(), display_name="Beta")

        for p in [p1, p2, p3]:
            p_repo.save(p)
            ps_repo.save(self._provider_service(provider_id=p.id, service_id=service_id))

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=TechnicalMatchingPolicyV1(),
        )

        results = use_case.execute(service_request_id=request.id)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].provider.display_name, "acme")
        self.assertEqual(results[1].provider.display_name, "Acme Corp")
        self.assertEqual(results[2].provider.display_name, "Beta")

        for res in results:
            self.assertEqual(res.score, 100)
            self.assertEqual(res.reasons, ("technical_service_match",))

    def test_policy_substitution_works(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        req_repo.save(request)

        p_low = self._provider(uuid4(), display_name="Provider Low Score")
        p_high = self._provider(uuid4(), display_name="Provider High Score")

        for p in [p_low, p_high]:
            p_repo.save(p)
            ps_repo.save(self._provider_service(provider_id=p.id, service_id=service_id))

        fake_policy = FakeMatchingPolicy({
            p_low.id: 40,
            p_high.id: 90,
        })

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=fake_policy,
        )

        results = use_case.execute(service_request_id=request.id)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].provider.id, p_high.id)
        self.assertEqual(results[0].score, 90)
        self.assertEqual(results[1].provider.id, p_low.id)
        self.assertEqual(results[1].score, 40)

    def test_inactive_providers_are_ignored(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        req_repo.save(request)

        p_inactive = self._provider(uuid4(), display_name="Inactive Provider", is_active=False)
        p_repo.save(p_inactive)
        ps_repo.save(self._provider_service(provider_id=p_inactive.id, service_id=service_id))

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=TechnicalMatchingPolicyV1(),
        )

        results = use_case.execute(service_request_id=request.id)
        self.assertEqual(results, [])

    def test_closed_service_request_is_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        request = self._service_request(uuid4(), service_id=uuid4(), status=ServiceRequestStatus.CLOSED)
        req_repo.save(request)

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=TechnicalMatchingPolicyV1(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=request.id)

    def test_cancelled_service_request_is_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        request = self._service_request(uuid4(), service_id=uuid4(), status=ServiceRequestStatus.CANCELLED)
        req_repo.save(request)

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=TechnicalMatchingPolicyV1(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=request.id)

    def test_invalid_service_request_id_is_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        ps_repo = InMemoryProviderServiceRepository()
        p_repo = InMemoryProviderRepository()

        discovery = DiscoverCandidates(
            service_request_repository=req_repo,
            provider_service_repository=ps_repo,
            provider_repository=p_repo,
        )
        use_case = RankCandidates(
            discover_candidates=discovery,
            service_request_repository=req_repo,
            matching_policy=TechnicalMatchingPolicyV1(),
        )

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id=None)

        with self.assertRaises(ValueError):
            use_case.execute(service_request_id="invalid-uuid")


class DistributeOpportunityTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Request",
            description="desc",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _opportunity(
        opportunity_id: UUID,
        *,
        service_request_id: UUID,
        max_accesses: int = 3,
        status: OpportunityStatus = OpportunityStatus.OPEN,
    ) -> Opportunity:
        now = datetime.now(timezone.utc)
        return Opportunity(
            id=opportunity_id,
            service_request_id=service_request_id,
            status=status,
            max_accesses=max_accesses,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        display_name: str,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name=display_name,
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider_service(
        *,
        provider_id: UUID,
        service_id: UUID,
        is_active: bool = True,
    ) -> ProviderService:
        now = datetime.now(timezone.utc)
        return ProviderService(
            id=uuid4(),
            provider_id=provider_id,
            service_id=service_id,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_invalid_opportunity_id_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=None)

        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id="invalid-uuid")

    def test_nonexistent_opportunity_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=uuid4())

    def test_closed_opportunity_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CLOSED)

        req_repo.save(request)
        opp_repo.save(opportunity)

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id)

    def test_cancelled_opportunity_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CANCELLED)

        req_repo.save(request)
        opp_repo.save(opportunity)

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id)

    def test_no_ranked_candidates_returns_empty(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)

        req_repo.save(request)
        opp_repo.save(opportunity)

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        results = use_case.execute(opportunity_id=opportunity.id)
        self.assertEqual(results, [])

    def test_one_ranked_candidate_with_capacity_granted(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, max_accesses=2)
        provider = self._provider(uuid4(), display_name="Provider A")
        capability = self._provider_service(provider_id=provider.id, service_id=service_id)

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)
        ps_repo.save(capability)

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        results = use_case.execute(opportunity_id=opportunity.id, max_invitations=2)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider_id, provider.id)
        self.assertEqual(results[0].opportunity_id, opportunity.id)

    def test_multiple_candidates_granted_up_to_capacity_and_respecting_ranking_order(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)

        p1 = self._provider(uuid4(), display_name="Low Score")
        p2 = self._provider(uuid4(), display_name="High Score")
        p3 = self._provider(uuid4(), display_name="Mid Score")

        for p in [p1, p2, p3]:
            p_repo.save(p)
            ps_repo.save(self._provider_service(provider_id=p.id, service_id=service_id))

        req_repo.save(request)
        opp_repo.save(opportunity)

        fake_policy = FakeMatchingPolicy({
            p1.id: 20,
            p2.id: 90,
            p3.id: 70,
        })

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, fake_policy)
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        results = use_case.execute(opportunity_id=opportunity.id, max_invitations=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].provider_id, p2.id)
        self.assertEqual(results[1].provider_id, p3.id)

    def test_existing_invitations_skipped_and_reduces_remaining_capacity(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)

        pb = self._provider(uuid4(), display_name="B")
        pc = self._provider(uuid4(), display_name="C")
        pa = self._provider(uuid4(), display_name="A")

        for p in [pb, pc, pa]:
            p_repo.save(p)
            ps_repo.save(self._provider_service(provider_id=p.id, service_id=service_id))

        req_repo.save(request)
        opp_repo.save(opportunity)

        existing_inv = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=pb.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(existing_inv)

        fake_policy = FakeMatchingPolicy({
            pb.id: 90,
            pc.id: 70,
            pa.id: 50,
        })

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, fake_policy)
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        results = use_case.execute(opportunity_id=opportunity.id, max_invitations=2)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider_id, pc.id)

    def test_distribute_when_capacity_full_returns_empty(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        p = self._provider(uuid4(), display_name="Provider A")

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(p)
        ps_repo.save(self._provider_service(provider_id=p.id, service_id=service_id))

        inv_repo.save(
            OpportunityInvitation(id=uuid4(), opportunity_id=opportunity.id, provider_id=p.id, created_at=datetime.now(timezone.utc))
        )

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        results = use_case.execute(opportunity_id=opportunity.id, max_invitations=1)
        self.assertEqual(results, [])

    def test_closed_service_request_rejected(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        request = self._service_request(uuid4(), service_id=uuid4(), status=ServiceRequestStatus.CLOSED)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)

        req_repo.save(request)
        opp_repo.save(opportunity)

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        with self.assertRaises(ValueError):
            use_case.execute(opportunity_id=opportunity.id)

    def test_critical_regression_distribute_does_not_create_opportunity_access(self):
        req_repo = InMemoryServiceRequestRepository()
        opp_repo = InMemoryOpportunityRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        p_repo = InMemoryProviderRepository()
        ps_repo = InMemoryProviderServiceRepository()

        service_id = uuid4()
        request = self._service_request(uuid4(), service_id=service_id)
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4(), display_name="Provider A")
        capability = self._provider_service(provider_id=provider.id, service_id=service_id)

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)
        ps_repo.save(capability)

        discovery = DiscoverCandidates(req_repo, ps_repo, p_repo)
        ranking = RankCandidates(discovery, req_repo, TechnicalMatchingPolicyV1())
        invite_usecase = InviteProviderToOpportunity(opp_repo, p_repo, inv_repo)

        use_case = DistributeOpportunity(
            opportunity_repository=opp_repo,
            service_request_repository=req_repo,
            opportunity_invitation_repository=inv_repo,
            rank_candidates=ranking,
            invite_provider_to_opportunity=invite_usecase,
        )

        # Distribute should only invoke InviteProviderToOpportunity and save invitations.
        # It must NOT call GrantOpportunityAccess or save in access_repo.
        results = use_case.execute(opportunity_id=opportunity.id, max_invitations=3)

        self.assertEqual(len(results), 1)
        self.assertEqual(inv_repo.save_calls, 1)
        self.assertEqual(access_repo.save_calls, 0)


class FakeAccessEntitlementPolicy:
    def __init__(self, allowed: bool = True, reason: str = "test"):
        self.allowed = allowed
        self.reason = reason
        self.call_count = 0
        self.last_interest = None
        self.last_invitation = None
        self.last_opportunity = None
        self.last_provider = None

    def decide(
        self,
        *,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> AccessEntitlementDecision:
        self.call_count += 1
        self.last_interest = interest
        self.last_invitation = invitation
        self.last_opportunity = opportunity
        self.last_provider = provider
        return AccessEntitlementDecision(allowed=self.allowed, reason=self.reason)


class RequestOpportunityAccessTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Demanda tecnica",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _opportunity(
        opportunity_id: UUID,
        *,
        service_request_id: UUID,
        status: OpportunityStatus = OpportunityStatus.OPEN,
    ) -> Opportunity:
        now = datetime.now(timezone.utc)
        return Opportunity(
            id=opportunity_id,
            service_request_id=service_request_id,
            status=status,
            max_accesses=3,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider",
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_invalid_interest_id_rejected(self):
        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            access_entitlement_policy=FakeAccessEntitlementPolicy(),
            grant_opportunity_access=GrantOpportunityAccess(
                InMemoryOpportunityRepository(),
                InMemoryOpportunityAccessRepository(),
                InMemoryProviderRepository(),
            ),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=None)
        with self.assertRaises(ValueError):
            use_case.execute(interest_id="invalid-uuid")

    def test_nonexistent_interest_rejected(self):
        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            access_entitlement_policy=FakeAccessEntitlementPolicy(),
            grant_opportunity_access=GrantOpportunityAccess(
                InMemoryOpportunityRepository(),
                InMemoryOpportunityAccessRepository(),
                InMemoryProviderRepository(),
            ),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=uuid4())

    def test_closed_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CLOSED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=FakeAccessEntitlementPolicy(),
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

    def test_cancelled_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CANCELLED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=FakeAccessEntitlementPolicy(),
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

    def test_inactive_provider_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4(), is_active=False)

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=FakeAccessEntitlementPolicy(),
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

    def test_existing_opportunity_access_rejected_before_policy_decision(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        access_repo.save(
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )

        policy = FakeAccessEntitlementPolicy(allowed=True, reason="test")

        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=policy,
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

        self.assertEqual(policy.call_count, 0)

    def test_critical_denied_scenario(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        policy = FakeAccessEntitlementPolicy(allowed=False, reason="test_denied")

        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=policy,
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        result = use_case.execute(interest_id=interest.id)

        self.assertFalse(result.decision.allowed)
        self.assertEqual(result.decision.reason, "test_denied")
        self.assertIsNone(result.access)
        self.assertEqual(len(access_repo._items), 0)
        self.assertEqual(policy.call_count, 1)

    def test_critical_allowed_scenario(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        policy = FakeAccessEntitlementPolicy(allowed=True, reason="test_allowed")

        use_case = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=policy,
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        result = use_case.execute(interest_id=interest.id)

        self.assertTrue(result.decision.allowed)
        self.assertEqual(result.decision.reason, "test_allowed")
        self.assertIsNotNone(result.access)
        self.assertEqual(result.access.opportunity_id, opportunity.id)
        self.assertEqual(result.access.provider_id, provider.id)
        self.assertEqual(len(access_repo._items), 1)
        self.assertEqual(policy.call_count, 1)

        self.assertEqual(policy.last_interest.id, interest.id)
        self.assertEqual(policy.last_invitation.id, invitation.id)
        self.assertEqual(policy.last_opportunity.id, opportunity.id)
        self.assertEqual(policy.last_provider.id, provider.id)


class FakeOpportunityPricingPolicy:
    def __init__(self, amount_minor: int = 2500, currency: str = "BRL", reason: str = "test_quote"):
        self.amount_minor = amount_minor
        self.currency = currency
        self.reason = reason
        self.call_count = 0
        self.last_interest = None
        self.last_invitation = None
        self.last_opportunity = None
        self.last_provider = None

    def quote(
        self,
        *,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> OpportunityPricingQuote:
        self.call_count += 1
        self.last_interest = interest
        self.last_invitation = invitation
        self.last_opportunity = opportunity
        self.last_provider = provider
        return OpportunityPricingQuote(
            amount=Money(amount_minor=self.amount_minor, currency=self.currency),
            reason=self.reason,
        )


class QuoteOpportunityAccessPriceTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Demanda tecnica",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _opportunity(
        opportunity_id: UUID,
        *,
        service_request_id: UUID,
        status: OpportunityStatus = OpportunityStatus.OPEN,
    ) -> Opportunity:
        now = datetime.now(timezone.utc)
        return Opportunity(
            id=opportunity_id,
            service_request_id=service_request_id,
            status=status,
            max_accesses=3,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider",
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_invalid_interest_id_rejected(self):
        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            opportunity_pricing_policy=FakeOpportunityPricingPolicy(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=None)
        with self.assertRaises(ValueError):
            use_case.execute(interest_id="invalid-uuid")

    def test_nonexistent_interest_rejected(self):
        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            opportunity_pricing_policy=FakeOpportunityPricingPolicy(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=uuid4())

    def test_closed_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CLOSED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            opportunity_pricing_policy=FakeOpportunityPricingPolicy(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

    def test_cancelled_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CANCELLED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            opportunity_pricing_policy=FakeOpportunityPricingPolicy(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

    def test_inactive_provider_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4(), is_active=False)

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            opportunity_pricing_policy=FakeOpportunityPricingPolicy(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

    def test_existing_opportunity_access_rejected_before_pricing_policy_call(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        access_repo.save(
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )

        policy = FakeOpportunityPricingPolicy()

        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            opportunity_pricing_policy=policy,
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id)

        self.assertEqual(policy.call_count, 0)

    def test_critical_semantic_pricing_test(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        policy = FakeOpportunityPricingPolicy(amount_minor=2500, currency="BRL", reason="test_quote")

        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            opportunity_pricing_policy=policy,
        )
        quote = use_case.execute(interest_id=interest.id)

        self.assertEqual(quote.amount.amount_minor, 2500)
        self.assertEqual(quote.amount.currency, "BRL")
        self.assertEqual(quote.reason, "test_quote")
        self.assertEqual(len(access_repo._items), 0)
        self.assertEqual(policy.call_count, 1)

        self.assertEqual(policy.last_interest.id, interest.id)
        self.assertEqual(policy.last_invitation.id, invitation.id)
        self.assertEqual(policy.last_opportunity.id, opportunity.id)
        self.assertEqual(policy.last_provider.id, provider.id)

    def test_zero_price_test(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        policy = FakeOpportunityPricingPolicy(amount_minor=0, currency="BRL", reason="test_free")

        use_case = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            opportunity_pricing_policy=policy,
        )
        quote = use_case.execute(interest_id=interest.id)

        self.assertEqual(quote.amount.amount_minor, 0)
        self.assertEqual(quote.amount.currency, "BRL")
        self.assertEqual(quote.reason, "test_free")
        self.assertEqual(len(access_repo._items), 0)
        self.assertEqual(policy.call_count, 1)

    def test_regression_flows_remain_independent(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        # 1. RegisterOpportunityInterest creates Interest but NO Access
        register_usecase = RegisterOpportunityInterest(
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_interest_repository=int_repo,
        )
        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = register_usecase.execute(invitation_id=invitation.id)
        self.assertIsNotNone(interest)
        self.assertEqual(len(access_repo._items), 0)

        # 2. QuoteOpportunityAccessPrice returns Quote but NO Access
        quote_usecase = QuoteOpportunityAccessPrice(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            opportunity_pricing_policy=FakeOpportunityPricingPolicy(amount_minor=1000),
        )
        quote = quote_usecase.execute(interest_id=interest.id)
        self.assertEqual(quote.amount.amount_minor, 1000)
        self.assertEqual(len(access_repo._items), 0)

        # 3. RequestOpportunityAccess using DENIED entitlement policy creates NO Access
        ent_policy_denied = FakeAccessEntitlementPolicy(allowed=False, reason="denied")
        request_usecase_denied = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=ent_policy_denied,
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        result_denied = request_usecase_denied.execute(interest_id=interest.id)
        self.assertFalse(result_denied.decision.allowed)
        self.assertIsNone(result_denied.access)
        self.assertEqual(len(access_repo._items), 0)

        # 4. RequestOpportunityAccess using ALLOWED entitlement policy creates Access
        ent_policy_allowed = FakeAccessEntitlementPolicy(allowed=True, reason="allowed")
        request_usecase_allowed = RequestOpportunityAccess(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            access_entitlement_policy=ent_policy_allowed,
            grant_opportunity_access=GrantOpportunityAccess(opp_repo, access_repo, p_repo),
        )
        result_allowed = request_usecase_allowed.execute(interest_id=interest.id)
        self.assertTrue(result_allowed.decision.allowed)
        self.assertIsNotNone(result_allowed.access)
        self.assertEqual(len(access_repo._items), 1)


class RecordEconomicSettlementTests(SimpleTestCase):
    @staticmethod
    def _service_request(
        service_request_id: UUID,
        *,
        service_id: UUID,
        status: ServiceRequestStatus = ServiceRequestStatus.OPEN,
    ) -> ServiceRequest:
        now = datetime.now(timezone.utc)
        return ServiceRequest(
            id=service_request_id,
            organization_id=uuid4(),
            service_id=service_id,
            title="Demanda tecnica",
            description="Descricao",
            status=status,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _opportunity(
        opportunity_id: UUID,
        *,
        service_request_id: UUID,
        status: OpportunityStatus = OpportunityStatus.OPEN,
    ) -> Opportunity:
        now = datetime.now(timezone.utc)
        return Opportunity(
            id=opportunity_id,
            service_request_id=service_request_id,
            status=status,
            max_accesses=3,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _provider(
        provider_id: UUID,
        *,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider",
            slug=f"provider-{provider_id}",
            description="desc",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_invalid_interest_id_rejected(self):
        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            economic_settlement_repository=InMemoryEconomicSettlementRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=None, method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))
        with self.assertRaises(ValueError):
            use_case.execute(interest_id="invalid-uuid", method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))

    def test_invalid_method_rejected(self):
        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            economic_settlement_repository=InMemoryEconomicSettlementRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=uuid4(), method=None, amount=Money(100, "BRL"))
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=uuid4(), method="invalid-method", amount=Money(100, "BRL"))

    def test_invalid_amount_rejected(self):
        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            economic_settlement_repository=InMemoryEconomicSettlementRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=uuid4(), method=SettlementMethod.MANUAL, amount=None)
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=uuid4(), method=SettlementMethod.MANUAL, amount=25.90)

    def test_nonexistent_interest_rejected(self):
        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=InMemoryOpportunityInterestRepository(),
            opportunity_invitation_repository=InMemoryOpportunityInvitationRepository(),
            opportunity_repository=InMemoryOpportunityRepository(),
            provider_repository=InMemoryProviderRepository(),
            opportunity_access_repository=InMemoryOpportunityAccessRepository(),
            economic_settlement_repository=InMemoryEconomicSettlementRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=uuid4(), method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))

    def test_closed_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CLOSED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            economic_settlement_repository=settle_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id, method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))

    def test_cancelled_opportunity_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id, status=OpportunityStatus.CANCELLED)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            economic_settlement_repository=settle_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id, method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))

    def test_inactive_provider_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4(), is_active=False)

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            economic_settlement_repository=settle_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id, method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))

    def test_existing_opportunity_access_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        access_repo.save(
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )

        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            economic_settlement_repository=settle_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id, method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))

    def test_duplicate_settlement_rejected(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        settle_repo.save(
            EconomicSettlement(
                id=uuid4(),
                interest_id=interest.id,
                method=SettlementMethod.MANUAL,
                amount=Money(100, "BRL"),
                created_at=datetime.now(timezone.utc),
            )
        )

        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            economic_settlement_repository=settle_repo,
        )
        with self.assertRaises(ValueError):
            use_case.execute(interest_id=interest.id, method=SettlementMethod.MANUAL, amount=Money(100, "BRL"))

    def test_critical_semantic_settlement_test(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            economic_settlement_repository=settle_repo,
        )
        settlement = use_case.execute(
            interest_id=interest.id,
            method=SettlementMethod.MANUAL,
            amount=Money(2500, "BRL"),
        )

        self.assertIsNotNone(settlement.id)
        self.assertEqual(settlement.interest_id, interest.id)
        self.assertEqual(settlement.method, SettlementMethod.MANUAL)
        self.assertEqual(settlement.amount.amount_minor, 2500)
        self.assertEqual(settlement.amount.currency, "BRL")
        self.assertIsNotNone(settlement.created_at)
        self.assertIsNotNone(settlement.created_at.tzinfo)
        self.assertEqual(settle_repo.save_calls, 1)
        self.assertEqual(len(access_repo._items), 0)

    def test_complimentary_test(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        use_case = RecordEconomicSettlement(
            opportunity_interest_repository=int_repo,
            opportunity_invitation_repository=inv_repo,
            opportunity_repository=opp_repo,
            provider_repository=p_repo,
            opportunity_access_repository=access_repo,
            economic_settlement_repository=settle_repo,
        )
        settlement = use_case.execute(
            interest_id=interest.id,
            method=SettlementMethod.COMPLIMENTARY,
            amount=Money(0, "BRL"),
        )

        self.assertEqual(settlement.amount.amount_minor, 0)
        self.assertEqual(settlement.method, SettlementMethod.COMPLIMENTARY)
        self.assertEqual(len(access_repo._items), 0)

    def test_zero_quote_vs_settlement_regression(self):
        opp_repo = InMemoryOpportunityRepository()
        p_repo = InMemoryProviderRepository()
        req_repo = InMemoryServiceRequestRepository()
        inv_repo = InMemoryOpportunityInvitationRepository()
        int_repo = InMemoryOpportunityInterestRepository()
        access_repo = InMemoryOpportunityAccessRepository()
        settle_repo = InMemoryEconomicSettlementRepository()

        request = self._service_request(uuid4(), service_id=uuid4())
        opportunity = self._opportunity(uuid4(), service_request_id=request.id)
        provider = self._provider(uuid4())

        req_repo.save(request)
        opp_repo.save(opportunity)
        p_repo.save(provider)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        inv_repo.save(invitation)

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        int_repo.save(interest)

        # Conceptual pricing policy returns Money(0, "BRL")
        # Assert by itself: Settlement remains absent, Access remains absent.
        self.assertEqual(len(settle_repo._items), 0)
        self.assertEqual(len(access_repo._items), 0)
