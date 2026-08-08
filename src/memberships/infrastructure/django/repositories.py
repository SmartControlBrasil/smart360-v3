from uuid import UUID

from src.memberships.application.ports import MembershipRepository
from src.memberships.domain.entities import Membership, MembershipRole
from src.memberships.infrastructure.django.memberships.models import MembershipModel


class DjangoMembershipRepository(MembershipRepository):

    @staticmethod
    def _to_entity(model: MembershipModel) -> Membership:
        return Membership(
            id=model.id,
            user_id=model.user_id,
            organization_id=model.organization_id,
            role=MembershipRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, membership: Membership) -> Membership:
        model, _ = MembershipModel.objects.update_or_create(
            id=membership.id,
            defaults={
                "user_id": membership.user_id,
                "organization_id": membership.organization_id,
                "role": membership.role.value,
                "is_active": membership.is_active,
            },
        )

        return self._to_entity(model)

    def get_by_id(self, membership_id: UUID) -> Membership | None:
        try:
            model = MembershipModel.objects.get(id=membership_id)
        except MembershipModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_user_and_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> Membership | None:
        try:
            model = MembershipModel.objects.get(
                user_id=user_id,
                organization_id=organization_id,
            )
        except MembershipModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_by_user(self, user_id: UUID) -> list[Membership]:
        models = MembershipModel.objects.filter(
            user_id=user_id,
        ).order_by("created_at")

        return [self._to_entity(model) for model in models]
