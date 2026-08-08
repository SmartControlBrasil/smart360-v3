from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.memberships.application.ports import MembershipRepository
from src.memberships.domain.entities import Membership, MembershipRole


class AddMemberToOrganization:
    def __init__(self, repository: MembershipRepository):
        self.repository = repository

    def execute(
        self,
        *,
        user_id: UUID,
        organization_id: UUID,
        role: MembershipRole = MembershipRole.MEMBER,
    ) -> Membership:
        existing = self.repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        )

        if existing is not None:
            raise ValueError(
                "User already belongs to this organization."
            )

        now = datetime.now(timezone.utc)

        membership = Membership(
            id=uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            role=role,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.repository.save(membership)
