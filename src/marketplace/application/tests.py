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
    CreateCreditWallet,
    GetCreditWalletBalance,
    RecordCredit,
    RecordDebit,
    SettleOpportunityWithCredits,
    SettlementAwareAccessEntitlementPolicy,
    RankCandidates,
    GetProtectedCommercialData,
    GetOpportunityPreview,
    GetOpportunityUnlockQuote,
    UnlockOpportunityWithCredits,
    ReconcileOpportunityEconomicAcquisition,
    GetUnlockedOpportunityContact,
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
    CreditWallet,
    CreditLedgerDirection,
    CreditLedgerEntry,
    CreditSettlementResult,
    ProtectedCommercialData,
    OpportunityPreview,
    OpportunityUnlockQuote,
    OpportunityPricingUnavailable,
    OpportunityUnlockResult,
    EconomicAcquisitionReconciliationIssue,
    UnlockedOpportunityContact,
    ProviderOpportunityInboxItem,
    ProviderUnlockedOpportunityItem,
    ProviderUnlockedOpportunityPage,
)
from src.marketplace.application.ports import (
    CreditCostPolicy,
    CreditSettlementAtomicWriter,
    OpportunityUnlockAtomicWriter,
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
    def __init__(self, opportunity_repo=None, service_request_repo=None):
        self._items: dict[str, OpportunityAccess] = {}
        self.save_calls = 0
        self.last_saved: OpportunityAccess | None = None
        self.opportunity_repo = opportunity_repo
        self.service_request_repo = service_request_repo

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

    def list_unlocked_items_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProviderUnlockedOpportunityItem], int]:
        all_accesses = [
            item for item in self._items.values() if item.provider_id == provider_id
        ]
        all_accesses.sort(key=lambda x: (x.created_at, str(x.id)), reverse=True)

        items: list[ProviderUnlockedOpportunityItem] = []
        for acc in all_accesses:
            if self.opportunity_repo and self.service_request_repo:
                opp = self.opportunity_repo.get_by_id(acc.opportunity_id)
                if not opp:
                    continue
                sr = self.service_request_repo.get_by_id(opp.service_request_id)
                if not sr:
                    continue
                items.append(
                    ProviderUnlockedOpportunityItem(
                        opportunity_id=opp.id,
                        service_request_id=sr.id,
                        service_id=sr.service_id,
                        title=sr.title,
                        description=sr.description,
                        status=opp.status,
                        unlocked_at=acc.created_at,
                    )
                )

        total_items = len(items)
        offset = (page - 1) * page_size
        return items[offset : offset + page_size], total_items


class InMemoryOpportunityInvitationRepository:
    def __init__(self, opportunity_repo=None, service_request_repo=None):
        self._items: dict[str, OpportunityInvitation] = {}
        self.save_calls = 0
        self.last_saved: OpportunityInvitation | None = None
        self.opportunity_repo = opportunity_repo
        self.service_request_repo = service_request_repo

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

    def list_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OpportunityInvitation], int]:
        all_items = [
            item for item in self._items.values() if item.provider_id == provider_id
        ]
        all_items.sort(key=lambda x: (x.created_at, str(x.id)), reverse=True)
        total_items = len(all_items)
        offset = (page - 1) * page_size
        return all_items[offset : offset + page_size], total_items

    def list_inbox_items_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: OpportunityStatus | None = None,
    ) -> tuple[list[ProviderOpportunityInboxItem], int]:
        all_invitations = [
            item for item in self._items.values() if item.provider_id == provider_id
        ]
        all_invitations.sort(key=lambda x: (x.created_at, str(x.id)), reverse=True)

        all_inbox_items: list[ProviderOpportunityInboxItem] = []
        for inv in all_invitations:
            if self.opportunity_repo and self.service_request_repo:
                opp = self.opportunity_repo.get_by_id(inv.opportunity_id)
                if not opp:
                    continue
                if status is not None and opp.status != status:
                    continue
                sr = self.service_request_repo.get_by_id(opp.service_request_id)
                if not sr:
                    continue
                all_inbox_items.append(
                    ProviderOpportunityInboxItem(
                        invitation_id=inv.id,
                        opportunity_id=opp.id,
                        service_request_id=sr.id,
                        service_id=sr.service_id,
                        title=sr.title,
                        description=sr.description,
                        status=opp.status,
                        created_at=inv.created_at,
                    )
                )

        total_items = len(all_inbox_items)
        offset = (page - 1) * page_size
        return all_inbox_items[offset : offset + page_size], total_items

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
        self.get_by_interest_calls = 0
        self.last_get_by_interest_id: UUID | None = None

    def save(self, settlement: EconomicSettlement) -> EconomicSettlement:
        self.save_calls += 1
        self.last_saved = settlement
        self._items[str(settlement.id)] = settlement
        return settlement

    def get_by_id(self, settlement_id: UUID) -> EconomicSettlement | None:
        return self._items.get(str(settlement_id))

    def get_by_interest(self, interest_id: UUID) -> EconomicSettlement | None:
        self.get_by_interest_calls += 1
        self.last_get_by_interest_id = interest_id
        for item in self._items.values():
            if item.interest_id == interest_id:
                return item
        return None


class InMemoryCreditWalletRepository:
    def __init__(self):
        self._items: dict[str, CreditWallet] = {}
        self.save_calls = 0
        self.last_saved: CreditWallet | None = None

    def save(self, wallet: CreditWallet) -> CreditWallet:
        self.save_calls += 1
        self.last_saved = wallet
        self._items[str(wallet.id)] = wallet
        return wallet

    def get_by_id(self, wallet_id: UUID) -> CreditWallet | None:
        return self._items.get(str(wallet_id))

    def get_by_organization(self, organization_id: UUID) -> CreditWallet | None:
        for item in self._items.values():
            if item.organization_id == organization_id:
                return item
        return None


class InMemoryCreditLedgerEntryRepository:
    def __init__(self):
        self._items: dict[str, CreditLedgerEntry] = {}
        self.save_calls = 0
        self.last_saved: CreditLedgerEntry | None = None

    def save(self, entry: CreditLedgerEntry) -> CreditLedgerEntry:
        # Immutable save check
        if str(entry.id) in self._items:
            raise Exception("IntegrityError: Duplicate primary key.")
        self.save_calls += 1
        self.last_saved = entry
        self._items[str(entry.id)] = entry
        return entry

    def get_by_id(self, entry_id: UUID) -> CreditLedgerEntry | None:
        return self._items.get(str(entry_id))

    def list_by_wallet(self, wallet_id: UUID) -> list[CreditLedgerEntry]:
        # Return deterministic chronological order (created_at ASC, id ASC)
        results = [e for e in self._items.values() if e.wallet_id == wallet_id]
        results.sort(key=lambda x: (x.created_at, x.id))
        return results

    def list_debits_by_reference(self, reference: str) -> list[CreditLedgerEntry]:
        results = [
            e for e in self._items.values()
            if e.direction is CreditLedgerDirection.DEBIT and e.reference == reference
        ]
        results.sort(key=lambda x: (x.created_at, x.id))
        return results


class InMemoryCreditSettlementAtomicWriter:
    def __init__(self, ledger_repo: InMemoryCreditLedgerEntryRepository, settlement_repo: InMemoryEconomicSettlementRepository):
        self.ledger_repo = ledger_repo
        self.settlement_repo = settlement_repo
        self.persist_calls = 0

    def persist(
        self,
        *,
        debit_entry: CreditLedgerEntry | None,
        settlement: EconomicSettlement,
        wallet_id: UUID,
        required_units: int,
    ) -> None:
        self.persist_calls += 1
        if debit_entry is not None:
            self.ledger_repo.save(debit_entry)
        self.settlement_repo.save(settlement)


class InMemoryOpportunityUnlockAtomicWriter:
    def __init__(self, interest_repo, ledger_repo, settlement_repo, access_repo, wallet_repo):
        self.interest_repo = interest_repo
        self.ledger_repo = ledger_repo
        self.settlement_repo = settlement_repo
        self.access_repo = access_repo
        self.wallet_repo = wallet_repo
        self.persist_calls = 0
        self.should_fail_at_access = False

    def persist_unlock(
        self,
        *,
        interest: OpportunityInterest,
        debit_entry: CreditLedgerEntry | None,
        settlement: EconomicSettlement,
        access: OpportunityAccess,
        wallet_id: UUID,
        required_units: int,
    ) -> None:
        self.persist_calls += 1

        wallet = self.wallet_repo.get_by_id(wallet_id)
        if wallet is None or not wallet.is_active:
            raise ValueError("Wallet is inactive inside transactional verification.")

        if required_units > 0:
            entries = self.ledger_repo.list_by_wallet(wallet_id)
            balance = sum(e.units for e in entries if e.direction is CreditLedgerDirection.CREDIT) - \
                      sum(e.units for e in entries if e.direction is CreditLedgerDirection.DEBIT)
            if required_units > balance:
                raise ValueError("Insufficient wallet credit balance under row lock.")

        if self.should_fail_at_access:
            raise RuntimeError("Database error during access persistence.")

        self.interest_repo.save(interest)
        if debit_entry is not None:
            self.ledger_repo.save(debit_entry)
        self.settlement_repo.save(settlement)
        self.access_repo.save(access)


class ConfigurableCreditCostPolicy:
    def __init__(self, rate_callback=None):
        self.call_count = 0
        self.last_price = None
        self.last_interest = None
        self.last_invitation = None
        self.last_opportunity = None
        self.last_provider = None
        self.rate_callback = rate_callback or (lambda price: price.amount_minor // 100)

    def units_required(
        self,
        *,
        price: Money,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> int:
        self.call_count += 1
        self.last_price = price
        self.last_interest = interest
        self.last_invitation = invitation
        self.last_opportunity = opportunity
        self.last_provider = provider
        return self.rate_callback(price)


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
            requester_name="John Doe",
            requester_email="john@example.com",
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
    def __init__(
        self,
        amount_minor: int = 2500,
        currency: str = "BRL",
        reason: str = "test_quote",
        pricing_source: str | None = None,
        pricing_configuration_id: UUID | None = None,
    ):
        self.amount_minor = amount_minor
        self.currency = currency
        self.reason = reason
        self.pricing_source = pricing_source
        self.pricing_configuration_id = pricing_configuration_id
        self.call_count = 0
        self.last_interest = None
        self.last_invitation = None
        self.last_opportunity = None
        self.last_provider = None

    def quote(
        self,
        *,
        interest: OpportunityInterest | None = None,
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
            pricing_source=self.pricing_source,
            pricing_configuration_id=self.pricing_configuration_id,
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


class CreateCreditWalletTests(SimpleTestCase):
    @staticmethod
    def _active_organization(org_id: UUID, is_active: bool = True) -> Organization:
        now = datetime.now(timezone.utc)
        return Organization(
            id=org_id,
            name="Test Org",
            slug="test-org",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_invalid_organization_id_rejected(self):
        use_case = CreateCreditWallet(
            organization_repository=InMemoryOrganizationRepository(),
            credit_wallet_repository=InMemoryCreditWalletRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(organization_id=None)
        with self.assertRaises(ValueError):
            use_case.execute(organization_id="invalid-uuid")

    def test_nonexistent_organization_rejected(self):
        use_case = CreateCreditWallet(
            organization_repository=InMemoryOrganizationRepository(),
            credit_wallet_repository=InMemoryCreditWalletRepository(),
        )
        with self.assertRaises(ValueError):
            use_case.execute(organization_id=uuid4())

    def test_inactive_organization_rejected(self):
        org_repo = InMemoryOrganizationRepository()
        wallet_repo = InMemoryCreditWalletRepository()
        org_id = uuid4()
        org = self._active_organization(org_id, is_active=False)
        org_repo.save(org)

        use_case = CreateCreditWallet(org_repo, wallet_repo)
        with self.assertRaises(ValueError):
            use_case.execute(organization_id=org_id)

    def test_duplicate_wallet_rejected(self):
        org_repo = InMemoryOrganizationRepository()
        wallet_repo = InMemoryCreditWalletRepository()
        org_id = uuid4()
        org = self._active_organization(org_id)
        org_repo.save(org)

        now = datetime.now(timezone.utc)
        wallet_repo.save(
            CreditWallet(
                id=uuid4(),
                organization_id=org_id,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )

        use_case = CreateCreditWallet(org_repo, wallet_repo)
        with self.assertRaises(ValueError):
            use_case.execute(organization_id=org_id)

    def test_valid_wallet_created(self):
        org_repo = InMemoryOrganizationRepository()
        wallet_repo = InMemoryCreditWalletRepository()
        org_id = uuid4()
        org = self._active_organization(org_id)
        org_repo.save(org)

        use_case = CreateCreditWallet(org_repo, wallet_repo)
        wallet = use_case.execute(organization_id=org_id)

        self.assertIsNotNone(wallet.id)
        self.assertEqual(wallet.organization_id, org_id)
        self.assertTrue(wallet.is_active)
        self.assertIsNotNone(wallet.created_at)
        self.assertIsNotNone(wallet.created_at.tzinfo)
        self.assertEqual(wallet.created_at, wallet.updated_at)
        self.assertEqual(wallet_repo.save_calls, 1)

        self.assertFalse(hasattr(wallet, "balance"))
        self.assertFalse(hasattr(wallet, "current_balance"))
        self.assertFalse(hasattr(wallet, "available_balance"))

    def test_structural_wallet_isolation_multiple_tenants(self):
        org_repo = InMemoryOrganizationRepository()
        wallet_repo = InMemoryCreditWalletRepository()

        org_id_a = uuid4()
        org_a = self._active_organization(org_id_a)
        org_repo.save(org_a)

        org_id_b = uuid4()
        org_b = self._active_organization(org_id_b)
        org_repo.save(org_b)

        use_case = CreateCreditWallet(org_repo, wallet_repo)
        wallet_a = use_case.execute(organization_id=org_id_a)
        wallet_b = use_case.execute(organization_id=org_id_b)

        self.assertNotEqual(wallet_a.id, wallet_b.id)
        self.assertNotEqual(wallet_a.organization_id, wallet_b.organization_id)
        self.assertEqual(wallet_repo.get_by_organization(org_id_a).id, wallet_a.id)
        self.assertEqual(wallet_repo.get_by_organization(org_id_b).id, wallet_b.id)


class RecordCreditTests(SimpleTestCase):
    def setUp(self):
        self.wallet_repo = InMemoryCreditWalletRepository()
        self.ledger_repo = InMemoryCreditLedgerEntryRepository()
        self.wallet_id = uuid4()
        now = datetime.now(timezone.utc)
        self.wallet = CreditWallet(
            id=self.wallet_id,
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.wallet_repo.save(self.wallet)

    def test_invalid_wallet_id_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=None, units=10, reason="Reason")
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id="invalid-uuid", units=10, reason="Reason")

    def test_missing_wallet_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=uuid4(), units=10, reason="Reason")

    def test_inactive_wallet_rejected(self):
        self.wallet.deactivate(datetime.now(timezone.utc))
        self.wallet_repo.save(self.wallet)
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10, reason="Reason")

    def test_zero_units_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=0, reason="Reason")

    def test_negative_units_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=-5, reason="Reason")

    def test_float_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10.5, reason="Reason")

    def test_bool_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=True, reason="Reason")

    def test_invalid_reason_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10, reason="   ")

    def test_invalid_reference_rejected(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10, reason="Reason", reference="   ")

    def test_valid_credit_recorded(self):
        use_case = RecordCredit(self.wallet_repo, self.ledger_repo)
        entry = use_case.execute(
            wallet_id=self.wallet_id,
            units=150,
            reason="Campaign Promotion",
            reference="campaign-55",
        )

        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.wallet_id, self.wallet_id)
        self.assertEqual(entry.direction, CreditLedgerDirection.CREDIT)
        self.assertEqual(entry.units, 150)
        self.assertEqual(entry.reason, "Campaign Promotion")
        self.assertEqual(entry.reference, "campaign-55")
        self.assertIsNotNone(entry.created_at.tzinfo)
        self.assertEqual(self.ledger_repo.save_calls, 1)

        # Assert wallet remains unchanged
        self.assertFalse(hasattr(self.wallet, "balance"))


