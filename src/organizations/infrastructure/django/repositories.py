from uuid import UUID

from src.organizations.application.ports import OrganizationRepository
from src.organizations.domain.entities import Organization
from src.organizations.infrastructure.django.organizations.models import (
    OrganizationModel,
)


class DjangoOrganizationRepository(OrganizationRepository):

    @staticmethod
    def _to_entity(model: OrganizationModel) -> Organization:
        return Organization(
            id=model.id,
            name=model.name,
            slug=model.slug,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, organization: Organization) -> Organization:
        model, _ = OrganizationModel.objects.update_or_create(
            id=organization.id,
            defaults={
                "name": organization.name,
                "slug": organization.slug,
                "is_active": organization.is_active,
            },
        )

        return self._to_entity(model)

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        try:
            model = OrganizationModel.objects.get(id=organization_id)
        except OrganizationModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_slug(self, slug: str) -> Organization | None:
        try:
            model = OrganizationModel.objects.get(slug=slug)
        except OrganizationModel.DoesNotExist:
            return None

        return self._to_entity(model)
