from typing import Protocol
from uuid import UUID


from src.marketplace.domain.entities import (
    MatchingResult,
    Opportunity,
    OpportunityAccess,
    OpportunityInvitation,
    OpportunityInterest,
    Provider,
    ProviderService,
    Service,
    ServiceCategory,
    ServiceRequest,
    AccessEntitlementDecision,
    OpportunityPricingQuote,
    OpportunityUnlockPricingConfiguration,
    EconomicSettlement,
    CreditWallet,
    CreditLedgerEntry,
    Money,
    OpportunityStatus,
    ProviderOpportunityInboxItem,
    ProviderUnlockedOpportunityItem,
    ProviderUnlockedOpportunityPage,
)


class ServiceCategoryRepository(Protocol):
    def save(
        self,
        service_category: ServiceCategory,
    ) -> ServiceCategory:
        ...

    def get_by_id(
        self,
        service_category_id: UUID,
    ) -> ServiceCategory | None:
        ...

    def get_by_slug(self, slug: str) -> ServiceCategory | None:
        ...

    def list_active(self) -> list[ServiceCategory]:
        ...


class ServiceRepository(Protocol):
    def save(self, service: Service) -> Service:
        ...

    def get_by_id(self, service_id: UUID) -> Service | None:
        ...

    def get_by_category_and_slug(
        self,
        category_id: UUID,
        slug: str,
    ) -> Service | None:
        ...

    def list_active_by_category(
        self,
        category_id: UUID,
    ) -> list[Service]:
        ...


class ProviderRepository(Protocol):
    def save(self, provider: Provider) -> Provider:
        ...

    def get_by_id(self, provider_id: UUID) -> Provider | None:
        ...

    def get_by_slug(self, slug: str) -> Provider | None:
        ...

    def list_active_by_organization(
        self,
        organization_id: UUID,
    ) -> list[Provider]:
        ...


class ProviderServiceRepository(Protocol):
    def save(
        self,
        provider_service: ProviderService,
    ) -> ProviderService:
        ...

    def get_by_id(
        self,
        provider_service_id: UUID,
    ) -> ProviderService | None:
        ...

    def get_by_provider_and_service(
        self,
        provider_id: UUID,
        service_id: UUID,
    ) -> ProviderService | None:
        ...

    def list_active_by_provider(
        self,
        provider_id: UUID,
    ) -> list[ProviderService]:
        ...

    def list_active_by_service(
        self,
        service_id: UUID,
    ) -> list[ProviderService]:
        ...


class ServiceRequestRepository(Protocol):
    def save(
        self,
        service_request: ServiceRequest,
    ) -> ServiceRequest:
        ...

    def get_by_id(
        self,
        service_request_id: UUID,
    ) -> ServiceRequest | None:
        ...

    def list_open_by_organization(
        self,
        organization_id: UUID,
    ) -> list[ServiceRequest]:
        ...

    def list_open_by_service(
        self,
        service_id: UUID,
    ) -> list[ServiceRequest]:
        ...


class OpportunityRepository(Protocol):
    def save(self, opportunity: Opportunity) -> Opportunity:
        ...

    def get_by_id(self, opportunity_id: UUID) -> Opportunity | None:
        ...

    def get_by_service_request(
        self,
        service_request_id: UUID,
    ) -> Opportunity | None:
        ...

    def list_open(self) -> list[Opportunity]:
        ...


class OpportunityAccessRepository(Protocol):
    def save(self, access: OpportunityAccess) -> OpportunityAccess:
        ...

    def get_by_id(self, access_id: UUID) -> OpportunityAccess | None:
        ...

    def get_by_opportunity_and_provider(
        self,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityAccess | None:
        ...

    def list_by_opportunity(
        self,
        opportunity_id: UUID,
    ) -> list[OpportunityAccess]:
        ...

    def list_by_provider(
        self,
        provider_id: UUID,
    ) -> list[OpportunityAccess]:
        ...

    def count_by_opportunity(self, opportunity_id: UUID) -> int:
        ...

    def list_unlocked_items_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProviderUnlockedOpportunityItem], int]:
        ...


class MatchingPolicy(Protocol):
    def evaluate(
        self,
        *,
        service_request: ServiceRequest,
        provider: Provider,
    ) -> MatchingResult:
        ...


