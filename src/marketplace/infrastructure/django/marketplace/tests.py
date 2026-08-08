from datetime import datetime, timezone
from uuid import uuid4

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from src.marketplace.domain.entities import (
    Provider,
    ProviderService,
    Service,
    ServiceCategory,
)
from src.marketplace.infrastructure.django.marketplace.models import (
    ProviderModel,
    ProviderServiceModel,
    ServiceModel,
    ServiceCategoryModel,
)
from src.marketplace.infrastructure.django.repositories import (
    DjangoProviderRepository,
    DjangoProviderServiceRepository,
    DjangoServiceRepository,
    DjangoServiceCategoryRepository,
)
from src.organizations.infrastructure.django.organizations.models import (
    OrganizationModel,
)


class DjangoServiceCategoryRepositoryTests(TestCase):
    def setUp(self):
        self.repository = DjangoServiceCategoryRepository()

    def test_get_by_id(self):
        now = datetime.now(timezone.utc)
        category = ServiceCategory(
            id=uuid4(),
            name="Automacao Industrial",
            slug="automacao-industrial",
            description="Categoria",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        saved = self.repository.save(category)

        found = self.repository.get_by_id(saved.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, saved.id)
        self.assertEqual(found.slug, "automacao-industrial")

    def test_get_by_slug(self):
        now = datetime.now(timezone.utc)
        category = ServiceCategory(
            id=uuid4(),
            name="Manutencao CNC",
            slug="manutencao-cnc",
            description="Categoria",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.repository.save(category)

        found = self.repository.get_by_slug("manutencao-cnc")

        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Manutencao CNC")

    def test_list_active(self):
        now = datetime.now(timezone.utc)
        active = ServiceCategory(
            id=uuid4(),
            name="Ativa",
            slug="ativa",
            description="Ativa",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        inactive = ServiceCategory(
            id=uuid4(),
            name="Inativa",
            slug="inativa",
            description="Inativa",
            is_active=False,
            created_at=now,
            updated_at=now,
        )

        self.repository.save(active)
        self.repository.save(inactive)

        active_items = self.repository.list_active()

        self.assertEqual(len(active_items), 1)
        self.assertEqual(active_items[0].slug, "ativa")

    def test_save_persists_model(self):
        now = datetime.now(timezone.utc)
        category = ServiceCategory(
            id=uuid4(),
            name="Eletrica Industrial",
            slug="eletrica-industrial",
            description="Categoria",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.repository.save(category)

        self.assertTrue(
            ServiceCategoryModel.objects.filter(
                id=category.id,
                slug="eletrica-industrial",
            ).exists()
        )


class DjangoServiceRepositoryTests(TestCase):
    def setUp(self):
        self.category_repository = DjangoServiceCategoryRepository()
        self.service_repository = DjangoServiceRepository()
        now = datetime.now(timezone.utc)
        self.category_a = self.category_repository.save(
            ServiceCategory(
                id=uuid4(),
                name="Automacao Industrial",
                slug="automacao-industrial",
                description="Categoria A",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
        self.category_b = self.category_repository.save(
            ServiceCategory(
                id=uuid4(),
                name="Refrigeracao",
                slug="refrigeracao",
                description="Categoria B",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )

    def _build_service(
        self,
        *,
        category_id,
        name: str,
        slug: str,
        is_active: bool = True,
    ) -> Service:
        now = datetime.now(timezone.utc)
        return Service(
            id=uuid4(),
            category_id=category_id,
            name=name,
            slug=slug,
            description="Descricao",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_save(self):
        service = self._build_service(
            category_id=self.category_a.id,
            name="Manutencao CNC",
            slug="manutencao",
        )

        saved = self.service_repository.save(service)

        self.assertEqual(saved.id, service.id)
        self.assertEqual(saved.category_id, self.category_a.id)
        self.assertTrue(
            ServiceModel.objects.filter(id=service.id).exists()
        )

    def test_get_by_id(self):
        service = self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Programacao CLP",
                slug="programacao-clp",
            )
        )

        found = self.service_repository.get_by_id(service.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, service.id)
        self.assertEqual(found.category_id, self.category_a.id)

    def test_get_by_category_and_slug(self):
        self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Retrofit",
                slug="retrofit",
            )
        )

        found = self.service_repository.get_by_category_and_slug(
            category_id=self.category_a.id,
            slug="retrofit",
        )

        self.assertIsNotNone(found)
        self.assertEqual(found.slug, "retrofit")

    def test_get_by_category_and_slug_returns_none_when_missing(self):
        found = self.service_repository.get_by_category_and_slug(
            category_id=self.category_a.id,
            slug="inexistente",
        )

        self.assertIsNone(found)

    def test_list_active_by_category(self):
        self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Servico A",
                slug="servico-a",
                is_active=True,
            )
        )
        self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Servico B",
                slug="servico-b",
                is_active=False,
            )
        )
        self.service_repository.save(
            self._build_service(
                category_id=self.category_b.id,
                name="Servico C",
                slug="servico-c",
                is_active=True,
            )
        )

        results = self.service_repository.list_active_by_category(
            category_id=self.category_a.id,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].slug, "servico-a")
        self.assertEqual(results[0].category_id, self.category_a.id)

    def test_list_active_by_category_is_deterministic(self):
        self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Zulu",
                slug="zulu",
            )
        )
        self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Alpha",
                slug="alpha",
            )
        )

        results = self.service_repository.list_active_by_category(
            category_id=self.category_a.id,
        )

        self.assertEqual(results[0].name, "Alpha")
        self.assertEqual(results[1].name, "Zulu")

    def test_constraint_rejects_duplicate_slug_in_same_category(self):
        self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Servico 1",
                slug="manutencao",
            )
        )

        with self.assertRaises(IntegrityError):
            self.service_repository.save(
                self._build_service(
                    category_id=self.category_a.id,
                    name="Servico 2",
                    slug="manutencao",
                )
            )

    def test_constraint_allows_same_slug_in_different_categories(self):
        first = self.service_repository.save(
            self._build_service(
                category_id=self.category_a.id,
                name="Servico A",
                slug="manutencao",
            )
        )
        second = self.service_repository.save(
            self._build_service(
                category_id=self.category_b.id,
                name="Servico B",
                slug="manutencao",
            )
        )

        self.assertEqual(first.slug, second.slug)
        self.assertNotEqual(first.category_id, second.category_id)