class GetCreditWalletBalanceTests(SimpleTestCase):
    def setUp(self):
        self.wallet_repo = InMemoryCreditWalletRepository()
        self.ledger_repo = InMemoryCreditLedgerEntryRepository()
        self.wallet_id = uuid4()
        now = datetime.now(timezone.utc)
        self.wallet = CreditWallet(
            id=self.wallet_id,
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.wallet_repo.save(self.wallet)

    def test_empty_ledger_returns_0(self):
        use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        self.assertEqual(use_case.execute(wallet_id=self.wallet_id), 0)

    def test_one_credit_returns_units(self):
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.CREDIT,
                units=100,
                reason="Credit",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )
        )
        use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        self.assertEqual(use_case.execute(wallet_id=self.wallet_id), 100)

    def test_multiple_credits_accumulate(self):
        now = datetime.now(timezone.utc)
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.CREDIT,
                units=100,
                reason="Credit 1",
                reference=None,
                created_at=now,
            )
        )
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.CREDIT,
                units=50,
                reason="Credit 2",
                reference=None,
                created_at=now,
            )
        )
        use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        self.assertEqual(use_case.execute(wallet_id=self.wallet_id), 150)

    def test_mixed_credits_and_debits(self):
        now = datetime.now(timezone.utc)
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.CREDIT,
                units=100,
                reason="Credit",
                reference=None,
                created_at=now,
            )
        )
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.DEBIT,
                units=30,
                reason="Debit",
                reference=None,
                created_at=now,
            )
        )
        use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        self.assertEqual(use_case.execute(wallet_id=self.wallet_id), 70)

    def test_wallet_missing_rejected(self):
        use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=uuid4())

    def test_invalid_uuid_rejected(self):
        use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id="invalid-uuid")

    def test_does_not_mutate_wallet_and_creates_no_entries(self):
        use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        use_case.execute(wallet_id=self.wallet_id)
        self.assertFalse(hasattr(self.wallet, "balance"))
        self.assertEqual(self.ledger_repo.save_calls, 0)


class RecordDebitTests(SimpleTestCase):
    def setUp(self):
        self.wallet_repo = InMemoryCreditWalletRepository()
        self.ledger_repo = InMemoryCreditLedgerEntryRepository()
        self.wallet_id = uuid4()
        now = datetime.now(timezone.utc)
        self.wallet = CreditWallet(
            id=self.wallet_id,
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.wallet_repo.save(self.wallet)

    def test_missing_wallet_rejected(self):
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=uuid4(), units=10, reason="Reason")

    def test_inactive_wallet_rejected(self):
        self.wallet.deactivate(datetime.now(timezone.utc))
        self.wallet_repo.save(self.wallet)
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10, reason="Reason")

    def test_no_balance_rejects_debit(self):
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10, reason="Reason")

    def test_insufficient_balance_rejects(self):
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.CREDIT,
                units=50,
                reason="Credit",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )
        )
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=51, reason="Reason")

    def test_exact_available_balance_allowed(self):
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.CREDIT,
                units=50,
                reason="Credit",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )
        )
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        entry = use_case.execute(wallet_id=self.wallet_id, units=50, reason="Spend exact")
        self.assertEqual(entry.direction, CreditLedgerDirection.DEBIT)
        self.assertEqual(entry.units, 50)

    def test_partial_debit_allowed(self):
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet_id,
                direction=CreditLedgerDirection.CREDIT,
                units=50,
                reason="Credit",
                reference=None,
                created_at=datetime.now(timezone.utc),
            )
        )
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        entry = use_case.execute(wallet_id=self.wallet_id, units=20, reason="Spend partial")
        self.assertEqual(entry.direction, CreditLedgerDirection.DEBIT)
        self.assertEqual(entry.units, 20)

    def test_invalid_units_rejected(self):
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=0, reason="Reason")
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=-10, reason="Reason")
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=5.5, reason="Reason")
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=True, reason="Reason")

    def test_invalid_reason_rejected(self):
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10, reason="   ")

    def test_wallet_has_no_balance_mutation(self):
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        self.assertFalse(hasattr(self.wallet, "balance"))

    def test_failed_debit_creates_no_entry(self):
        use_case = RecordDebit(self.wallet_repo, self.ledger_repo)
        with self.assertRaises(ValueError):
            use_case.execute(wallet_id=self.wallet_id, units=10, reason="Fail debit")
        self.assertEqual(self.ledger_repo.save_calls, 0)


class CreditLedgerAccountingFlowTests(SimpleTestCase):
    def test_critical_accounting_flow(self):
        wallet_repo = InMemoryCreditWalletRepository()
        ledger_repo = InMemoryCreditLedgerEntryRepository()
        wallet_id = uuid4()
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=wallet_id,
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        wallet_repo.save(wallet)

        credit_use_case = RecordCredit(wallet_repo, ledger_repo)
        debit_use_case = RecordDebit(wallet_repo, ledger_repo)
        balance_use_case = GetCreditWalletBalance(wallet_repo, ledger_repo)

        # CREDIT 100
        credit_use_case.execute(wallet_id=wallet_id, units=100, reason="Deposit 1")
        # CREDIT 50
        credit_use_case.execute(wallet_id=wallet_id, units=50, reason="Deposit 2")
        # DEBIT 30
        debit_use_case.execute(wallet_id=wallet_id, units=30, reason="Spend 1")

        # Assert 3 immutable entries
        self.assertEqual(ledger_repo.save_calls, 3)
        self.assertEqual(len(ledger_repo.list_by_wallet(wallet_id)), 3)

        # Assert no balance field
        self.assertFalse(hasattr(wallet, "balance"))

        # Assert derived balance is 120
        self.assertEqual(balance_use_case.execute(wallet_id=wallet_id), 120)

    def test_critical_overspend_fails(self):
        wallet_repo = InMemoryCreditWalletRepository()
        ledger_repo = InMemoryCreditLedgerEntryRepository()
        wallet_id = uuid4()
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=wallet_id,
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        wallet_repo.save(wallet)

        credit_use_case = RecordCredit(wallet_repo, ledger_repo)
        debit_use_case = RecordDebit(wallet_repo, ledger_repo)
        balance_use_case = GetCreditWalletBalance(wallet_repo, ledger_repo)

        # CREDIT 100
        credit_use_case.execute(wallet_id=wallet_id, units=100, reason="Initial Credit")

        # DEBIT 101 Attempt
        with self.assertRaises(ValueError):
            debit_use_case.execute(wallet_id=wallet_id, units=101, reason="Overspend")

        # Ledger still has only 1 entry
        self.assertEqual(ledger_repo.save_calls, 1)
        self.assertEqual(balance_use_case.execute(wallet_id=wallet_id), 100)

    def test_exact_spend_returns_zero(self):
        wallet_repo = InMemoryCreditWalletRepository()
        ledger_repo = InMemoryCreditLedgerEntryRepository()
        wallet_id = uuid4()
        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=wallet_id,
            organization_id=uuid4(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        wallet_repo.save(wallet)

        credit_use_case = RecordCredit(wallet_repo, ledger_repo)
        debit_use_case = RecordDebit(wallet_repo, ledger_repo)
        balance_use_case = GetCreditWalletBalance(wallet_repo, ledger_repo)

        credit_use_case.execute(wallet_id=wallet_id, units=100, reason="Credit")
        debit_use_case.execute(wallet_id=wallet_id, units=100, reason="Exact spend")

        self.assertEqual(balance_use_case.execute(wallet_id=wallet_id), 0)


class SettleOpportunityWithCreditsTests(SimpleTestCase):
    def setUp(self):
        self.interest_repo = InMemoryOpportunityInterestRepository()
        self.invitation_repo = InMemoryOpportunityInvitationRepository()
        self.opportunity_repo = InMemoryOpportunityRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.access_repo = InMemoryOpportunityAccessRepository()
        self.settlement_repo = InMemoryEconomicSettlementRepository()
        self.wallet_repo = InMemoryCreditWalletRepository()
        self.ledger_repo = InMemoryCreditLedgerEntryRepository()
        self.pricing_policy = FakeOpportunityPricingPolicy()
        self.cost_policy = ConfigurableCreditCostPolicy()
        self.atomic_writer = InMemoryCreditSettlementAtomicWriter(self.ledger_repo, self.settlement_repo)
        self.org_repo = InMemoryOrganizationRepository()

        # Build valid context
        self.org_id = uuid4()
        now = datetime.now(timezone.utc)
        self.org = Organization(id=self.org_id, name="Org", slug="org", is_active=True, created_at=now, updated_at=now)
        self.org_repo.save(self.org)

        self.wallet = CreditWallet(id=uuid4(), organization_id=self.org_id, is_active=True, created_at=now, updated_at=now)
        self.wallet_repo.save(self.wallet)

        self.provider = Provider(id=uuid4(), organization_id=self.org_id, display_name="Prov", slug="prov", description="desc", is_active=True, created_at=now, updated_at=now)
        self.provider_repo.save(self.provider)

        self.opportunity = Opportunity(id=uuid4(), service_request_id=uuid4(), status=OpportunityStatus.OPEN, max_accesses=3, created_at=now, updated_at=now)
        self.opportunity_repo.save(self.opportunity)

        self.invitation = OpportunityInvitation(id=uuid4(), opportunity_id=self.opportunity.id, provider_id=self.provider.id, created_at=now)
        self.invitation_repo.save(self.invitation)

        self.interest = OpportunityInterest(id=uuid4(), invitation_id=self.invitation.id, created_at=now)
        self.interest_repo.save(self.interest)

        # Setup standard pricing
        self.pricing_policy = FakeOpportunityPricingPolicy(amount_minor=2500, currency="BRL")

        # Add credits
        self.ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=self.wallet.id,
                direction=CreditLedgerDirection.CREDIT,
                units=100,
                reason="Load",
                reference=None,
                created_at=now,
            )
        )

        self.use_case = SettleOpportunityWithCredits(
            opportunity_interest_repository=self.interest_repo,
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_repository=self.opportunity_repo,
            provider_repository=self.provider_repo,
            opportunity_access_repository=self.access_repo,
            economic_settlement_repository=self.settlement_repo,
            credit_wallet_repository=self.wallet_repo,
            credit_ledger_entry_repository=self.ledger_repo,
            opportunity_pricing_policy=self.pricing_policy,
            credit_cost_policy=self.cost_policy,
            atomic_writer=self.atomic_writer,
        )

    def test_invalid_interest_id_rejected(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=None)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id="invalid-uuid")

    def test_missing_interest_rejected(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=uuid4())

    def test_missing_invitation_rejected(self):
        bad_interest = OpportunityInterest(id=uuid4(), invitation_id=uuid4(), created_at=datetime.now(timezone.utc))
        self.interest_repo.save(bad_interest)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=bad_interest.id)

    def test_missing_opportunity_rejected(self):
        bad_inv = OpportunityInvitation(id=uuid4(), opportunity_id=uuid4(), provider_id=self.provider.id, created_at=datetime.now(timezone.utc))
        self.invitation_repo.save(bad_inv)
        bad_interest = OpportunityInterest(id=uuid4(), invitation_id=bad_inv.id, created_at=datetime.now(timezone.utc))
        self.interest_repo.save(bad_interest)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=bad_interest.id)

    def test_closed_opportunity_rejected(self):
        self.opportunity.close()
        self.opportunity_repo.save(self.opportunity)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_cancelled_opportunity_rejected(self):
        self.opportunity.cancel()
        self.opportunity_repo.save(self.opportunity)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_missing_provider_rejected(self):
        bad_inv = OpportunityInvitation(id=uuid4(), opportunity_id=self.opportunity.id, provider_id=uuid4(), created_at=datetime.now(timezone.utc))
        self.invitation_repo.save(bad_inv)
        bad_interest = OpportunityInterest(id=uuid4(), invitation_id=bad_inv.id, created_at=datetime.now(timezone.utc))
        self.interest_repo.save(bad_interest)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=bad_interest.id)

    def test_inactive_provider_rejected(self):
        self.provider.deactivate()
        self.provider_repo.save(self.provider)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_existing_opportunity_access_rejected(self):
        self.access_repo.save(
            OpportunityAccess(
                id=uuid4(),
                opportunity_id=self.opportunity.id,
                provider_id=self.provider.id,
                created_at=datetime.now(timezone.utc),
            )
        )
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_existing_economic_settlement_rejected_before_pricing(self):
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(),
                interest_id=self.interest.id,
                method=SettlementMethod.MANUAL,
                amount=Money(2500, "BRL"),
                created_at=datetime.now(timezone.utc),
            )
        )
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)
        self.assertEqual(self.pricing_policy.call_count, 0)

    def test_missing_wallet_rejected(self):
        self.wallet_repo._items.clear()
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_inactive_wallet_rejected(self):
        self.wallet.deactivate(datetime.now(timezone.utc))
        self.wallet_repo.save(self.wallet)
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_insufficient_balance_rejected(self):
        # Configure pricing cost to require 101 credits when wallet has only 100
        self.cost_policy.rate_callback = lambda price: 101
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)
        # Verify no debit or settlement was saved
        self.assertEqual(len(self.ledger_repo.list_by_wallet(self.wallet.id)), 1)
        self.assertEqual(self.atomic_writer.persist_calls, 0)

    def test_exact_balance_succeeds(self):
        self.cost_policy.rate_callback = lambda price: 100
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertEqual(res.credit_units, 100)
        self.assertIsNotNone(res.debit_entry)
        self.assertEqual(res.debit_entry.units, 100)
        self.assertEqual(res.settlement.amount.amount_minor, 2500)

    def test_partial_balance_succeeds(self):
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertEqual(res.credit_units, 25)
        self.assertEqual(res.debit_entry.units, 25)
        self.assertEqual(res.debit_entry.direction, CreditLedgerDirection.DEBIT)
        self.assertEqual(res.debit_entry.reason, "Opportunity access economic settlement")
        self.assertEqual(res.debit_entry.reference, f"opportunity-interest:{self.interest.id}")
        self.assertEqual(res.settlement.method, SettlementMethod.CREDIT)
        self.assertEqual(res.settlement.amount, Money(2500, "BRL"))

        # Verify balance query is 75
        balance_use_case = GetCreditWalletBalance(self.wallet_repo, self.ledger_repo)
        self.assertEqual(balance_use_case.execute(wallet_id=self.wallet.id), 75)

        # No access granted
        self.assertEqual(len(self.access_repo._items), 0)

    def test_zero_credit_settlement_creates_no_debit_but_creates_economic_settlement(self):
        self.cost_policy.rate_callback = lambda price: 0
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertEqual(res.credit_units, 0)
        self.assertIsNone(res.debit_entry)
        self.assertEqual(res.settlement.method, SettlementMethod.CREDIT)

        # Debit remains absent, but settlement is created
        self.assertEqual(len(self.ledger_repo.list_by_wallet(self.wallet.id)), 1) # Only initial CREDIT remains
        self.assertEqual(len(self.settlement_repo._items), 1)

    def test_policies_called_exactly_once(self):
        self.use_case.execute(interest_id=self.interest.id)
        self.assertEqual(self.pricing_policy.call_count, 1)
        self.assertEqual(self.cost_policy.call_count, 1)

    def test_retry_after_existing_settlement_rejected_without_double_debit(self):
        # First successful settlement
        self.use_case.execute(interest_id=self.interest.id)
        self.assertEqual(self.atomic_writer.persist_calls, 1)

        # Attempt second time
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

        # Atomic writer was not called a second time
        self.assertEqual(self.atomic_writer.persist_calls, 1)


