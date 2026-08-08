from typing import Protocol
from uuid import UUID

from src.marketplace.domain.entities import (
    Provider,
    Service,
    ServiceCategory,
)


class ServiceCategoryRepository(Protocol):
    def save(
        self,
        service_category: ServiceCategory,
    ) -> ServiceCategory:
        ...

    def get_by_id(
        self,
        service_category_id: UUID,
    ) -> ServiceCategory | None:
        ...

    def get_by_slug(self, slug: str) -> ServiceCategory | None:
        ...

    def list_active(self) -> list[ServiceCategory]:
        ...


class ServiceRepository(Protocol):
    def save(self, service: Service) -> Service:
        ...

    def get_by_id(self, service_id: UUID) -> Service | None:
        ...

    def get_by_category_and_slug(
        self,
        category_id: UUID,
        slug: str,
    ) -> Service | None:
        ...

    def list_active_by_category(
        self,
        category_id: UUID,
    ) -> list[Service]:
        ...


class ProviderRepository(Protocol):
    def save(self, provider: Provider) -> Provider:
        ...

    def get_by_id(self, provider_id: UUID) -> Provider | None:
        ...

    def get_by_slug(self, slug: str) -> Provider | None:
        ...

    def list_active_by_organization(
        self,
        organization_id: UUID,
    ) -> list[Provider]:
        ...
