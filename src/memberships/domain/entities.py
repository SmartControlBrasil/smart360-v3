from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class MembershipRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


@dataclass(slots=True)
class Membership:
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: MembershipRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def change_role(self, role: MembershipRole) -> None:
        self.role = role