class DjangoProviderRepositoryTests(TestCase):
    def setUp(self):
        self.repository = DjangoProviderRepository()
        self.organization_a = OrganizationModel.objects.create(
            name="ACME Organization A",
            slug="acme-org-a",
        )
        self.organization_b = OrganizationModel.objects.create(
            name="ACME Organization B",
            slug="acme-org-b",
        )

    def _build_provider(
        self,
        *,
        organization_id,
        display_name: str,
        slug: str,
        is_active: bool = True,
    ) -> Provider:
        now = datetime.now(timezone.utc)
        return Provider(
            id=uuid4(),
            organization_id=organization_id,
            display_name=display_name,
            slug=slug,
            description="Descricao",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def test_save(self):
        provider = self._build_provider(
            organization_id=self.organization_a.id,
            display_name="ACME Automacao",
            slug="acme-automacao",
        )

        saved = self.repository.save(provider)

        self.assertEqual(saved.id, provider.id)
        self.assertEqual(saved.organization_id, self.organization_a.id)
        self.assertTrue(
            ProviderModel.objects.filter(id=provider.id).exists()
        )

    def test_get_by_id(self):
        provider = self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Provider A",
                slug="provider-a",
            )
        )

        found = self.repository.get_by_id(provider.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, provider.id)
        self.assertEqual(found.organization_id, self.organization_a.id)

    def test_get_by_slug(self):
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Provider B",
                slug="provider-b",
            )
        )

        found = self.repository.get_by_slug("provider-b")

        self.assertIsNotNone(found)
        self.assertEqual(found.display_name, "Provider B")

    def test_get_by_slug_returns_none_when_missing(self):
        self.assertIsNone(self.repository.get_by_slug("missing-provider"))

    def test_list_active_by_organization(self):
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Ativo A",
                slug="ativo-a",
                is_active=True,
            )
        )
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Inativo A",
                slug="inativo-a",
                is_active=False,
            )
        )
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_b.id,
                display_name="Ativo B",
                slug="ativo-b",
                is_active=True,
            )
        )

        results = self.repository.list_active_by_organization(
            self.organization_a.id,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].slug, "ativo-a")
        self.assertEqual(results[0].organization_id, self.organization_a.id)

    def test_list_active_by_organization_is_deterministic(self):
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Zulu Provider",
                slug="zulu-provider",
            )
        )
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Alpha Provider",
                slug="alpha-provider",
            )
        )

        results = self.repository.list_active_by_organization(
            self.organization_a.id,
        )

        self.assertEqual(results[0].display_name, "Alpha Provider")
        self.assertEqual(results[1].display_name, "Zulu Provider")

    def test_slug_is_globally_unique(self):
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Provider One",
                slug="unique-provider",
            )
        )

        with self.assertRaises(IntegrityError):
            self.repository.save(
                self._build_provider(
                    organization_id=self.organization_b.id,
                    display_name="Provider Two",
                    slug="unique-provider",
                )
            )

    def test_same_display_name_allowed_for_different_providers(self):
        first = self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Nome Igual",
                slug="nome-igual-a",
            )
        )
        second = self.repository.save(
            self._build_provider(
                organization_id=self.organization_b.id,
                display_name="Nome Igual",
                slug="nome-igual-b",
            )
        )

        self.assertEqual(first.display_name, second.display_name)
        self.assertNotEqual(first.id, second.id)

    def test_multiple_providers_can_belong_to_same_organization(self):
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Provider A1",
                slug="provider-a1",
            )
        )
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Provider A2",
                slug="provider-a2",
            )
        )

        providers = ProviderModel.objects.filter(
            organization_id=self.organization_a.id,
        )

        self.assertEqual(providers.count(), 2)

    def test_protect_prevents_organization_delete_with_provider(self):
        self.repository.save(
            self._build_provider(
                organization_id=self.organization_a.id,
                display_name="Provider Protect",
                slug="provider-protect",
            )
        )

        with self.assertRaises(ProtectedError):
            self.organization_a.delete()


