from typing import Protocol
from uuid import UUID

from src.organizations.domain.entities import Organization


class OrganizationRepository(Protocol):
    def save(self, organization: Organization) -> Organization:
        ...

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        ...

    def get_by_slug(self, slug: str) -> Organization | None:
        ...

