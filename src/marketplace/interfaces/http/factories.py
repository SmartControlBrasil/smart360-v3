from src.marketplace.application.ports import OpportunityPricingPolicy, CreditCostPolicy
from src.marketplace.application.use_cases import (
    AuthenticatedProviderMarketplaceService,
    GetOpportunityPreview,
    GetOpportunityUnlockQuote,
    UnlockOpportunityWithCredits,
    GetUnlockedOpportunityContact,
    ListProviderOpportunityInbox,
    ListProviderUnlockedOpportunities,
)
from src.marketplace.infrastructure.django.repositories import (
    DjangoOpportunityInvitationRepository,
    DjangoOpportunityRepository,
    DjangoServiceRequestRepository,
    DjangoProviderRepository,
    DjangoOpportunityAccessRepository,
    DjangoOpportunityInterestRepository,
    DjangoEconomicSettlementRepository,
    DjangoCreditWalletRepository,
    DjangoCreditLedgerEntryRepository,
    DjangoOpportunityUnlockAtomicWriter,
    DjangoOrganizationMemberProviderResolver,
    DjangoProtectedDataReadAuditWriter,
)
from src.marketplace.infrastructure.policies import (
    UnconfiguredOpportunityPricingPolicy,
    UnconfiguredCreditCostPolicy,
)


def build_authenticated_provider_marketplace_service(
    *,
    pricing_policy: OpportunityPricingPolicy | None = None,
    credit_cost_policy: CreditCostPolicy | None = None,
) -> AuthenticatedProviderMarketplaceService:
    """
    Factory function (Composition Root) that wires up Django ORM repositories
    and application policies to produce an AuthenticatedProviderMarketplaceService.
    """
    invitation_repo = DjangoOpportunityInvitationRepository()
    opportunity_repo = DjangoOpportunityRepository()
    service_request_repo = DjangoServiceRequestRepository()
    provider_repo = DjangoProviderRepository()
    access_repo = DjangoOpportunityAccessRepository()
    interest_repo = DjangoOpportunityInterestRepository()
    settlement_repo = DjangoEconomicSettlementRepository()
    wallet_repo = DjangoCreditWalletRepository()
    ledger_repo = DjangoCreditLedgerEntryRepository()
    unlock_atomic_writer = DjangoOpportunityUnlockAtomicWriter()
    resolver = DjangoOrganizationMemberProviderResolver()

    actual_pricing_policy = pricing_policy or UnconfiguredOpportunityPricingPolicy()
    actual_cost_policy = credit_cost_policy or UnconfiguredCreditCostPolicy()

    get_preview = GetOpportunityPreview(
        opportunity_invitation_repository=invitation_repo,
        opportunity_repository=opportunity_repo,
        service_request_repository=service_request_repo,
        provider_repository=provider_repo,
    )

    get_quote = GetOpportunityUnlockQuote(
        opportunity_invitation_repository=invitation_repo,
        opportunity_repository=opportunity_repo,
        service_request_repository=service_request_repo,
        provider_repository=provider_repo,
        opportunity_access_repository=access_repo,
        opportunity_pricing_policy=actual_pricing_policy,
    )

    unlock_use_case = UnlockOpportunityWithCredits(
        opportunity_invitation_repository=invitation_repo,
        opportunity_repository=opportunity_repo,
        service_request_repository=service_request_repo,
        provider_repository=provider_repo,
        opportunity_access_repository=access_repo,
        opportunity_interest_repository=interest_repo,
        economic_settlement_repository=settlement_repo,
        credit_wallet_repository=wallet_repo,
        credit_ledger_entry_repository=ledger_repo,
        opportunity_pricing_policy=actual_pricing_policy,
        credit_cost_policy=actual_cost_policy,
        unlock_atomic_writer=unlock_atomic_writer,
    )

    audit_writer = DjangoProtectedDataReadAuditWriter()

    get_contact = GetUnlockedOpportunityContact(
        opportunity_access_repository=access_repo,
        opportunity_repository=opportunity_repo,
        service_request_repository=service_request_repo,
        provider_repository=provider_repo,
        audit_writer=audit_writer,
    )

    list_inbox = ListProviderOpportunityInbox(
        opportunity_invitation_repository=invitation_repo,
        opportunity_repository=opportunity_repo,
        service_request_repository=service_request_repo,
        provider_repository=provider_repo,
    )

    list_unlocked = ListProviderUnlockedOpportunities(
        opportunity_access_repository=access_repo,
        provider_repository=provider_repo,
    )

    return AuthenticatedProviderMarketplaceService(
        provider_identity_resolver=resolver,
        invitation_repository=invitation_repo,
        get_opportunity_preview=get_preview,
        get_opportunity_unlock_quote=get_quote,
        unlock_opportunity_with_credits=unlock_use_case,
        get_unlocked_opportunity_contact=get_contact,
        list_provider_opportunity_inbox=list_inbox,
        list_provider_unlocked_opportunities=list_unlocked,
    )