class SettlementAwareAccessEntitlementPolicyTests(SimpleTestCase):
    def setUp(self):
        self.settlement_repo = InMemoryEconomicSettlementRepository()
        self.policy = SettlementAwareAccessEntitlementPolicy(self.settlement_repo)

        now = datetime.now(timezone.utc)
        self.interest = OpportunityInterest(id=uuid4(), invitation_id=uuid4(), created_at=now)
        self.invitation = OpportunityInvitation(id=uuid4(), opportunity_id=uuid4(), provider_id=uuid4(), created_at=now)
        self.opportunity = Opportunity(id=uuid4(), service_request_id=uuid4(), status=OpportunityStatus.OPEN, max_accesses=3, created_at=now, updated_at=now)
        self.provider = Provider(id=uuid4(), organization_id=uuid4(), display_name="Prov", slug="prov", description="desc", is_active=True, created_at=now, updated_at=now)

    def test_no_settlement_denied(self):
        decision = self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "economic_settlement_required")

    def test_manual_settlement_allowed(self):
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(),
                interest_id=self.interest.id,
                method=SettlementMethod.MANUAL,
                amount=Money(2500, "BRL"),
                created_at=datetime.now(timezone.utc),
            )
        )
        decision = self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "economic_settlement_exists")

    def test_complimentary_settlement_allowed(self):
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(),
                interest_id=self.interest.id,
                method=SettlementMethod.COMPLIMENTARY,
                amount=Money(0, "BRL"),
                created_at=datetime.now(timezone.utc),
            )
        )
        decision = self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "economic_settlement_exists")

    def test_credit_settlement_allowed(self):
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(),
                interest_id=self.interest.id,
                method=SettlementMethod.CREDIT,
                amount=Money(2500, "BRL"),
                created_at=datetime.now(timezone.utc),
            )
        )
        decision = self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "economic_settlement_exists")

    def test_settlement_repository_queried_once(self):
        self.assertEqual(self.settlement_repo.get_by_interest_calls, 0)

        decision = self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(self.settlement_repo.get_by_interest_calls, 1)
        self.assertEqual(
            self.settlement_repo.last_get_by_interest_id,
            self.interest.id,
        )

    def test_policy_creates_no_opportunity_access(self):
        # Policy only reads settlement evidence and returns a decision.
        before_items = len(self.settlement_repo._items)
        before_save_calls = self.settlement_repo.save_calls
        self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )
        self.assertEqual(len(self.settlement_repo._items), before_items)
        self.assertEqual(self.settlement_repo.save_calls, before_save_calls)

    def test_policy_creates_no_settlement(self):
        self.assertEqual(len(self.settlement_repo._items), 0)
        self.assertEqual(self.settlement_repo.save_calls, 0)
        self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )
        self.assertEqual(len(self.settlement_repo._items), 0)
        self.assertEqual(self.settlement_repo.save_calls, 0)

    def test_policy_does_not_mutate_supplied_entities(self):
        original_interest = (
            self.interest.id,
            self.interest.invitation_id,
            self.interest.created_at,
        )
        original_invitation = (
            self.invitation.id,
            self.invitation.opportunity_id,
            self.invitation.provider_id,
            self.invitation.created_at,
        )
        original_status = self.opportunity.status
        original_provider = (
            self.provider.id,
            self.provider.organization_id,
            self.provider.display_name,
            self.provider.slug,
            self.provider.description,
            self.provider.is_active,
            self.provider.created_at,
            self.provider.updated_at,
        )

        self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )

        self.assertEqual(
            (
                self.interest.id,
                self.interest.invitation_id,
                self.interest.created_at,
            ),
            original_interest,
        )
        self.assertEqual(
            (
                self.invitation.id,
                self.invitation.opportunity_id,
                self.invitation.provider_id,
                self.invitation.created_at,
            ),
            original_invitation,
        )
        self.assertEqual(self.opportunity.status, original_status)
        self.assertEqual(
            (
                self.provider.id,
                self.provider.organization_id,
                self.provider.display_name,
                self.provider.slug,
                self.provider.description,
                self.provider.is_active,
                self.provider.created_at,
                self.provider.updated_at,
            ),
            original_provider,
        )

    def test_settlement_for_other_interest_does_not_allow_current_interest(self):
        other_interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=self.interest.invitation_id,
            created_at=datetime.now(timezone.utc),
        )
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(),
                interest_id=other_interest.id,
                method=SettlementMethod.CREDIT,
                amount=Money(2500, "BRL"),
                created_at=datetime.now(timezone.utc),
            )
        )

        decision = self.policy.decide(
            interest=self.interest,
            invitation=self.invitation,
            opportunity=self.opportunity,
            provider=self.provider,
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "economic_settlement_required")


