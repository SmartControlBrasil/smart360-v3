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
    EconomicSettlement,
    CreditWallet,
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
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> OpportunityPricingQuote:
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
