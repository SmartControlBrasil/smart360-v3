from typing import Protocol
from uuid import UUID

from src.memberships.domain.entities import Membership


class MembershipRepository(Protocol):
    def save(self, membership: Membership) -> Membership:
        ...

    def get_by_id(self, membership_id: UUID) -> Membership | None:
        ...

    def get_by_user_and_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> Membership | None:
        ...

    def list_by_user(self, user_id: UUID) -> list[Membership]:
        ...