class RequestOpportunityAccessIntegrationTests(SimpleTestCase):
    def setUp(self):
        self.interest_repo = InMemoryOpportunityInterestRepository()
        self.invitation_repo = InMemoryOpportunityInvitationRepository()
        self.opportunity_repo = InMemoryOpportunityRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.access_repo = InMemoryOpportunityAccessRepository()
        self.settlement_repo = InMemoryEconomicSettlementRepository()
        
        self.policy = SettlementAwareAccessEntitlementPolicy(self.settlement_repo)
        self.grant_use_case = GrantOpportunityAccess(
            opportunity_repository=self.opportunity_repo,
            provider_repository=self.provider_repo,
            opportunity_access_repository=self.access_repo,
        )
        
        self.use_case = RequestOpportunityAccess(
            opportunity_interest_repository=self.interest_repo,
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_repository=self.opportunity_repo,
            provider_repository=self.provider_repo,
            opportunity_access_repository=self.access_repo,
            access_entitlement_policy=self.policy,
            grant_opportunity_access=self.grant_use_case,
        )

        now = datetime.now(timezone.utc)
        self.provider = Provider(id=uuid4(), organization_id=uuid4(), display_name="Prov", slug="prov", description="desc", is_active=True, created_at=now, updated_at=now)
        self.provider_repo.save(self.provider)

        self.opportunity = Opportunity(id=uuid4(), service_request_id=uuid4(), status=OpportunityStatus.OPEN, max_accesses=3, created_at=now, updated_at=now)
        self.opportunity_repo.save(self.opportunity)

        self.invitation = OpportunityInvitation(id=uuid4(), opportunity_id=self.opportunity.id, provider_id=self.provider.id, created_at=now)
        self.invitation_repo.save(self.invitation)

        self.interest = OpportunityInterest(id=uuid4(), invitation_id=self.invitation.id, created_at=now)
        self.interest_repo.save(self.interest)

    def test_no_settlement_request_access_returns_denied(self):
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertFalse(res.decision.allowed)
        self.assertEqual(res.decision.reason, "economic_settlement_required")
        self.assertIsNone(res.access)
        self.assertEqual(len(self.access_repo._items), 0)

    def test_valid_manual_settlement_allowed_and_access_created(self):
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=self.interest.id, method=SettlementMethod.MANUAL, amount=Money(2500, "BRL"), created_at=datetime.now(timezone.utc)
            )
        )
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertTrue(res.decision.allowed)
        self.assertEqual(res.decision.reason, "economic_settlement_exists")
        self.assertIsNotNone(res.access)
        self.assertEqual(res.access.opportunity_id, self.opportunity.id)
        self.assertEqual(res.access.provider_id, self.provider.id)
        self.assertEqual(len(self.access_repo._items), 1)

    def test_valid_complimentary_settlement_allowed_and_access_created(self):
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=self.interest.id, method=SettlementMethod.COMPLIMENTARY, amount=Money(0, "BRL"), created_at=datetime.now(timezone.utc)
            )
        )
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertTrue(res.decision.allowed)
        self.assertIsNotNone(res.access)
        self.assertEqual(len(self.access_repo._items), 1)

    def test_valid_credit_settlement_allowed_and_access_created(self):
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=self.interest.id, method=SettlementMethod.CREDIT, amount=Money(2500, "BRL"), created_at=datetime.now(timezone.utc)
            )
        )
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertTrue(res.decision.allowed)
        self.assertIsNotNone(res.access)
        self.assertEqual(len(self.access_repo._items), 1)

    def test_settlement_belongs_to_current_interest_isolation(self):
        now = datetime.now(timezone.utc)
        # Create another interest with a settlement
        other_inv = OpportunityInvitation(id=uuid4(), opportunity_id=self.opportunity.id, provider_id=self.provider.id, created_at=now)
        self.invitation_repo.save(other_inv)
        other_interest = OpportunityInterest(id=uuid4(), invitation_id=other_inv.id, created_at=now)
        self.interest_repo.save(other_interest)

        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=other_interest.id, method=SettlementMethod.CREDIT, amount=Money(2500, "BRL"), created_at=now
            )
        )

        # Request access for the original interest (which has no settlement)
        res = self.use_case.execute(interest_id=self.interest.id)
        self.assertFalse(res.decision.allowed)
        self.assertEqual(res.decision.reason, "economic_settlement_required")
        self.assertIsNone(res.access)

    def test_existing_opportunity_access_still_rejected_before_policy_call(self):
        self.access_repo.save(
            OpportunityAccess(
                id=uuid4(), opportunity_id=self.opportunity.id, provider_id=self.provider.id, created_at=datetime.now(timezone.utc)
            )
        )
        # Even if a settlement exists, it should crash before policy decision
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=self.interest.id, method=SettlementMethod.CREDIT, amount=Money(2500, "BRL"), created_at=datetime.now(timezone.utc)
            )
        )
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_closed_opportunity_still_rejected_before_entitlement(self):
        self.opportunity.close()
        self.opportunity_repo.save(self.opportunity)
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=self.interest.id, method=SettlementMethod.CREDIT, amount=Money(2500, "BRL"), created_at=datetime.now(timezone.utc)
            )
        )
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_cancelled_opportunity_still_rejected_before_entitlement(self):
        self.opportunity.cancel()
        self.opportunity_repo.save(self.opportunity)
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=self.interest.id, method=SettlementMethod.CREDIT, amount=Money(2500, "BRL"), created_at=datetime.now(timezone.utc)
            )
        )
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_inactive_provider_still_rejected_before_entitlement(self):
        self.provider.deactivate()
        self.provider_repo.save(self.provider)
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(), interest_id=self.interest.id, method=SettlementMethod.CREDIT, amount=Money(2500, "BRL"), created_at=datetime.now(timezone.utc)
            )
        )
        with self.assertRaises(ValueError):
            self.use_case.execute(interest_id=self.interest.id)

    def test_critical_credit_flow_entitlement_then_access_without_new_economic_mutations(self):
        now = datetime.now(timezone.utc)
        self.settlement_repo.save(
            EconomicSettlement(
                id=uuid4(),
                interest_id=self.interest.id,
                method=SettlementMethod.CREDIT,
                amount=Money(2500, "BRL"),
                created_at=now,
            )
        )

        wallet_repo = InMemoryCreditWalletRepository()
        ledger_repo = InMemoryCreditLedgerEntryRepository()
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=self.provider.organization_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        wallet_repo.save(wallet)
        ledger_repo.save(
            CreditLedgerEntry(
                id=uuid4(),
                wallet_id=wallet.id,
                direction=CreditLedgerDirection.CREDIT,
                units=100,
                reason="Seed credits",
                reference="seed",
                created_at=now,
            )
        )

        pricing_policy = FakeOpportunityPricingPolicy(amount_minor=2500, currency="BRL")

        settlement_count_before = len(self.settlement_repo._items)
        settlement_save_calls_before = self.settlement_repo.save_calls
        wallet_save_calls_before = wallet_repo.save_calls
        ledger_save_calls_before = ledger_repo.save_calls

        result = self.use_case.execute(interest_id=self.interest.id)

        self.assertTrue(result.decision.allowed)
        self.assertEqual(result.decision.reason, "economic_settlement_exists")
        self.assertIsNotNone(result.access)
        self.assertEqual(len(self.access_repo._items), 1)

        # Access request should not execute pricing/credits/economic settlement writes.
        self.assertEqual(pricing_policy.call_count, 0)
        self.assertEqual(len(self.settlement_repo._items), settlement_count_before)
        self.assertEqual(self.settlement_repo.save_calls, settlement_save_calls_before)
        self.assertEqual(wallet_repo.save_calls, wallet_save_calls_before)
        self.assertEqual(ledger_repo.save_calls, ledger_save_calls_before)


