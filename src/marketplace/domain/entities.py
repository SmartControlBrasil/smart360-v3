from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


@dataclass(slots=True)
class ServiceCategory:
    id: UUID
    name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        normalized_slug = self.slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service category name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service category slug cannot be empty.")

        self.name = normalized_name
        self.slug = normalized_slug
        self.description = self.description.strip()

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(slots=True)
class Service:
    id: UUID
    category_id: UUID
    name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.category_id is None:
            raise ValueError("Service category_id is required.")
        if not isinstance(self.category_id, UUID):
            raise ValueError(
                "Service category_id must be a valid UUID instance."
            )

        normalized_name = self.name.strip()
        normalized_slug = self.slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service slug cannot be empty.")

        self.name = normalized_name
        self.slug = normalized_slug
        self.description = self.description.strip()

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(slots=True)
class Provider:
    id: UUID
    organization_id: UUID
    display_name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.organization_id is None:
            raise ValueError("Provider organization_id is required.")
        if not isinstance(self.organization_id, UUID):
            raise ValueError(
                "Provider organization_id must be a valid UUID instance."
            )

        normalized_display_name = self.display_name.strip()
        normalized_slug = self.slug.strip().lower()

        if not normalized_display_name:
            raise ValueError("Provider display_name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Provider slug cannot be empty.")

        self.display_name = normalized_display_name
        self.slug = normalized_slug
        self.description = self.description.strip()

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(slots=True)
class ProviderService:
    id: UUID
    provider_id: UUID
    service_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.provider_id is None:
            raise ValueError("ProviderService provider_id is required.")
        if not isinstance(self.provider_id, UUID):
            raise ValueError(
                "ProviderService provider_id must be a valid UUID instance."
            )

        if self.service_id is None:
            raise ValueError("ProviderService service_id is required.")
        if not isinstance(self.service_id, UUID):
            raise ValueError(
                "ProviderService service_id must be a valid UUID instance."
            )

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


class ServiceRequestStatus(StrEnum):
    OPEN = "open"
    CANCELLED = "cancelled"
    CLOSED = "closed"


@dataclass(slots=True)
class ServiceRequest:
    id: UUID
    organization_id: UUID
    service_id: UUID
    title: str
    description: str
    status: ServiceRequestStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.organization_id is None:
            raise ValueError("ServiceRequest organization_id is required.")
        if not isinstance(self.organization_id, UUID):
            raise ValueError(
                "ServiceRequest organization_id must be a valid UUID instance."
            )

        if self.service_id is None:
            raise ValueError("ServiceRequest service_id is required.")
        if not isinstance(self.service_id, UUID):
            raise ValueError(
                "ServiceRequest service_id must be a valid UUID instance."
            )

        normalized_title = self.title.strip()
        if not normalized_title:
            raise ValueError("ServiceRequest title cannot be empty.")

        if not isinstance(self.status, ServiceRequestStatus):
            raise ValueError("ServiceRequest status must be a ServiceRequestStatus.")

        self.title = normalized_title
        self.description = self.description.strip()

    def cancel(self) -> None:
        if self.status is not ServiceRequestStatus.OPEN:
            raise ValueError("Only OPEN service requests can be cancelled.")
        self.status = ServiceRequestStatus.CANCELLED

    def close(self) -> None:
        if self.status is not ServiceRequestStatus.OPEN:
            raise ValueError("Only OPEN service requests can be closed.")
        self.status = ServiceRequestStatus.CLOSED
