from datetime import datetime, timezone
from uuid import uuid4

from src.marketplace.application.ports import ServiceCategoryRepository
from src.marketplace.domain.entities import ServiceCategory


class CreateServiceCategory:
    def __init__(self, repository: ServiceCategoryRepository):
        self.repository = repository

    def execute(
        self,
        *,
        name: str,
        slug: str,
        description: str = "",
    ) -> ServiceCategory:
        normalized_name = name.strip()
        normalized_slug = slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service category name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service category slug cannot be empty.")

        existing = self.repository.get_by_slug(normalized_slug)

        if existing is not None:
            raise ValueError("Service category slug already exists.")

        now = datetime.now(timezone.utc)

        service_category = ServiceCategory(
            id=uuid4(),
            name=normalized_name,
            slug=normalized_slug,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.repository.save(service_category)