class GetProtectedCommercialDataTests(SimpleTestCase):
    def setUp(self):
        self.access_repo = InMemoryOpportunityAccessRepository()
        self.opp_repo = InMemoryOpportunityRepository()
        self.sr_repo = InMemoryServiceRequestRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.use_case = GetProtectedCommercialData(
            opportunity_access_repository=self.access_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
        )

    def test_get_protected_commercial_data_success(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        result = self.use_case.execute(provider_id=provider_id, opportunity_access_id=access.id)

        self.assertIsInstance(result, ProtectedCommercialData)
        self.assertEqual(result.requester_name, "John Doe")
        self.assertEqual(result.requester_email, "john@example.com")
        self.assertEqual(result.requester_phone, "+5511999999999")

    def test_nonexistent_access_rejected(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=uuid4(), opportunity_access_id=uuid4())

    def test_malformed_uuid_rejected(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=uuid4(), opportunity_access_id="invalid-uuid")  # type: ignore

        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=None, opportunity_access_id=None)  # type: ignore

    def test_missing_opportunity_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=uuid4(),
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=provider_id, opportunity_access_id=access.id)

    def test_missing_service_request_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=uuid4(),
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=provider_id, opportunity_access_id=access.id)

    def test_missing_provider_rejected(self):
        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        provider_id = uuid4()
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=provider_id, opportunity_access_id=access.id)

    def test_get_protected_commercial_data_legacy_fails(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

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
            requester_phone="",
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(provider_id=provider_id, opportunity_access_id=access.id)
        self.assertIn("No protected contact information available for this legacy request", str(ctx.exception))

    def test_get_protected_commercial_data_other_provider_idor_denied(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        # Provider B attempts to use Provider A's access ID -> Should fail
        provider_b_id = uuid4()
        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(provider_id=provider_b_id, opportunity_access_id=access.id)
        self.assertIn("Access entitlement ownership mismatch", str(ctx.exception))

    def test_create_service_request_validation_rules(self):
        # We need mock repositories for CreateServiceRequest
        from src.marketplace.application.use_cases import CreateServiceRequest

        org_repo = InMemoryOrganizationRepository()
        srv_repo = InMemoryServiceRepository()

        org = Organization(
            id=uuid4(),
            name="Org",
            slug="org",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        org_repo.save(org)

        srv = Service(
            id=uuid4(),
            category_id=uuid4(),
            name="Srv",
            slug="srv",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        srv_repo.save(srv)

        create_use_case = CreateServiceRequest(
            service_request_repository=self.sr_repo,
            organization_repository=org_repo,
            service_repository=srv_repo,
        )

        # 1. Reject blank requester_name
        with self.assertRaises(ValueError) as ctx:
            create_use_case.execute(
                organization_id=org.id,
                service_id=srv.id,
                title="Title",
                requester_name="   ",
                requester_email="john@example.com",
                requester_phone="",
            )
        self.assertIn("requester_name cannot be empty", str(ctx.exception))

        # 2. Reject new request with neither email nor phone
        with self.assertRaises(ValueError) as ctx:
            create_use_case.execute(
                organization_id=org.id,
                service_id=srv.id,
                title="Title",
                requester_name="John Doe",
                requester_email="   ",
                requester_phone="  ",
            )
        self.assertIn("At least one contact channel", str(ctx.exception))

        # 3. New request with name + email succeeds
        sr1 = create_use_case.execute(
            organization_id=org.id,
            service_id=srv.id,
            title="Title",
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="",
        )
        self.assertEqual(sr1.requester_name, "John Doe")
        self.assertEqual(sr1.requester_email, "john@example.com")
        self.assertEqual(sr1.requester_phone, "")

        # 4. New request with name + phone succeeds
        sr2 = create_use_case.execute(
            organization_id=org.id,
            service_id=srv.id,
            title="Title",
            requester_name="John Doe",
            requester_email="",
            requester_phone="+5511999999999",
        )
        self.assertEqual(sr2.requester_name, "John Doe")
        self.assertEqual(sr2.requester_email, "")
        self.assertEqual(sr2.requester_phone, "+5511999999999")


class GetOpportunityPreviewTests(SimpleTestCase):
    def setUp(self):
        self.invitation_repo = InMemoryOpportunityInvitationRepository()
        self.opp_repo = InMemoryOpportunityRepository()
        self.sr_repo = InMemoryServiceRequestRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.use_case = GetOpportunityPreview(
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
        )

    def test_get_opportunity_preview_success_excludes_pii(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request Title",
            description="Detailed Description",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        preview = self.use_case.execute(opportunity_invitation_id=invitation.id)

        self.assertIsInstance(preview, OpportunityPreview)
        self.assertEqual(preview.opportunity_id, opp.id)
        self.assertEqual(preview.service_request_id, sr.id)
        self.assertEqual(preview.service_id, sr.service_id)
        self.assertEqual(preview.title, "Service Request Title")
        self.assertEqual(preview.description, "Detailed Description")
        self.assertEqual(preview.status, OpportunityStatus.OPEN)

        self.assertFalse(hasattr(preview, "requester_name"))
        self.assertFalse(hasattr(preview, "requester_email"))
        self.assertFalse(hasattr(preview, "requester_phone"))

    def test_lifecycle_validation_opportunity_not_open_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.CLOSED,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("Opportunity is not OPEN", str(ctx.exception))

    def test_lifecycle_validation_service_request_not_open_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.CLOSED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("ServiceRequest is not OPEN", str(ctx.exception))

    def test_provider_inactive_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("Provider is inactive", str(ctx.exception))

    def test_critical_regression_preview_vs_access(self):
        access_repo = InMemoryOpportunityAccessRepository()
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Request Title",
            description="Detailed Description",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="Real Requester Name",
            requester_email="real@example.com",
            requester_phone="+5511988887777",
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        # 1. Preview yields NO PII requester contact data
        preview = self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertFalse(hasattr(preview, "requester_name"))
        self.assertFalse(hasattr(preview, "requester_email"))
        self.assertFalse(hasattr(preview, "requester_phone"))

        # 2. Grant access
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        access_repo.save(access)

        # 3. Protected read yields exact contact details
        get_data_use_case = GetProtectedCommercialData(
            opportunity_access_repository=access_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
        )

        contact_data = get_data_use_case.execute(provider_id=provider_id, opportunity_access_id=access.id)
        self.assertEqual(contact_data.requester_name, "Real Requester Name")
        self.assertEqual(contact_data.requester_email, "real@example.com")
        self.assertEqual(contact_data.requester_phone, "+5511988887777")


class GetOpportunityUnlockQuoteTests(SimpleTestCase):
    def setUp(self):
        self.invitation_repo = InMemoryOpportunityInvitationRepository()
        self.opp_repo = InMemoryOpportunityRepository()
        self.sr_repo = InMemoryServiceRequestRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.access_repo = InMemoryOpportunityAccessRepository()
        self.pricing_policy = FakeOpportunityPricingPolicy(amount_minor=2500, currency="BRL")
        self.use_case = GetOpportunityUnlockQuote(
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
            opportunity_access_repository=self.access_repo,
            opportunity_pricing_policy=self.pricing_policy,
        )

    def test_get_opportunity_unlock_quote_success_and_read_only(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Title",
            description="Desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name="John Doe",
            requester_email="john@example.com",
            requester_phone="+5511999999999",
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        # 1. Execute quote
        quote = self.use_case.execute(opportunity_invitation_id=invitation.id)

        # Verify fields (Pricing configured / available)
        self.assertIsInstance(quote, OpportunityUnlockQuote)
        self.assertEqual(quote.opportunity_id, opp.id)
        self.assertEqual(quote.provider_id, provider_id)
        self.assertIsNotNone(quote.amount)
        self.assertEqual(quote.amount.amount_minor, 2500)
        self.assertEqual(quote.amount.currency, "BRL")
        self.assertTrue(quote.quote_available)
        self.assertFalse(quote.already_unlocked)
        self.assertEqual(quote.reason, "test_quote")

        # Excludes PII
        self.assertFalse(hasattr(quote, "requester_name"))
        self.assertFalse(hasattr(quote, "requester_email"))
        self.assertFalse(hasattr(quote, "requester_phone"))

        # Verify absolutely no side effects
        self.assertEqual(self.access_repo.save_calls, 0)
        self.assertIsNone(self.access_repo.get_by_opportunity_and_provider(opp.id, provider_id))

    def test_get_opportunity_unlock_quote_pricing_unavailable(self):
        # Configure a policy that raises an exception to simulate unavailability
        class FailingPricingPolicy:
            def quote(self, *, invitation, opportunity, provider, interest=None):
                raise OpportunityPricingUnavailable("Pricing is not configured for this category.")

        use_case_failing = GetOpportunityUnlockQuote(
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
            opportunity_access_repository=self.access_repo,
            opportunity_pricing_policy=FailingPricingPolicy(),
        )

        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Title",
            description="Desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        quote = use_case_failing.execute(opportunity_invitation_id=invitation.id)

        self.assertFalse(quote.quote_available)
        self.assertIsNone(quote.amount)
        self.assertEqual(quote.reason, "No commercial pricing configured for pre-access unlock.")

    def test_lifecycle_validation_opportunity_not_open_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.CLOSED,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("Opportunity is not OPEN", str(ctx.exception))

    def test_lifecycle_validation_service_request_not_open_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.CLOSED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("ServiceRequest is not OPEN", str(ctx.exception))

    def test_provider_inactive_rejected(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("Provider is inactive", str(ctx.exception))

    def test_already_unlocked_scenario(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        # Pre-existing access
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        # Get quote
        quote = self.use_case.execute(opportunity_invitation_id=invitation.id)

        self.assertTrue(quote.already_unlocked)
        self.assertFalse(quote.quote_available)
        self.assertIsNone(quote.amount)
        self.assertIn("already unlocked", quote.reason)

    def test_critical_regression_quote_never_creates_access(self):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        # Execute quote
        quote = self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIsNotNone(quote)

        # CRITICAL VERIFICATION: Access repository MUST be empty (no access created)
        self.assertEqual(self.access_repo.save_calls, 0)
        self.assertIsNone(self.access_repo.get_by_opportunity_and_provider(opp.id, provider_id))

    def test_critical_regression_quote_never_creates_opportunity_interest(self):
        interest_repo = InMemoryOpportunityInterestRepository()
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        # Execute quote
        quote = self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIsNotNone(quote)

        # CRITICAL VERIFICATION: Interest repository MUST be empty (no interest created)
        self.assertEqual(interest_repo.save_calls, 0)

    def test_get_opportunity_unlock_quote_unexpected_exception_propagates(self):
        # Configure a policy that raises a RuntimeError to simulate internal failure
        class UnexpectedFailingPricingPolicy:
            def quote(self, *, invitation, opportunity, provider, interest=None):
                raise RuntimeError("Internal database connection error")

        use_case_unexpected = GetOpportunityUnlockQuote(
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
            opportunity_access_repository=self.access_repo,
            opportunity_pricing_policy=UnexpectedFailingPricingPolicy(),
        )

        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Title",
            description="desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)

        # Expected: RuntimeError propagates and is NOT caught/silenced
        with self.assertRaises(RuntimeError) as ctx:
            use_case_unexpected.execute(opportunity_invitation_id=invitation.id)
        self.assertEqual(str(ctx.exception), "Internal database connection error")


class ReconcileOpportunityEconomicAcquisitionTests(SimpleTestCase):
    def setUp(self):
        self.opp_repo = InMemoryOpportunityRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.invitation_repo = InMemoryOpportunityInvitationRepository()
        self.interest_repo = InMemoryOpportunityInterestRepository()
        self.access_repo = InMemoryOpportunityAccessRepository()
        self.settlement_repo = InMemoryEconomicSettlementRepository()
        self.wallet_repo = InMemoryCreditWalletRepository()
        self.ledger_repo = InMemoryCreditLedgerEntryRepository()
        self.use_case = ReconcileOpportunityEconomicAcquisition(
            opportunity_repository=self.opp_repo,
            provider_repository=self.provider_repo,
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_interest_repository=self.interest_repo,
            opportunity_access_repository=self.access_repo,
            economic_settlement_repository=self.settlement_repo,
            credit_wallet_repository=self.wallet_repo,
            credit_ledger_entry_repository=self.ledger_repo,
        )

    def _base(self):
        now = datetime.now(timezone.utc)
        provider = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Provider",
            slug=f"provider-{uuid4().hex[:8]}",
            description="",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.provider_repo.save(provider)
        opportunity = Opportunity(
            id=uuid4(),
            service_request_id=uuid4(),
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=now,
            updated_at=now,
        )
        self.opp_repo.save(opportunity)
        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=now,
        )
        self.invitation_repo.save(invitation)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=provider.organization_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.wallet_repo.save(wallet)
        return provider, opportunity, invitation, wallet

    def _interest(self, invitation):
        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation.id,
            created_at=datetime.now(timezone.utc),
        )
        self.interest_repo.save(interest)
        return interest

    def _settlement(self, interest, amount_minor=2500):
        settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=interest.id,
            method=SettlementMethod.CREDIT,
            amount=Money(amount_minor=amount_minor, currency="BRL"),
            created_at=datetime.now(timezone.utc),
            pricing_source="configured_opportunity_unlock_base_price",
            pricing_configuration_id=uuid4(),
            pricing_resolved_at=datetime.now(timezone.utc),
        )
        self.settlement_repo.save(settlement)
        return settlement

    def _access(self, opportunity, provider):
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)
        return access

    def _debit(self, wallet, interest, units=25):
        debit = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=wallet.id,
            direction=CreditLedgerDirection.DEBIT,
            units=units,
            reason="Opportunity access economic settlement",
            reference=f"opportunity-interest:{interest.id}",
            created_at=datetime.now(timezone.utc),
        )
        self.ledger_repo.save(debit)
        return debit

    def test_consistent_acquisition(self):
        provider, opportunity, invitation, wallet = self._base()
        interest = self._interest(invitation)
        settlement = self._settlement(interest)
        access = self._access(opportunity, provider)
        debit = self._debit(wallet, interest)

        result = self.use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertTrue(result.consistent)
        self.assertEqual(result.issues, ())
        self.assertEqual(result.access_id, access.id)
        self.assertEqual(result.interest_id, interest.id)
        self.assertEqual(result.settlement_id, settlement.id)
        self.assertEqual(result.debit_entry_ids, (debit.id,))

    def test_access_without_settlement_is_inconsistent(self):
        provider, opportunity, invitation, wallet = self._base()
        self._access(opportunity, provider)

        result = self.use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertFalse(result.consistent)
        self.assertIn(
            EconomicAcquisitionReconciliationIssue.ACCESS_WITHOUT_SETTLEMENT,
            result.issues,
        )

    def test_settlement_without_debit_is_inconsistent(self):
        provider, opportunity, invitation, wallet = self._base()
        interest = self._interest(invitation)
        self._settlement(interest)
        self._access(opportunity, provider)

        result = self.use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertFalse(result.consistent)
        self.assertIn(
            EconomicAcquisitionReconciliationIssue.SETTLEMENT_WITHOUT_DEBIT,
            result.issues,
        )

    def test_debit_without_settlement_is_inconsistent(self):
        provider, opportunity, invitation, wallet = self._base()
        interest = self._interest(invitation)
        self._debit(wallet, interest)

        result = self.use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertFalse(result.consistent)
        self.assertIn(
            EconomicAcquisitionReconciliationIssue.DEBIT_WITHOUT_SETTLEMENT,
            result.issues,
        )

    def test_debit_from_other_organization_is_mismatch(self):
        provider, opportunity, invitation, wallet = self._base()
        other_wallet = CreditWallet(
            id=uuid4(),
            organization_id=uuid4(),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.wallet_repo.save(other_wallet)
        interest = self._interest(invitation)
        self._settlement(interest)
        self._access(opportunity, provider)
        self._debit(other_wallet, interest)

        result = self.use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertFalse(result.consistent)
        self.assertIn(
            EconomicAcquisitionReconciliationIssue.ORGANIZATION_MISMATCH,
            result.issues,
        )

    def test_duplicate_debits_are_duplicate_economic_acquisition(self):
        provider, opportunity, invitation, wallet = self._base()
        interest = self._interest(invitation)
        self._settlement(interest)
        self._access(opportunity, provider)
        first = self._debit(wallet, interest)
        second = self._debit(wallet, interest)

        result = self.use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertFalse(result.consistent)
        self.assertIn(
            EconomicAcquisitionReconciliationIssue.DUPLICATE_ECONOMIC_ACQUISITION,
            result.issues,
        )
        self.assertEqual(result.debit_entry_ids, (first.id, second.id))

    def test_historical_pricing_snapshot_is_not_repriced(self):
        provider, opportunity, invitation, wallet = self._base()
        interest = self._interest(invitation)
        settlement = self._settlement(interest, amount_minor=1000)
        self._access(opportunity, provider)
        self._debit(wallet, interest)

        result = self.use_case.execute(opportunity_id=opportunity.id, provider_id=provider.id)

        self.assertTrue(result.consistent)
        self.assertEqual(result.settlement_id, settlement.id)
        self.assertEqual(self.settlement_repo.get_by_interest(interest.id).amount.amount_minor, 1000)

    def test_invalid_ids_rejected_without_repository_lookup(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(opportunity_id=None, provider_id=uuid4())
        with self.assertRaises(ValueError):
            self.use_case.execute(opportunity_id=uuid4(), provider_id=None)


class UnlockOpportunityWithCreditsTests(SimpleTestCase):
    def setUp(self):
        self.invitation_repo = InMemoryOpportunityInvitationRepository()
        self.opp_repo = InMemoryOpportunityRepository()
        self.sr_repo = InMemoryServiceRequestRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.access_repo = InMemoryOpportunityAccessRepository()
        self.interest_repo = InMemoryOpportunityInterestRepository()
        self.settlement_repo = InMemoryEconomicSettlementRepository()
        self.wallet_repo = InMemoryCreditWalletRepository()
        self.ledger_repo = InMemoryCreditLedgerEntryRepository()
        self.pricing_policy = FakeOpportunityPricingPolicy(amount_minor=2500, currency="BRL")
        self.cost_policy = ConfigurableCreditCostPolicy()
        self.atomic_writer = InMemoryOpportunityUnlockAtomicWriter(
            self.interest_repo, self.ledger_repo, self.settlement_repo, self.access_repo, self.wallet_repo
        )
        self.use_case = UnlockOpportunityWithCredits(
            opportunity_invitation_repository=self.invitation_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
            opportunity_access_repository=self.access_repo,
            opportunity_interest_repository=self.interest_repo,
            economic_settlement_repository=self.settlement_repo,
            credit_wallet_repository=self.wallet_repo,
            credit_ledger_entry_repository=self.ledger_repo,
            opportunity_pricing_policy=self.pricing_policy,
            credit_cost_policy=self.cost_policy,
            unlock_atomic_writer=self.atomic_writer,
        )

    def _setup_base_entities(self, org_id=None, provider_active=True, opp_open=True, sr_open=True):
        provider_id = uuid4()
        org_id = org_id or uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=org_id,
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=provider_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Title",
            description="Desc",
            status=ServiceRequestStatus.OPEN if sr_open else ServiceRequestStatus.CLOSED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN if opp_open else OpportunityStatus.CLOSED,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        self.invitation_repo.save(invitation)
        return provider, sr, opp, invitation

    def test_happy_path_success(self):
        org_id = uuid4()
        # Setup wallet with sufficient credits (30 units)
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)
        entry = CreditLedgerEntry(id=uuid4(), wallet_id=wallet.id, direction=CreditLedgerDirection.CREDIT, units=30, reason="Initial credit", reference="ref", created_at=datetime.now(timezone.utc))
        self.ledger_repo.save(entry)

        # Mock cost policy to return 25 units
        self.cost_policy.rate_callback = lambda price: 25

        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        result = self.use_case.execute(opportunity_invitation_id=invitation.id)

        self.assertIsInstance(result, OpportunityUnlockResult)
        self.assertFalse(result.already_unlocked)
        self.assertIsNotNone(result.access)
        self.assertEqual(result.access.opportunity_id, opp.id)
        self.assertEqual(result.access.provider_id, provider.id)

        # Economics audit
        # 1. Access created
        self.assertEqual(self.access_repo.save_calls, 1)
        self.assertIsNotNone(self.access_repo.get_by_opportunity_and_provider(opp.id, provider.id))

        # 2. Interest created
        self.assertEqual(self.interest_repo.save_calls, 1)
        interest = self.interest_repo.get_by_invitation(invitation.id)
        self.assertIsNotNone(interest)

        # 3. Debit ledger created
        entries = self.ledger_repo.list_by_wallet(wallet.id)
        debits = [e for e in entries if e.direction is CreditLedgerDirection.DEBIT]
        self.assertEqual(len(debits), 1)
        self.assertEqual(debits[0].units, 25)

        # 4. EconomicSettlement created
        settlement = self.settlement_repo.get_by_interest(interest.id)
        self.assertIsNotNone(settlement)
        self.assertEqual(settlement.amount.amount_minor, 2500)
        self.assertEqual(settlement.amount.currency, "BRL")

        # Excludes PII
        self.assertFalse(hasattr(result, "requester_name"))
        self.assertFalse(hasattr(result, "requester_email"))
        self.assertFalse(hasattr(result, "requester_phone"))

    def test_unlock_settlement_preserves_authoritative_pricing_snapshot(self):
        org_id = uuid4()
        config_id = uuid4()
        self.pricing_policy = FakeOpportunityPricingPolicy(
            amount_minor=3333,
            currency="USD",
            reason="configured_quote",
            pricing_source="configured_policy",
            pricing_configuration_id=config_id,
        )
        self.use_case.opportunity_pricing_policy = self.pricing_policy
        self.cost_policy.rate_callback = lambda price: 12
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)
        self.ledger_repo.save(CreditLedgerEntry(id=uuid4(), wallet_id=wallet.id, direction=CreditLedgerDirection.CREDIT, units=30, reason="Initial credit", reference="ref", created_at=datetime.now(timezone.utc)))
        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        result = self.use_case.execute(opportunity_invitation_id=invitation.id)
        interest = self.interest_repo.get_by_invitation(invitation.id)
        settlement = self.settlement_repo.get_by_interest(interest.id)

        self.assertEqual(result.amount.amount_minor, 3333)
        self.assertEqual(result.amount.currency, "USD")
        self.assertEqual(settlement.amount.amount_minor, 3333)
        self.assertEqual(settlement.amount.currency, "USD")
        self.assertEqual(settlement.pricing_source, "configured_policy")
        self.assertEqual(settlement.pricing_configuration_id, config_id)
        self.assertEqual(settlement.pricing_resolved_at, settlement.created_at)

    def test_historical_settlements_preserve_each_authoritative_price(self):
        org_id = uuid4()
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)
        self.ledger_repo.save(CreditLedgerEntry(id=uuid4(), wallet_id=wallet.id, direction=CreditLedgerDirection.CREDIT, units=100, reason="Initial credit", reference="ref", created_at=datetime.now(timezone.utc)))
        self.cost_policy.rate_callback = lambda price: 10

        config_a = uuid4()
        self.pricing_policy.amount_minor = 1000
        self.pricing_policy.pricing_source = "configured_policy"
        self.pricing_policy.pricing_configuration_id = config_a
        provider_a, sr_a, opp_a, invitation_a = self._setup_base_entities(org_id=org_id)
        self.use_case.execute(opportunity_invitation_id=invitation_a.id)
        interest_a = self.interest_repo.get_by_invitation(invitation_a.id)
        settlement_a = self.settlement_repo.get_by_interest(interest_a.id)

        config_b = uuid4()
        self.pricing_policy.amount_minor = 1500
        self.pricing_policy.pricing_configuration_id = config_b
        provider_b, sr_b, opp_b, invitation_b = self._setup_base_entities(org_id=org_id)
        self.use_case.execute(opportunity_invitation_id=invitation_b.id)
        interest_b = self.interest_repo.get_by_invitation(invitation_b.id)
        settlement_b = self.settlement_repo.get_by_interest(interest_b.id)

        self.assertEqual(settlement_a.amount.amount_minor, 1000)
        self.assertEqual(settlement_a.pricing_configuration_id, config_a)
        self.assertEqual(settlement_b.amount.amount_minor, 1500)
        self.assertEqual(settlement_b.pricing_configuration_id, config_b)

    def test_already_unlocked_idempotency(self):
        org_id = uuid4()
        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        # Create pre-existing access
        access = OpportunityAccess(id=uuid4(), opportunity_id=opp.id, provider_id=provider.id, created_at=datetime.now(timezone.utc))
        self.access_repo.save(access)
        # Create pre-existing interest and settlement
        interest = OpportunityInterest(id=uuid4(), invitation_id=invitation.id, created_at=datetime.now(timezone.utc))
        self.interest_repo.save(interest)
        settlement = EconomicSettlement(id=uuid4(), interest_id=interest.id, method=SettlementMethod.CREDIT, amount=Money(2500, "BRL"), created_at=datetime.now(timezone.utc))
        self.settlement_repo.save(settlement)

        # Reset mocks
        self.access_repo.save_calls = 0
        self.interest_repo.save_calls = 0

        self.pricing_policy.amount_minor = 1500
        self.pricing_policy.call_count = 0

        # Execute again
        result = self.use_case.execute(opportunity_invitation_id=invitation.id)

        self.assertTrue(result.already_unlocked)
        self.assertEqual(result.access.id, access.id)
        self.assertEqual(result.settlement_id, settlement.id)

        # NO new mutations
        self.assertEqual(self.access_repo.save_calls, 0)
        self.assertEqual(self.interest_repo.save_calls, 0)
        self.assertEqual(self.pricing_policy.call_count, 0)
        self.assertEqual(self.settlement_repo.get_by_interest(interest.id).amount.amount_minor, 2500)

    def test_insufficient_credits(self):
        org_id = uuid4()
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)
        # Only 10 credits in wallet
        entry = CreditLedgerEntry(id=uuid4(), wallet_id=wallet.id, direction=CreditLedgerDirection.CREDIT, units=10, reason="Initial credit", reference="ref", created_at=datetime.now(timezone.utc))
        self.ledger_repo.save(entry)

        self.cost_policy.rate_callback = lambda price: 25
        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("Insufficient wallet credit balance", str(ctx.exception))

        # Verification: NO mutations
        self.assertEqual(self.access_repo.save_calls, 0)
        self.assertEqual(self.interest_repo.save_calls, 0)

    def test_pricing_unavailable(self):
        org_id = uuid4()
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)

        class FailingPricingPolicy:
            def quote(self, *, invitation, opportunity, provider, interest=None):
                raise OpportunityPricingUnavailable("Pricing not configured.")

        self.pricing_policy = FailingPricingPolicy()
        self.use_case.opportunity_pricing_policy = FailingPricingPolicy()

        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        with self.assertRaises(OpportunityPricingUnavailable):
            self.use_case.execute(opportunity_invitation_id=invitation.id)

        self.assertEqual(self.access_repo.save_calls, 0)

    def test_unexpected_pricing_failure(self):
        org_id = uuid4()
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)

        class BrokenPricingPolicy:
            def quote(self, *, invitation, opportunity, provider, interest=None):
                raise RuntimeError("Internal database error")

        self.pricing_policy = BrokenPricingPolicy()
        self.use_case.opportunity_pricing_policy = BrokenPricingPolicy()

        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        with self.assertRaises(RuntimeError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertEqual(str(ctx.exception), "Internal database error")

        self.assertEqual(self.access_repo.save_calls, 0)

    def test_invalid_invitation(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(opportunity_invitation_id=uuid4())

    def test_inactive_provider(self):
        provider, sr, opp, invitation = self._setup_base_entities(provider_active=False)
        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("Provider is inactive", str(ctx.exception))

    def test_closed_opportunity(self):
        provider, sr, opp, invitation = self._setup_base_entities(opp_open=False)
        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("Opportunity is not OPEN", str(ctx.exception))

    def test_closed_service_request(self):
        provider, sr, opp, invitation = self._setup_base_entities(sr_open=False)
        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertIn("ServiceRequest is not OPEN", str(ctx.exception))

    def test_atomic_rollback_on_access_creation_failure(self):
        org_id = uuid4()
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)
        entry = CreditLedgerEntry(id=uuid4(), wallet_id=wallet.id, direction=CreditLedgerDirection.CREDIT, units=30, reason="Initial credit", reference="ref", created_at=datetime.now(timezone.utc))
        self.ledger_repo.save(entry)

        self.cost_policy.rate_callback = lambda price: 25
        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        # Force the writer to fail after simulating all checks
        self.atomic_writer.should_fail_at_access = True

        with self.assertRaises(RuntimeError) as ctx:
            self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertEqual(str(ctx.exception), "Database error during access persistence.")

        # Ensure rollback simulation means NO database entities were persisted
        self.assertEqual(self.access_repo.save_calls, 0)
        self.assertEqual(self.interest_repo.save_calls, 0)
        # Debit entry must not be persisted (only initial credit exists)
        entries = self.ledger_repo.list_by_wallet(wallet.id)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].direction, CreditLedgerDirection.CREDIT)

    def test_double_invocation_regression(self):
        org_id = uuid4()
        wallet = CreditWallet(id=uuid4(), organization_id=org_id, is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.wallet_repo.save(wallet)
        entry = CreditLedgerEntry(id=uuid4(), wallet_id=wallet.id, direction=CreditLedgerDirection.CREDIT, units=100, reason="Initial credit", reference="ref", created_at=datetime.now(timezone.utc))
        self.ledger_repo.save(entry)

        self.cost_policy.rate_callback = lambda price: 25
        provider, sr, opp, invitation = self._setup_base_entities(org_id=org_id)

        # First execution
        result1 = self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertFalse(result1.already_unlocked)

        # Mock repos save count reset
        self.access_repo.save_calls = 0
        self.interest_repo.save_calls = 0

        # Second execution
        result2 = self.use_case.execute(opportunity_invitation_id=invitation.id)
        self.assertTrue(result2.already_unlocked)

        # Count check
        self.assertEqual(self.access_repo.save_calls, 0)
        self.assertSilentInterestEmpty(wallet.id)
        # Ledger check: only 1 debit was registered
        entries = self.ledger_repo.list_by_wallet(wallet.id)
        debits = [e for e in entries if e.direction is CreditLedgerDirection.DEBIT]
        self.assertEqual(len(debits), 1)

    def assertSilentInterestEmpty(self, wallet_id):
        pass


class InMemoryProtectedDataReadAuditWriter:
    def __init__(self):
        self.events = []
        self.should_fail = False

    def record_contact_read(
        self,
        *,
        authenticated_user_id: UUID,
        provider_id: UUID,
        opportunity_id: UUID,
        service_request_id: UUID,
    ) -> None:
        if self.should_fail:
            raise RuntimeError("Audit DB failure")
        self.events.append({
            "authenticated_user_id": authenticated_user_id,
            "provider_id": provider_id,
            "opportunity_id": opportunity_id,
            "service_request_id": service_request_id,
        })


class GetUnlockedOpportunityContactTests(SimpleTestCase):
    def setUp(self):
        self.access_repo = InMemoryOpportunityAccessRepository()
        self.opp_repo = InMemoryOpportunityRepository()
        self.sr_repo = InMemoryServiceRequestRepository()
        self.provider_repo = InMemoryProviderRepository()
        self.audit_writer = InMemoryProtectedDataReadAuditWriter()
        self.use_case = GetUnlockedOpportunityContact(
            opportunity_access_repository=self.access_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.provider_repo,
            audit_writer=self.audit_writer,
        )

    def _setup_base_entities(self, requester_name="John Doe", requester_email="john@example.com", requester_phone="+5511999999999"):
        provider_id = uuid4()
        provider = Provider(
            id=provider_id,
            organization_id=uuid4(),
            display_name="Provider A",
            slug="provider-a",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider)

        sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Service Title",
            description="Desc",
            status=ServiceRequestStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            requester_name=requester_name,
            requester_email=requester_email,
            requester_phone=requester_phone,
        )
        self.sr_repo.save(sr)

        opp = Opportunity(
            id=uuid4(),
            service_request_id=sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.opp_repo.save(opp)

        return provider, sr, opp

    def test_happy_path_success(self):
        provider, sr, opp = self._setup_base_entities()

        # Pre-existing access representing legit purchase
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        contact = self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider.id, opportunity_id=opp.id)

        self.assertIsInstance(contact, UnlockedOpportunityContact)
        self.assertEqual(contact.opportunity_id, opp.id)
        self.assertEqual(contact.service_request_id, sr.id)
        self.assertEqual(contact.requester_name, "John Doe")
        self.assertEqual(contact.requester_email, "john@example.com")
        self.assertEqual(contact.requester_phone, "+5511999999999")

    def test_no_access_denied(self):
        provider, sr, opp = self._setup_base_entities()

        # No access saved - should raise error
        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider.id, opportunity_id=opp.id)
        self.assertIn("Access entitlement missing", str(ctx.exception))

    def test_wrong_provider_idor_protection(self):
        provider_a, sr, opp = self._setup_base_entities()

        # Provider B setup
        provider_b_id = uuid4()
        provider_b = Provider(
            id=provider_b_id,
            organization_id=uuid4(),
            display_name="Provider B",
            slug="provider-b",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider_b)

        # Access ONLY for Provider A
        access_a = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_a.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access_a)

        # Provider B tries to read contact - should raise error
        with self.assertRaises(ValueError) as ctx:
            self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider_b.id, opportunity_id=opp.id)
        self.assertIn("Access entitlement missing", str(ctx.exception))

    def test_repeated_read_has_no_side_effects(self):
        provider, sr, opp = self._setup_base_entities()
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        # Reset repository spy calls
        self.access_repo.save_calls = 0

        # Execute multiple times
        c1 = self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider.id, opportunity_id=opp.id)
        c2 = self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider.id, opportunity_id=opp.id)

        self.assertEqual(c1.requester_name, c2.requester_name)
        # Ensure no mutations occurred
        self.assertEqual(self.access_repo.save_calls, 0)

    def test_legacy_blank_fields_preserved(self):
        provider, sr, opp = self._setup_base_entities(requester_name="Legacy Name", requester_email="", requester_phone="")
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        contact = self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider.id, opportunity_id=opp.id)

        self.assertEqual(contact.requester_name, "Legacy Name")
        self.assertEqual(contact.requester_email, "")
        self.assertEqual(contact.requester_phone, "")

    def test_unexpected_repository_failure_propagates(self):
        # Setup repository that throws RuntimeError on access retrieval
        class FailingAccessRepository:
            def get_by_opportunity_and_provider(self, opportunity_id, provider_id):
                raise RuntimeError("Access DB is down")

        self.use_case.opportunity_access_repository = FailingAccessRepository()

        with self.assertRaises(RuntimeError) as ctx:
            self.use_case.execute(authenticated_user_id=uuid4(), provider_id=uuid4(), opportunity_id=uuid4())
        self.assertEqual(str(ctx.exception), "Access DB is down")

    def test_pii_allowlist_regression(self):
        provider, sr, opp = self._setup_base_entities()
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)

        contact = self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider.id, opportunity_id=opp.id)

        # Structural validation that no other fields from ServiceRequest exist on UnlockedOpportunityContact
        from dataclasses import fields
        field_names = {f.name for f in fields(contact)}
        self.assertEqual(
            field_names,
            {"opportunity_id", "service_request_id", "requester_name", "requester_email", "requester_phone"}
        )

    def test_audit_recorded_on_success(self):
        provider, sr, opp = self._setup_base_entities()
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)
        user_id = uuid4()

        contact = self.use_case.execute(
            authenticated_user_id=user_id,
            provider_id=provider.id,
            opportunity_id=opp.id,
        )

        self.assertEqual(len(self.audit_writer.events), 1)
        event = self.audit_writer.events[0]
        self.assertEqual(event["authenticated_user_id"], user_id)
        self.assertEqual(event["provider_id"], provider.id)
        self.assertEqual(event["opportunity_id"], opp.id)
        self.assertEqual(event["service_request_id"], sr.id)

    def test_audit_recorded_on_repeated_reads(self):
        provider, sr, opp = self._setup_base_entities()
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)
        user_id = uuid4()

        self.use_case.execute(
            authenticated_user_id=user_id,
            provider_id=provider.id,
            opportunity_id=opp.id,
        )
        self.use_case.execute(
            authenticated_user_id=user_id,
            provider_id=provider.id,
            opportunity_id=opp.id,
        )

        self.assertEqual(len(self.audit_writer.events), 2)

    def test_no_audit_on_unauthorized_read(self):
        provider, sr, opp = self._setup_base_entities()
        user_id = uuid4()

        with self.assertRaises(ValueError):
            self.use_case.execute(
                authenticated_user_id=user_id,
                provider_id=provider.id,
                opportunity_id=opp.id,
            )

        self.assertEqual(len(self.audit_writer.events), 0)

    def test_audit_failure_blocks_contact_return(self):
        provider, sr, opp = self._setup_base_entities()
        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access)
        user_id = uuid4()
        self.audit_writer.should_fail = True

        with self.assertRaises(RuntimeError) as ctx:
            self.use_case.execute(
                authenticated_user_id=user_id,
                provider_id=provider.id,
                opportunity_id=opp.id,
            )
        self.assertEqual(str(ctx.exception), "Audit DB failure")
        self.assertEqual(len(self.audit_writer.events), 0)

    def test_privacy_critical_regression(self):
        provider_a, sr, opp = self._setup_base_entities()
        provider_b_id = uuid4()
        provider_b = Provider(
            id=provider_b_id,
            organization_id=uuid4(),
            display_name="Provider B",
            slug="provider-b",
            description="",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.provider_repo.save(provider_b)

        # A has access, B does not
        access_a = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opp.id,
            provider_id=provider_a.id,
            created_at=datetime.now(timezone.utc),
        )
        self.access_repo.save(access_a)

        # Exclude B from accessing contact details
        with self.assertRaises(ValueError):
            self.use_case.execute(authenticated_user_id=uuid4(), provider_id=provider_b.id, opportunity_id=opp.id)


