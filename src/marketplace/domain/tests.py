from datetime import datetime, timezone
from uuid import uuid4

from django.test import SimpleTestCase

from src.marketplace.domain.entities import (
    Provider,
    Service,
    ServiceCategory,
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