class DjangoProviderServiceRepositoryTests(TestCase):
    def setUp(self):
        self.category_repository = DjangoServiceCategoryRepository()
        self.service_repository = DjangoServiceRepository()
        self.provider_repository = DjangoProviderRepository()
        self.provider_service_repository = DjangoProviderServiceRepository()

        self.organization_a = OrganizationModel.objects.create(
            name="ORG A",
            slug="org-a",
        )
        self.organization_b = OrganizationModel.objects.create(
            name="ORG B",
            slug="org-b",
        )

        now = datetime.now(timezone.utc)
        self.provider_a = self.provider_repository.save(
            Provider(
                id=uuid4(),
                organization_id=self.organization_a.id,
                display_name="Provider A",
                slug="provider-a-base",
                description="desc",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
        self.provider_b = self.provider_repository.save(
            Provider(
                id=uuid4(),
                organization_id=self.organization_b.id,
                display_name="Provider B",
                slug="provider-b-base",
                description="desc",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )

        self.category = self.category_repository.save(
            ServiceCategory(
                id=uuid4(),
                name="Categoria",
                slug="categoria",
                description="desc",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )

        self.service_a = self.service_repository.save(
            Service(
                id=uuid4(),
                category_id=self.category.id,
                name="Service A",
                slug="service-a",
                description="desc",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
        self.service_b = self.service_repository.save(
            Service(
                id=uuid4(),
                category_id=self.category.id,
                name="Service B",
                slug="service-b",
                description="desc",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )

    def _build_provider_service(
        self,
        *,
        provider_id,
        service_id,
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

    def test_save(self):
        provider_service = self._build_provider_service(
            provider_id=self.provider_a.id,
            service_id=self.service_a.id,
        )

        saved = self.provider_service_repository.save(provider_service)

        self.assertEqual(saved.id, provider_service.id)
        self.assertTrue(
            ProviderServiceModel.objects.filter(id=provider_service.id).exists()
        )

    def test_get_by_id(self):
        provider_service = self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
            )
        )

        found = self.provider_service_repository.get_by_id(provider_service.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, provider_service.id)

    def test_get_by_provider_and_service(self):
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
            )
        )

        found = self.provider_service_repository.get_by_provider_and_service(
            provider_id=self.provider_a.id,
            service_id=self.service_a.id,
        )

        self.assertIsNotNone(found)
        self.assertEqual(found.provider_id, self.provider_a.id)
        self.assertEqual(found.service_id, self.service_a.id)

    def test_get_by_provider_and_service_returns_none_when_missing(self):
        found = self.provider_service_repository.get_by_provider_and_service(
            provider_id=self.provider_a.id,
            service_id=self.service_b.id,
        )

        self.assertIsNone(found)

    def test_list_active_by_provider(self):
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
                is_active=True,
            )
        )
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_b.id,
                is_active=False,
            )
        )
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_b.id,
                service_id=self.service_a.id,
                is_active=True,
            )
        )

        results = self.provider_service_repository.list_active_by_provider(
            self.provider_a.id,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider_id, self.provider_a.id)
        self.assertEqual(results[0].service_id, self.service_a.id)

    def test_list_active_by_service(self):
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
                is_active=True,
            )
        )
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_b.id,
                service_id=self.service_a.id,
                is_active=False,
            )
        )
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_b.id,
                is_active=True,
            )
        )

        results = self.provider_service_repository.list_active_by_service(
            self.service_a.id,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].service_id, self.service_a.id)
        self.assertEqual(results[0].provider_id, self.provider_a.id)

    def test_listings_are_deterministic(self):
        first = ProviderService(
            id=uuid4(),
            provider_id=self.provider_a.id,
            service_id=self.service_a.id,
            is_active=True,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        second = ProviderService(
            id=uuid4(),
            provider_id=self.provider_a.id,
            service_id=self.service_b.id,
            is_active=True,
            created_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        self.provider_service_repository.save(second)
        self.provider_service_repository.save(first)

        results = self.provider_service_repository.list_active_by_provider(
            self.provider_a.id,
        )

        self.assertEqual(results[0].id, first.id)
        self.assertEqual(results[1].id, second.id)

    def test_constraint_provider_service_unique(self):
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
            )
        )

        with self.assertRaises(IntegrityError):
            self.provider_service_repository.save(
                self._build_provider_service(
                    provider_id=self.provider_a.id,
                    service_id=self.service_a.id,
                )
            )

    def test_same_provider_can_offer_different_services(self):
        first = self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
            )
        )
        second = self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_b.id,
            )
        )

        self.assertEqual(first.provider_id, second.provider_id)
        self.assertNotEqual(first.service_id, second.service_id)

    def test_different_providers_can_offer_same_service(self):
        first = self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
            )
        )
        second = self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_b.id,
                service_id=self.service_a.id,
            )
        )

        self.assertEqual(first.service_id, second.service_id)
        self.assertNotEqual(first.provider_id, second.provider_id)

    def test_protect_prevents_provider_delete_when_linked(self):
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
            )
        )

        with self.assertRaises(ProtectedError):
            ProviderModel.objects.get(id=self.provider_a.id).delete()

    def test_protect_prevents_service_delete_when_linked(self):
        self.provider_service_repository.save(
            self._build_provider_service(
                provider_id=self.provider_a.id,
                service_id=self.service_a.id,
            )
        )

        with self.assertRaises(ProtectedError):
            ServiceModel.objects.get(id=self.service_a.id).delete()