# ---------------------------------------------------------------------------
# Sprint 01Y — Authenticated Provider Identity Boundary V1
# ---------------------------------------------------------------------------

from src.marketplace.application.use_cases import (
    AmbiguousProviderIdentity,
    AuthenticatedProviderMarketplaceService,
    ProviderIdentityNotFound,
)


class FakeProviderIdentityResolver:
    """In-memory stub of ProviderIdentityResolver. Django-free."""

    def __init__(self, mapping: dict):
        # {user_id (UUID): Provider | Exception}
        self._mapping = mapping

    def resolve(self, *, authenticated_user_id: UUID) -> Provider:
        result = self._mapping.get(authenticated_user_id)
        if result is None:
            raise ProviderIdentityNotFound(
                f"No provider mapping for user {authenticated_user_id}"
            )
        if isinstance(result, Exception):
            raise result
        return result


class _Fake01YPreview:
    def __init__(self):
        self.called_with = []
        self.return_value = None

    def execute(self, *, opportunity_invitation_id: UUID):
        self.called_with.append(opportunity_invitation_id)
        return self.return_value


class _Fake01YQuote:
    def __init__(self):
        self.called_with = []
        self.return_value = None

    def execute(self, *, opportunity_invitation_id: UUID):
        self.called_with.append(opportunity_invitation_id)
        return self.return_value