class OpportunityInvitationRepository(Protocol):
    def save(
        self,
        invitation: OpportunityInvitation,
    ) -> OpportunityInvitation:
        ...

    def get_by_id(
        self,
        invitation_id: UUID,
    ) -> OpportunityInvitation | None:
        ...

    def get_by_opportunity_and_provider(
        self,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityInvitation | None:
        ...

    def list_by_opportunity(
        self,
        opportunity_id: UUID,
    ) -> list[OpportunityInvitation]:
        ...

    def list_by_provider(
        self,
        provider_id: UUID,
    ) -> list[OpportunityInvitation]:
        ...

    def list_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OpportunityInvitation], int]:
        ...

    def list_inbox_items_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: OpportunityStatus | None = None,
    ) -> tuple[list[ProviderOpportunityInboxItem], int]:
        ...

    def count_by_opportunity(self, opportunity_id: UUID) -> int:
        ...


class OpportunityInterestRepository(Protocol):
    def save(
        self,
        interest: OpportunityInterest,
    ) -> OpportunityInterest:
        ...

    def get_by_id(
        self,
        interest_id: UUID,
    ) -> OpportunityInterest | None:
        ...

    def get_by_invitation(
        self,
        invitation_id: UUID,
    ) -> OpportunityInterest | None:
        ...


class AccessEntitlementPolicy(Protocol):
    def decide(
        self,
        *,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> AccessEntitlementDecision:
        ...


class OpportunityPricingPolicy(Protocol):
    def quote(
        self,
        *,
        interest: OpportunityInterest | None = None,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> OpportunityPricingQuote:
        ...


class OpportunityUnlockPricingConfigurationRepository(Protocol):
    def get_active_default(self) -> OpportunityUnlockPricingConfiguration | None:
        ...


class EconomicSettlementRepository(Protocol):
    def save(
        self,
        settlement: EconomicSettlement,
    ) -> EconomicSettlement:
        ...

    def get_by_id(
        self,
        settlement_id: UUID,
    ) -> EconomicSettlement | None:
        ...

    def get_by_interest(
        self,
        interest_id: UUID,
    ) -> EconomicSettlement | None:
        ...


class CreditWalletRepository(Protocol):
    def save(
        self,
        wallet: CreditWallet,
    ) -> CreditWallet:
        ...

    def get_by_id(
        self,
        wallet_id: UUID,
    ) -> CreditWallet | None:
        ...

    def get_by_organization(
        self,
        organization_id: UUID,
    ) -> CreditWallet | None:
        ...


class CreditLedgerEntryRepository(Protocol):
    def save(
        self,
        entry: CreditLedgerEntry,
    ) -> CreditLedgerEntry:
        ...

    def get_by_id(
        self,
        entry_id: UUID,
    ) -> CreditLedgerEntry | None:
        ...

    def list_by_wallet(
        self,
        wallet_id: UUID,
    ) -> list[CreditLedgerEntry]:
        ...


class CreditCostPolicy(Protocol):
    def units_required(
        self,
        *,
        price: Money,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> int:
        ...


class CreditSettlementAtomicWriter(Protocol):
    def persist(
        self,
        *,
        debit_entry: CreditLedgerEntry | None,
        settlement: EconomicSettlement,
        wallet_id: UUID,
        required_units: int,
    ) -> None:
        ...


class OpportunityUnlockAtomicWriter(Protocol):
    def persist_unlock(
        self,
        *,
        interest: OpportunityInterest,
        debit_entry: CreditLedgerEntry | None,
        settlement: EconomicSettlement,
        access: OpportunityAccess,
        wallet_id: UUID,
        required_units: int,
    ) -> None:
        ...


class ProviderIdentityResolver(Protocol):
    """
    Application port for resolving an authenticated user's Provider identity.

    Implementations live in infrastructure; application and domain remain
    framework-free.

    Raises:
        ProviderIdentityNotFound: if the user has no active provider mapping.
        AmbiguousProviderIdentity: if resolution would be ambiguous.
        RuntimeError: propagated for unexpected infrastructure failures.
    """

    def resolve(
        self,
        *,
        authenticated_user_id: UUID,
    ) -> Provider:
        ...


class ProtectedDataReadAuditWriter(Protocol):
    def record_contact_read(
        self,
        *,
        authenticated_user_id: UUID,
        provider_id: UUID,
        opportunity_id: UUID,
        service_request_id: UUID,
    ) -> None:
        ...
