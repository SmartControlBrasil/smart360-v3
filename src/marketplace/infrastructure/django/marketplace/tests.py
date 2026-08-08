from datetime import datetime, timezone
from uuid import uuid4

from django.test import TestCase

from src.marketplace.domain.entities import ServiceCategory
from src.marketplace.infrastructure.django.marketplace.models import (
    ServiceCategoryModel,
)
from src.marketplace.infrastructure.django.repositories import (
    DjangoServiceCategoryRepository,
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
