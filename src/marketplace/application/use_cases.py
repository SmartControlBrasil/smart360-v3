from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.marketplace.application.ports import (
    ProviderRepository,
    ProviderServiceRepository,
    ServiceCategoryRepository,
    ServiceRepository,
)
from src.marketplace.domain.entities import (
    Provider,
    ProviderService,
    Service,
    ServiceCategory,
)
from src.organizations.application.ports import OrganizationRepository


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


class CreateProvider:
    def __init__(
        self,
        provider_repository: ProviderRepository,
        organization_repository: OrganizationRepository,
    ):
        self.provider_repository = provider_repository
        self.organization_repository = organization_repository

    def execute(
        self,
        *,
        organization_id: UUID,
        display_name: str,
        slug: str,
        description: str = "",
    ) -> Provider:
        if organization_id is None:
            raise ValueError("Provider organization_id is required.")
        if not isinstance(organization_id, UUID):
            raise ValueError(
                "Provider organization_id must be a valid UUID instance."
            )

        organization = self.organization_repository.get_by_id(
            organization_id,
        )

        if organization is None:
            raise ValueError("Organization does not exist.")

        if not organization.is_active:
            raise ValueError("Organization is inactive.")

        normalized_display_name = display_name.strip()
        normalized_slug = slug.strip().lower()

        if not normalized_display_name:
            raise ValueError("Provider display_name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Provider slug cannot be empty.")

        existing = self.provider_repository.get_by_slug(
            normalized_slug,
        )

        if existing is not None:
            raise ValueError("Provider slug already exists.")

        now = datetime.now(timezone.utc)

        provider = Provider(
            id=uuid4(),
            organization_id=organization_id,
            display_name=normalized_display_name,
            slug=normalized_slug,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.provider_repository.save(provider)


class CreateProviderService:
    def __init__(
        self,
        provider_service_repository: ProviderServiceRepository,
        provider_repository: ProviderRepository,
        service_repository: ServiceRepository,
    ):
        self.provider_service_repository = provider_service_repository
        self.provider_repository = provider_repository
        self.service_repository = service_repository

    def execute(
        self,
        *,
        provider_id: UUID,
        service_id: UUID,
    ) -> ProviderService:
        if provider_id is None:
            raise ValueError("ProviderService provider_id is required.")
        if not isinstance(provider_id, UUID):
            raise ValueError(
                "ProviderService provider_id must be a valid UUID instance."
            )

        if service_id is None:
            raise ValueError("ProviderService service_id is required.")
        if not isinstance(service_id, UUID):
            raise ValueError(
                "ProviderService service_id must be a valid UUID instance."
            )

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        service = self.service_repository.get_by_id(service_id)
        if service is None:
            raise ValueError("Service does not exist.")
        if not service.is_active:
            raise ValueError("Service is inactive.")

        existing = self.provider_service_repository.get_by_provider_and_service(
            provider_id=provider_id,
            service_id=service_id,
        )
        if existing is not None:
            raise ValueError("ProviderService relationship already exists.")

        now = datetime.now(timezone.utc)
        provider_service = ProviderService(
            id=uuid4(),
            provider_id=provider_id,
            service_id=service_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.provider_service_repository.save(provider_service)
