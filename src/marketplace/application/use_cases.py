from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.marketplace.application.ports import (
    ServiceCategoryRepository,
    ServiceRepository,
)
from src.marketplace.domain.entities import Service, ServiceCategory


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


class CreateService:
    def __init__(
        self,
        service_repository: ServiceRepository,
        category_repository: ServiceCategoryRepository,
    ):
        self.service_repository = service_repository
        self.category_repository = category_repository

    def execute(
        self,
        *,
        category_id: UUID,
        name: str,
        slug: str,
        description: str = "",
    ) -> Service:
        if category_id is None:
            raise ValueError("Service category_id is required.")
        if not isinstance(category_id, UUID):
            raise ValueError(
                "Service category_id must be a valid UUID instance."
            )

        category = self.category_repository.get_by_id(category_id)

        if category is None:
            raise ValueError("Service category does not exist.")

        if not category.is_active:
            raise ValueError("Service category is inactive.")

        normalized_name = name.strip()
        normalized_slug = slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service slug cannot be empty.")

        existing = self.service_repository.get_by_category_and_slug(
            category_id=category_id,
            slug=normalized_slug,
        )

        if existing is not None:
            raise ValueError(
                "Service slug already exists in this category."
            )

        now = datetime.now(timezone.utc)

        service = Service(
            id=uuid4(),
            category_id=category_id,
            name=normalized_name,
            slug=normalized_slug,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.service_repository.save(service)
