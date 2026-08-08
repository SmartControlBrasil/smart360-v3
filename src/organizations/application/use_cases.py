from datetime import datetime, timezone
from uuid import uuid4

from src.organizations.application.ports import OrganizationRepository
from src.organizations.domain.entities import Organization


class CreateOrganization:
    def __init__(self, repository: OrganizationRepository):
        self.repository = repository

    def execute(self, *, name: str, slug: str) -> Organization:
        existing = self.repository.get_by_slug(slug)

        if existing is not None:
            raise ValueError("Organization slug already exists.")

        now = datetime.now(timezone.utc)

        organization = Organization(
            id=uuid4(),
            name=name.strip(),
            slug=slug.strip().lower(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.repository.save(organization)
