from dataclasses import dataclass
from datetime import datetime
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