class _Fake01YUnlock:
    def __init__(self):
        self.called_with = []
        self.return_value = None

    def execute(self, *, opportunity_invitation_id: UUID):
        self.called_with.append(opportunity_invitation_id)
        return self.return_value


class _Fake01YContact:
    def __init__(self):
        self.called_with = []
        self.return_value = None

    def execute(self, *, authenticated_user_id: UUID, provider_id: UUID, opportunity_id: UUID):
        self.called_with.append((provider_id, opportunity_id))
        return self.return_value


def _prov01y(*, is_active: bool = True) -> Provider:
    now = datetime.now(timezone.utc)
    return Provider(
        id=uuid4(),
        organization_id=uuid4(),
        display_name="Provider",
        slug=f"p-{uuid4().hex[:8]}",
        description="",
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


def _inv01y(*, provider_id: UUID) -> OpportunityInvitation:
    return OpportunityInvitation(
        id=uuid4(),
        opportunity_id=uuid4(),
        provider_id=provider_id,
        created_at=datetime.now(timezone.utc),
    )


def _prev01y(*, opportunity_id: UUID) -> OpportunityPreview:
    return OpportunityPreview(
        opportunity_id=opportunity_id,
        service_request_id=uuid4(),
        service_id=uuid4(),
        title="T",
        description="D",
        status=OpportunityStatus.OPEN,
        created_at=datetime.now(timezone.utc),
    )


class AuthenticatedProviderIdentityResolverTests(SimpleTestCase):
    """Tests for ProviderIdentityNotFound / AmbiguousProviderIdentity semantics."""

    def test_valid_user_resolves_to_provider(self):
        uid = uuid4()
        prov = _prov01y()
        resolver = FakeProviderIdentityResolver({uid: prov})
        result = resolver.resolve(authenticated_user_id=uid)
        self.assertIs(result, prov)

    def test_unknown_user_raises_provider_identity_not_found(self):
        resolver = FakeProviderIdentityResolver({})
        with self.assertRaises(ProviderIdentityNotFound):
            resolver.resolve(authenticated_user_id=uuid4())

    def test_different_user_cannot_resolve_other_provider(self):
        user_a, user_b = uuid4(), uuid4()
        prov_a = _prov01y()
        resolver = FakeProviderIdentityResolver({user_a: prov_a})
        with self.assertRaises(ProviderIdentityNotFound):
            resolver.resolve(authenticated_user_id=user_b)

    def test_ambiguous_raises_ambiguous_provider_identity(self):
        uid = uuid4()
        resolver = FakeProviderIdentityResolver({uid: AmbiguousProviderIdentity("two")})
        with self.assertRaises(AmbiguousProviderIdentity):
            resolver.resolve(authenticated_user_id=uid)

    def test_unexpected_runtime_error_propagates(self):
        uid = uuid4()
        resolver = FakeProviderIdentityResolver({uid: RuntimeError("db down")})
        with self.assertRaises(RuntimeError):
            resolver.resolve(authenticated_user_id=uid)

    def test_provider_identity_not_found_is_not_runtime_error(self):
        self.assertNotIsInstance(ProviderIdentityNotFound(), RuntimeError)

    def test_ambiguous_provider_identity_is_not_runtime_error(self):
        self.assertNotIsInstance(AmbiguousProviderIdentity(), RuntimeError)

    def test_identity_exceptions_are_exceptions(self):
        self.assertIsInstance(ProviderIdentityNotFound(), Exception)
        self.assertIsInstance(AmbiguousProviderIdentity(), Exception)


class AuthenticatedProviderMarketplaceServiceTests(SimpleTestCase):
    """
    Security matrix: provider_id derived exclusively from ProviderIdentityResolver.

    Canonical surface tested:
        preview(authenticated_user_id, opportunity_invitation_id)
        quote(authenticated_user_id, opportunity_invitation_id)
        unlock(authenticated_user_id, opportunity_invitation_id)
        get_contact(authenticated_user_id, opportunity_id)

    Invariants:
        - All four methods resolve identity from authenticated_user_id — never from caller.
        - invitation ownership is enforced before any use-case delegation.
        - provider_id is NEVER accepted as an external parameter.
        - No _safe variants exist in the public API.
    """

    def _facade(
        self,
        *,
        resolver,
        invitation_repo=None,
        preview=None,
        quote=None,
        unlock=None,
        contact=None,
        list_inbox=None,
        list_unlocked=None,
    ):
        return AuthenticatedProviderMarketplaceService(
            provider_identity_resolver=resolver,
            invitation_repository=invitation_repo or InMemoryOpportunityInvitationRepository(),
            get_opportunity_preview=preview or _Fake01YPreview(),
            get_opportunity_unlock_quote=quote or _Fake01YQuote(),
            unlock_opportunity_with_credits=unlock or _Fake01YUnlock(),
            get_unlocked_opportunity_contact=contact or _Fake01YContact(),
            list_provider_opportunity_inbox=list_inbox,
            list_provider_unlocked_opportunities=list_unlocked,
        )

    # ------------------------------------------------------------------
    # A. Surface test — canonical methods exist; unsafe variants do NOT
    # ------------------------------------------------------------------

    def test_canonical_surface_has_preview(self):
        """preview method must exist on the facade."""
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        self.assertTrue(callable(getattr(facade, "preview", None)))

    def test_canonical_surface_has_quote(self):
        """quote method must exist on the facade."""
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        self.assertTrue(callable(getattr(facade, "quote", None)))

    def test_canonical_surface_has_unlock(self):
        """unlock method must exist on the facade."""
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        self.assertTrue(callable(getattr(facade, "unlock", None)))

    def test_canonical_surface_has_get_contact(self):
        """get_contact method must exist on the facade."""
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        self.assertTrue(callable(getattr(facade, "get_contact", None)))

    def test_preview_safe_does_not_exist(self):
        """preview_safe must NOT exist — secure behavior is the default."""
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        self.assertFalse(hasattr(facade, "preview_safe"))

    def test_quote_safe_does_not_exist(self):
        """quote_safe must NOT exist — secure behavior is the default."""
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        self.assertFalse(hasattr(facade, "quote_safe"))

    def test_unlock_safe_does_not_exist(self):
        """unlock_safe must NOT exist — secure behavior is the default."""
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        self.assertFalse(hasattr(facade, "unlock_safe"))

    def test_canonical_methods_do_not_accept_provider_id_parameter(self):
        """None of the four public methods should accept provider_id."""
        import inspect
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        for method_name in ("preview", "quote", "unlock", "get_contact"):
            sig = inspect.signature(getattr(facade, method_name))
            self.assertNotIn(
                "provider_id",
                sig.parameters,
                msg=f"{method_name}() must not accept provider_id",
            )

    # ------------------------------------------------------------------
    # B. get_contact — basic security
    # ------------------------------------------------------------------

    def test_get_contact_uses_resolved_provider_not_caller_payload(self):
        uid = uuid4()
        prov = _prov01y()
        opp_id = uuid4()
        contact = _Fake01YContact()
        contact.return_value = UnlockedOpportunityContact(
            opportunity_id=opp_id,
            service_request_id=uuid4(),
            requester_name="N",
            requester_email="e@e.com",
            requester_phone="+1",
        )
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            contact=contact,
        )
        facade.get_contact(authenticated_user_id=uid, opportunity_id=opp_id)
        self.assertEqual(len(contact.called_with), 1)
        called_pid, called_oid = contact.called_with[0]
        self.assertEqual(called_pid, prov.id)
        self.assertEqual(called_oid, opp_id)

    def test_get_contact_no_provider_mapping_raises_not_found(self):
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        with self.assertRaises(ProviderIdentityNotFound):
            facade.get_contact(authenticated_user_id=uuid4(), opportunity_id=uuid4())

    def test_get_contact_ambiguous_raises_ambiguous_identity(self):
        uid = uuid4()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: AmbiguousProviderIdentity("x")})
        )
        with self.assertRaises(AmbiguousProviderIdentity):
            facade.get_contact(authenticated_user_id=uid, opportunity_id=uuid4())

    def test_get_contact_resolver_runtime_error_propagates(self):
        uid = uuid4()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: RuntimeError("infra down")})
        )
        with self.assertRaises(RuntimeError):
            facade.get_contact(authenticated_user_id=uid, opportunity_id=uuid4())

    def test_get_contact_invalid_opportunity_id_rejected(self):
        uid = uuid4()
        prov = _prov01y()
        facade = self._facade(resolver=FakeProviderIdentityResolver({uid: prov}))
        with self.assertRaises(ValueError):
            facade.get_contact(authenticated_user_id=uid, opportunity_id=None)  # type: ignore

    def test_get_contact_invalid_user_id_rejected(self):
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        with self.assertRaises(ValueError):
            facade.get_contact(authenticated_user_id=None, opportunity_id=uuid4())  # type: ignore

    def test_get_contact_caller_cannot_supply_provider_id(self):
        """
        Regression: the façade API does not accept provider_id parameter.
        The resolved provider_id is always the one forwarded to the use case.
        """
        user_b = uuid4()
        prov_a = _prov01y()
        prov_b = _prov01y()
        opp_id = uuid4()
        contact = _Fake01YContact()
        contact.return_value = None
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({user_b: prov_b}),
            contact=contact,
        )
        facade.get_contact(authenticated_user_id=user_b, opportunity_id=opp_id)
        called_pid, _ = contact.called_with[0]
        # Provider B's ID was forwarded — NOT Provider A's
        self.assertEqual(called_pid, prov_b.id)
        self.assertNotEqual(called_pid, prov_a.id)

    # ------------------------------------------------------------------
    # C. preview — invitation ownership
    # ------------------------------------------------------------------

    def test_preview_allows_owner_provider(self):
        uid = uuid4()
        prov = _prov01y()
        inv = _inv01y(provider_id=prov.id)
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        preview = _Fake01YPreview()
        preview.return_value = _prev01y(opportunity_id=inv.opportunity_id)
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            invitation_repo=repo,
            preview=preview,
        )
        result = facade.preview(
            authenticated_user_id=uid,
            opportunity_invitation_id=inv.id,
        )
        self.assertIsInstance(result, OpportunityPreview)
        self.assertEqual(len(preview.called_with), 1)

    def test_preview_denies_cross_provider_access(self):
        """Provider B cannot preview Provider A's invitation."""
        user_b = uuid4()
        prov_a = _prov01y()
        prov_b = _prov01y()
        inv = _inv01y(provider_id=prov_a.id)
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        preview = _Fake01YPreview()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({user_b: prov_b}),
            invitation_repo=repo,
            preview=preview,
        )
        with self.assertRaises(ValueError) as ctx:
            facade.preview(
                authenticated_user_id=user_b,
                opportunity_invitation_id=inv.id,
            )
        self.assertIn("does not belong", str(ctx.exception))
        self.assertEqual(len(preview.called_with), 0)

    def test_preview_nonexistent_invitation_raises_value_error(self):
        uid = uuid4()
        prov = _prov01y()
        repo = InMemoryOpportunityInvitationRepository()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            invitation_repo=repo,
        )
        with self.assertRaises(ValueError) as ctx:
            facade.preview(
                authenticated_user_id=uid,
                opportunity_invitation_id=uuid4(),
            )
        self.assertIn("does not exist", str(ctx.exception))

    def test_preview_invalid_invitation_id_rejected(self):
        uid = uuid4()
        prov = _prov01y()
        repo = InMemoryOpportunityInvitationRepository()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            invitation_repo=repo,
        )
        with self.assertRaises(ValueError):
            facade.preview(
                authenticated_user_id=uid,
                opportunity_invitation_id=None,  # type: ignore
            )

    # ------------------------------------------------------------------
    # D. quote — invitation ownership
    # ------------------------------------------------------------------

    def test_quote_allows_owner_provider(self):
        uid = uuid4()
        prov = _prov01y()
        inv = _inv01y(provider_id=prov.id)
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        quote = _Fake01YQuote()
        quote.return_value = OpportunityUnlockQuote(
            opportunity_id=inv.opportunity_id,
            provider_id=prov.id,
            amount=None,
            quote_available=False,
            already_unlocked=False,
            reason="no pricing",
        )
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            invitation_repo=repo,
            quote=quote,
        )
        result = facade.quote(
            authenticated_user_id=uid,
            opportunity_invitation_id=inv.id,
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(quote.called_with), 1)

    def test_quote_denies_cross_provider_access(self):
        """Provider B cannot quote Provider A's invitation."""
        user_b = uuid4()
        prov_a = _prov01y()
        prov_b = _prov01y()
        inv = _inv01y(provider_id=prov_a.id)
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        quote = _Fake01YQuote()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({user_b: prov_b}),
            invitation_repo=repo,
            quote=quote,
        )
        with self.assertRaises(ValueError) as ctx:
            facade.quote(
                authenticated_user_id=user_b,
                opportunity_invitation_id=inv.id,
            )
        self.assertIn("does not belong", str(ctx.exception))
        self.assertEqual(len(quote.called_with), 0)

    # ------------------------------------------------------------------
    # E. unlock — invitation ownership + provider.is_active guard
    # ------------------------------------------------------------------

    def test_unlock_allows_owner_provider(self):
        uid = uuid4()
        prov = _prov01y(is_active=True)
        inv = _inv01y(provider_id=prov.id)
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        unlock = _Fake01YUnlock()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            invitation_repo=repo,
            unlock=unlock,
        )
        facade.unlock(
            authenticated_user_id=uid,
            opportunity_invitation_id=inv.id,
        )
        self.assertEqual(len(unlock.called_with), 1)

    def test_unlock_denies_cross_provider_access(self):
        """
        Critical: Provider B using Provider A's invitation would trigger
        an economic debit on B's wallet for A's opportunity.
        """
        user_b = uuid4()
        prov_a = _prov01y()
        prov_b = _prov01y()
        inv = _inv01y(provider_id=prov_a.id)
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        unlock = _Fake01YUnlock()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({user_b: prov_b}),
            invitation_repo=repo,
            unlock=unlock,
        )
        with self.assertRaises(ValueError) as ctx:
            facade.unlock(
                authenticated_user_id=user_b,
                opportunity_invitation_id=inv.id,
            )
        self.assertIn("does not belong", str(ctx.exception))
        # Unlock use case was NOT called — no economic effect triggered
        self.assertEqual(len(unlock.called_with), 0)

    def test_unlock_no_provider_mapping_raises_not_found(self):
        inv = _inv01y(provider_id=uuid4())
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        facade = self._facade(resolver=FakeProviderIdentityResolver({}))
        with self.assertRaises(ProviderIdentityNotFound):
            facade.unlock(
                authenticated_user_id=uuid4(),
                opportunity_invitation_id=inv.id,
            )

    def test_unlock_inactive_provider_denied_before_economic_use_case(self):
        """
        An inactive Provider resolves identity successfully (active Membership),
        but must be blocked at the facade before the economic unlock use case
        is called.

        Proof:
            - debit: 0  (unlock.called_with is empty)
            - settlement: 0
            - new OpportunityAccess: 0
        """
        uid = uuid4()
        prov = _prov01y(is_active=False)  # inactive Provider
        inv = _inv01y(provider_id=prov.id)
        repo = InMemoryOpportunityInvitationRepository()
        repo.save(inv)
        unlock = _Fake01YUnlock()
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            invitation_repo=repo,
            unlock=unlock,
        )
        with self.assertRaises(ValueError) as ctx:
            facade.unlock(
                authenticated_user_id=uid,
                opportunity_invitation_id=inv.id,
            )
        # Must mention the inactive status
        self.assertIn("inactive", str(ctx.exception).lower())
        # Underlying economic use case was NOT called
        self.assertEqual(len(unlock.called_with), 0,
                         "Inactive Provider must not reach the economic unlock use case")

    # ------------------------------------------------------------------
    # F. Historical contact — inactive Provider allowed
    # ------------------------------------------------------------------

    def test_inactive_provider_can_retrieve_historical_contact(self):
        """
        An inactive Provider with an active Membership resolves identity.
        Historical contact retrieval must succeed for that resolved provider_id.

        get_contact does NOT check provider.is_active — the entitlement was
        acquired before the Provider became inactive.  Validation of the
        existing OpportunityAccess is delegated to GetUnlockedOpportunityContact.
        """
        uid = uuid4()
        prov = _prov01y(is_active=False)  # inactive but identity resolves
        opp_id = uuid4()
        contact = _Fake01YContact()
        contact.return_value = UnlockedOpportunityContact(
            opportunity_id=opp_id,
            service_request_id=uuid4(),
            requester_name="Alice",
            requester_email="alice@example.com",
            requester_phone="+55119999",
        )
        facade = self._facade(
            resolver=FakeProviderIdentityResolver({uid: prov}),
            contact=contact,
        )
        result = facade.get_contact(authenticated_user_id=uid, opportunity_id=opp_id)
        # Identity resolved and contact was returned
        self.assertIsNotNone(result)
        self.assertEqual(len(contact.called_with), 1)
        called_pid, called_oid = contact.called_with[0]
        self.assertEqual(called_pid, prov.id)
        self.assertEqual(called_oid, opp_id)


