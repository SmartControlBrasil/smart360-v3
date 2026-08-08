from uuid import UUID

from django.test import SimpleTestCase

from src.marketplace.application.use_cases import CreateServiceCategory
from src.marketplace.domain.entities import ServiceCategory


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
