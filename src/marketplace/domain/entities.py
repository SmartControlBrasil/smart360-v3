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


class OpportunityStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Opportunity:
    id: UUID
    service_request_id: UUID
    status: OpportunityStatus
    max_accesses: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.service_request_id is None:
            raise ValueError("Opportunity service_request_id is required.")
        if not isinstance(self.service_request_id, UUID):
            raise ValueError(
                "Opportunity service_request_id must be a valid UUID instance."
            )

        if not isinstance(self.status, OpportunityStatus):
            raise ValueError("Opportunity status must be an OpportunityStatus.")

        if isinstance(self.max_accesses, bool) or not isinstance(
            self.max_accesses,
            int,
        ):
            raise ValueError("Opportunity max_accesses must be an integer.")
        if self.max_accesses < 1:
            raise ValueError("Opportunity max_accesses must be at least 1.")

    def close(self) -> None:
        if self.status is not OpportunityStatus.OPEN:
            raise ValueError("Only OPEN opportunities can be closed.")
        self.status = OpportunityStatus.CLOSED

    def cancel(self) -> None:
        if self.status is not OpportunityStatus.OPEN:
            raise ValueError("Only OPEN opportunities can be cancelled.")
        self.status = OpportunityStatus.CANCELLED


@dataclass(slots=True)
class OpportunityAccess:
    id: UUID
    opportunity_id: UUID
    provider_id: UUID
    created_at: datetime

    def __post_init__(self) -> None:
        if self.opportunity_id is None:
            raise ValueError("OpportunityAccess opportunity_id is required.")
        if not isinstance(self.opportunity_id, UUID):
            raise ValueError(
                "OpportunityAccess opportunity_id must be a valid UUID instance."
            )

        if self.provider_id is None:
            raise ValueError("OpportunityAccess provider_id is required.")
        if not isinstance(self.provider_id, UUID):
            raise ValueError(
                "OpportunityAccess provider_id must be a valid UUID instance."
            )


@dataclass(slots=True, frozen=True)
class MatchingResult:
    provider: Provider
    score: int
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.provider, Provider):
            raise ValueError("MatchingResult provider must be a Provider domain object.")

        if isinstance(self.score, bool) or not isinstance(self.score, int):
            raise ValueError("MatchingResult score must be an integer.")

        if not (0 <= self.score <= 100):
            raise ValueError("MatchingResult score must be between 0 and 100.")

        if not isinstance(self.reasons, tuple):
            raise ValueError("MatchingResult reasons must be a tuple of strings.")

        if not self.reasons:
            raise ValueError("MatchingResult reasons cannot be empty.")

        normalized_reasons: list[str] = []
        for reason in self.reasons:
            if not isinstance(reason, str):
                raise ValueError("MatchingResult reason must be a string.")
            normalized = reason.strip()
            if not normalized:
                raise ValueError("MatchingResult reason cannot be empty or blank.")
            normalized_reasons.append(normalized)

        object.__setattr__(self, "reasons", tuple(normalized_reasons))


@dataclass(slots=True)
class OpportunityInvitation:
    id: UUID
    opportunity_id: UUID
    provider_id: UUID
    created_at: datetime

    def __post_init__(self) -> None:
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("OpportunityInvitation id must be a valid UUID instance.")
        if self.opportunity_id is None or not isinstance(self.opportunity_id, UUID):
            raise ValueError("OpportunityInvitation opportunity_id must be a valid UUID instance.")
        if self.provider_id is None or not isinstance(self.provider_id, UUID):
            raise ValueError("OpportunityInvitation provider_id must be a valid UUID instance.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("OpportunityInvitation created_at must be a datetime instance.")
        if self.created_at.tzinfo is None:
            raise ValueError("OpportunityInvitation created_at must be timezone-aware.")