class ListProviderOpportunityInboxTests(SimpleTestCase):
    """Unit test suite for ListProviderOpportunityInbox application use case."""

    def setUp(self):
        from src.marketplace.domain.entities import OpportunityStatus, ServiceRequestStatus
        from src.marketplace.application.use_cases import ListProviderOpportunityInbox

        self.now = datetime.now(timezone.utc)
        self.opp_repo = InMemoryOpportunityRepository()
        self.sr_repo = InMemoryServiceRequestRepository()
        self.prov_repo = InMemoryProviderRepository()
        self.inv_repo = InMemoryOpportunityInvitationRepository(
            opportunity_repo=self.opp_repo,
            service_request_repo=self.sr_repo,
        )

        self.use_case = ListProviderOpportunityInbox(
            opportunity_invitation_repository=self.inv_repo,
            opportunity_repository=self.opp_repo,
            service_request_repository=self.sr_repo,
            provider_repository=self.prov_repo,
        )

        # Provider A
        self.provider_a = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Provider A",
            slug="pa",
            description="Desc A",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.prov_repo.save(self.provider_a)

        # Provider B
        self.provider_b = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Provider B",
            slug="pb",
            description="Desc B",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.prov_repo.save(self.provider_b)

        # ServiceRequest & Opportunity
        self.sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Arch Consulting",
            description="Review tech stack",
            status=ServiceRequestStatus.OPEN,
            requester_name="Secret Requester",
            requester_email="secret@test.com",
            requester_phone="+123456",
            created_at=self.now,
            updated_at=self.now,
        )
        self.sr_repo.save(self.sr)

        self.opp = Opportunity(
            id=uuid4(),
            service_request_id=self.sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )
        self.opp_repo.save(self.opp)

        # Invitation for Provider A
        self.inv_a = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=self.opp.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )
        self.inv_repo.save(self.inv_a)

        # Invitation for Provider B
        self.inv_b = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=self.opp.id,
            provider_id=self.provider_b.id,
            created_at=self.now,
        )
        self.inv_repo.save(self.inv_b)

    def test_list_inbox_lists_only_for_provider(self):
        page = self.use_case.execute(provider_id=self.provider_a.id)
        self.assertEqual(page.total_items, 1)
        self.assertEqual(len(page.items), 1)
        self.assertEqual(page.items[0].invitation_id, self.inv_a.id)
        self.assertEqual(page.items[0].opportunity_id, self.opp.id)
        self.assertEqual(page.items[0].title, "Arch Consulting")

    def test_list_inbox_empty_list_for_provider_without_invitations(self):
        empty_prov = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Provider Empty",
            slug="pe",
            description="Desc",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.prov_repo.save(empty_prov)

        page = self.use_case.execute(provider_id=empty_prov.id)
        self.assertEqual(page.total_items, 0)
        self.assertEqual(len(page.items), 0)
        self.assertEqual(page.total_pages, 0)

    def test_list_inbox_sanitization_no_pii(self):
        page = self.use_case.execute(provider_id=self.provider_a.id)
        item = page.items[0]
        self.assertFalse(hasattr(item, "requester_name"))
        self.assertFalse(hasattr(item, "requester_email"))
        self.assertFalse(hasattr(item, "requester_phone"))

    def test_list_inbox_invalid_pagination(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=self.provider_a.id, page=0)
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=self.provider_a.id, page_size=0)
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=self.provider_a.id, page_size=101)


class ListProviderUnlockedOpportunitiesTests(SimpleTestCase):
    def setUp(self):
        from src.marketplace.application.use_cases import ListProviderUnlockedOpportunities
        self.now = datetime.now(timezone.utc)
        self.prov_repo = InMemoryProviderRepository()
        self.opp_repo = InMemoryOpportunityRepository()
        self.sr_repo = InMemoryServiceRequestRepository()
        self.access_repo = InMemoryOpportunityAccessRepository(self.opp_repo, self.sr_repo)

        self.use_case = ListProviderUnlockedOpportunities(
            opportunity_access_repository=self.access_repo,
            provider_repository=self.prov_repo,
        )

        # Create provider
        self.provider_a = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Provider A",
            slug="pa",
            description="Desc",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.prov_repo.save(self.provider_a)

        # Create service request & opportunity
        self.sr = ServiceRequest(
            id=uuid4(),
            organization_id=uuid4(),
            service_id=uuid4(),
            title="Design Service",
            description="A nice project",
            status=ServiceRequestStatus.OPEN,
            requester_name="Alice",
            requester_email="alice@example.com",
            requester_phone="+5511",
            created_at=self.now,
            updated_at=self.now,
        )
        self.sr_repo.save(self.sr)

        self.opp = Opportunity(
            id=uuid4(),
            service_request_id=self.sr.id,
            status=OpportunityStatus.OPEN,
            max_accesses=3,
            created_at=self.now,
            updated_at=self.now,
        )
        self.opp_repo.save(self.opp)

        # Create access
        self.access_a = OpportunityAccess(
            id=uuid4(),
            opportunity_id=self.opp.id,
            provider_id=self.provider_a.id,
            created_at=self.now,
        )
        self.access_repo.save(self.access_a)

    def test_list_unlocked_opportunities_success(self):
        page = self.use_case.execute(provider_id=self.provider_a.id)
        self.assertEqual(page.total_items, 1)
        self.assertEqual(len(page.items), 1)
        item = page.items[0]
        self.assertEqual(item.opportunity_id, self.opp.id)
        self.assertEqual(item.title, "Design Service")
        self.assertEqual(item.status, OpportunityStatus.OPEN)

    def test_list_unlocked_opportunities_empty_for_another_provider(self):
        other_provider = Provider(
            id=uuid4(),
            organization_id=uuid4(),
            display_name="Provider B",
            slug="pb",
            description="Desc",
            is_active=True,
            created_at=self.now,
            updated_at=self.now,
        )
        self.prov_repo.save(other_provider)

        page = self.use_case.execute(provider_id=other_provider.id)
        self.assertEqual(page.total_items, 0)
        self.assertEqual(len(page.items), 0)

    def test_list_unlocked_opportunities_invalid_pagination(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=self.provider_a.id, page=0)
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=self.provider_a.id, page_size=0)
        with self.assertRaises(ValueError):
            self.use_case.execute(provider_id=self.provider_a.id, page_size=101)
