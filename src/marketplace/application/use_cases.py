from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.marketplace.application.ports import (
    MatchingPolicy,
    OpportunityAccessRepository,
    OpportunityInvitationRepository,
    OpportunityInterestRepository,
    OpportunityRepository,
    ProviderRepository,
    ProviderServiceRepository,
    ServiceRequestRepository,
    ServiceCategoryRepository,
    ServiceRepository,
    AccessEntitlementPolicy,
    OpportunityPricingPolicy,
    EconomicSettlementRepository,
    CreditWalletRepository,
    CreditLedgerEntryRepository,
    CreditCostPolicy,
    CreditSettlementAtomicWriter,
    OpportunityUnlockAtomicWriter,
    ProviderIdentityResolver,
    ProtectedDataReadAuditWriter,
)
from src.marketplace.domain.entities import (
    MatchingResult,
    Opportunity,
    OpportunityAccess,
    OpportunityInvitation,
    OpportunityInterest,
    OpportunityStatus,
    Provider,
    ProviderService,
    Service,
    ServiceCategory,
    OpportunityUnlockResult,
    UnlockedOpportunityContact,
    ServiceRequest,
    ServiceRequestStatus,
    AccessEntitlementDecision,
    RequestOpportunityAccessResult,
    OpportunityPricingQuote,
    Money,
    SettlementMethod,
    EconomicSettlement,
    CreditWallet,
    CreditLedgerDirection,
    CreditLedgerEntry,
    CreditSettlementResult,
    ProtectedCommercialData,
    OpportunityPreview,
    OpportunityUnlockQuote,
    OpportunityPricingUnavailable,
    EconomicAcquisitionReconciliation,
    EconomicAcquisitionReconciliationIssue,
    ProviderOpportunityInboxItem,
    ProviderOpportunityInboxPage,
    ProviderUnlockedOpportunityItem,
    ProviderUnlockedOpportunityPage,
)
from src.organizations.application.ports import OrganizationRepository


class ProviderIdentityNotFound(Exception):
    """
    Raised when an authenticated user has no active Provider mapping.

    This is a semantically expected condition (not a programming bug).
    The caller should treat this as an identity-not-found response.
    """


class AmbiguousProviderIdentity(Exception):
    """
    Raised when resolution of an authenticated user's Provider identity
    would be ambiguous (multiple active Providers found).

    A future mechanism (e.g., explicit Provider selection) is required
    before the operation can proceed.
    """


class CreateServiceCategory:
    def __init__(self, repository: ServiceCategoryRepository):
        self.repository = repository

    def execute(
        self,
        *,
        name: str,
        slug: str,
        description: str = "",
    ) -> ServiceCategory:
        normalized_name = name.strip()
        normalized_slug = slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service category name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service category slug cannot be empty.")

        existing = self.repository.get_by_slug(normalized_slug)

        if existing is not None:
            raise ValueError("Service category slug already exists.")

        now = datetime.now(timezone.utc)

        service_category = ServiceCategory(
            id=uuid4(),
            name=normalized_name,
            slug=normalized_slug,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.repository.save(service_category)


class CreateService:
    def __init__(
        self,
        service_repository: ServiceRepository,
        category_repository: ServiceCategoryRepository,
    ):
        self.service_repository = service_repository
        self.category_repository = category_repository

    def execute(
        self,
        *,
        category_id: UUID,
        name: str,
        slug: str,
        description: str = "",
    ) -> Service:
        if category_id is None:
            raise ValueError("Service category_id is required.")
        if not isinstance(category_id, UUID):
            raise ValueError(
                "Service category_id must be a valid UUID instance."
            )

        category = self.category_repository.get_by_id(category_id)

        if category is None:
            raise ValueError("Service category does not exist.")

        if not category.is_active:
            raise ValueError("Service category is inactive.")

        normalized_name = name.strip()
        normalized_slug = slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service slug cannot be empty.")

        existing = self.service_repository.get_by_category_and_slug(
            category_id=category_id,
            slug=normalized_slug,
        )

        if existing is not None:
            raise ValueError(
                "Service slug already exists in this category."
            )

        now = datetime.now(timezone.utc)

        service = Service(
            id=uuid4(),
            category_id=category_id,
            name=normalized_name,
            slug=normalized_slug,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.service_repository.save(service)


class CreateProvider:
    def __init__(
        self,
        provider_repository: ProviderRepository,
        organization_repository: OrganizationRepository,
    ):
        self.provider_repository = provider_repository
        self.organization_repository = organization_repository

    def execute(
        self,
        *,
        organization_id: UUID,
        display_name: str,
        slug: str,
        description: str = "",
    ) -> Provider:
        if organization_id is None:
            raise ValueError("Provider organization_id is required.")
        if not isinstance(organization_id, UUID):
            raise ValueError(
                "Provider organization_id must be a valid UUID instance."
            )

        organization = self.organization_repository.get_by_id(
            organization_id,
        )

        if organization is None:
            raise ValueError("Organization does not exist.")

        if not organization.is_active:
            raise ValueError("Organization is inactive.")

        normalized_display_name = display_name.strip()
        normalized_slug = slug.strip().lower()

        if not normalized_display_name:
            raise ValueError("Provider display_name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Provider slug cannot be empty.")

        existing = self.provider_repository.get_by_slug(
            normalized_slug,
        )

        if existing is not None:
            raise ValueError("Provider slug already exists.")

        now = datetime.now(timezone.utc)

        provider = Provider(
            id=uuid4(),
            organization_id=organization_id,
            display_name=normalized_display_name,
            slug=normalized_slug,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.provider_repository.save(provider)


class CreateProviderService:
    def __init__(
        self,
        provider_service_repository: ProviderServiceRepository,
        provider_repository: ProviderRepository,
        service_repository: ServiceRepository,
    ):
        self.provider_service_repository = provider_service_repository
        self.provider_repository = provider_repository
        self.service_repository = service_repository

    def execute(
        self,
        *,
        provider_id: UUID,
        service_id: UUID,
    ) -> ProviderService:
        if provider_id is None:
            raise ValueError("ProviderService provider_id is required.")
        if not isinstance(provider_id, UUID):
            raise ValueError(
                "ProviderService provider_id must be a valid UUID instance."
            )

        if service_id is None:
            raise ValueError("ProviderService service_id is required.")
        if not isinstance(service_id, UUID):
            raise ValueError(
                "ProviderService service_id must be a valid UUID instance."
            )

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        service = self.service_repository.get_by_id(service_id)
        if service is None:
            raise ValueError("Service does not exist.")
        if not service.is_active:
            raise ValueError("Service is inactive.")

        existing = self.provider_service_repository.get_by_provider_and_service(
            provider_id=provider_id,
            service_id=service_id,
        )
        if existing is not None:
            raise ValueError("ProviderService relationship already exists.")

        now = datetime.now(timezone.utc)
        provider_service = ProviderService(
            id=uuid4(),
            provider_id=provider_id,
            service_id=service_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.provider_service_repository.save(provider_service)


class CreateServiceRequest:
    def __init__(
        self,
        service_request_repository: ServiceRequestRepository,
        organization_repository: OrganizationRepository,
        service_repository: ServiceRepository,
    ):
        self.service_request_repository = service_request_repository
        self.organization_repository = organization_repository
        self.service_repository = service_repository

    def execute(
        self,
        *,
        organization_id: UUID,
        service_id: UUID,
        title: str,
        description: str = "",
        requester_name: str = "",
        requester_email: str = "",
        requester_phone: str = "",
    ) -> ServiceRequest:
        if organization_id is None:
            raise ValueError("ServiceRequest organization_id is required.")
        if not isinstance(organization_id, UUID):
            raise ValueError(
                "ServiceRequest organization_id must be a valid UUID instance."
            )

        if service_id is None:
            raise ValueError("ServiceRequest service_id is required.")
        if not isinstance(service_id, UUID):
            raise ValueError(
                "ServiceRequest service_id must be a valid UUID instance."
            )

        organization = self.organization_repository.get_by_id(organization_id)
        if organization is None:
            raise ValueError("Organization does not exist.")
        if not organization.is_active:
            raise ValueError("Organization is inactive.")

        service = self.service_repository.get_by_id(service_id)
        if service is None:
            raise ValueError("Service does not exist.")
        if not service.is_active:
            raise ValueError("Service is inactive.")

        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("ServiceRequest title cannot be empty.")
        normalized_description = description.strip()

        normalized_req_name = requester_name.strip()
        if not normalized_req_name:
            raise ValueError("requester_name cannot be empty for new requests.")

        normalized_req_email = requester_email.strip()
        normalized_req_phone = requester_phone.strip()
        if not normalized_req_email and not normalized_req_phone:
            raise ValueError("At least one contact channel (email or phone) must be provided for new requests.")

        now = datetime.now(timezone.utc)
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=organization_id,
            service_id=service_id,
            title=normalized_title,
            description=normalized_description,
            status=ServiceRequestStatus.OPEN,
            requester_name=normalized_req_name,
            requester_email=normalized_req_email,
            requester_phone=normalized_req_phone,
            created_at=now,
            updated_at=now,
        )

        return self.service_request_repository.save(service_request)


class DiscoverCandidates:
    def __init__(
        self,
        service_request_repository: ServiceRequestRepository,
        provider_service_repository: ProviderServiceRepository,
        provider_repository: ProviderRepository,
    ):
        self.service_request_repository = service_request_repository
        self.provider_service_repository = provider_service_repository
        self.provider_repository = provider_repository

    def execute(
        self,
        *,
        service_request_id: UUID,
    ) -> list[Provider]:
        if service_request_id is None:
            raise ValueError("ServiceRequest id is required.")
        if not isinstance(service_request_id, UUID):
            raise ValueError("ServiceRequest id must be a valid UUID instance.")

        service_request = self.service_request_repository.get_by_id(service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")
        if service_request.status is not ServiceRequestStatus.OPEN:
            raise ValueError("ServiceRequest must be OPEN for candidate discovery.")

        provider_services = self.provider_service_repository.list_active_by_service(
            service_request.service_id,
        )

        unique_providers: dict[UUID, Provider] = {}
        for provider_service in provider_services:
            provider = self.provider_repository.get_by_id(provider_service.provider_id)
            if provider is None:
                continue
            if not provider.is_active:
                continue
            unique_providers[provider.id] = provider

        return sorted(
            unique_providers.values(),
            key=lambda provider: (provider.display_name.casefold(), str(provider.id)),
        )


class CreateOpportunity:
    def __init__(
        self,
        opportunity_repository: OpportunityRepository,
        service_request_repository: ServiceRequestRepository,
    ):
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository

    def execute(
        self,
        *,
        service_request_id: UUID,
        max_accesses: int = 3,
    ) -> Opportunity:
        if service_request_id is None:
            raise ValueError("Opportunity service_request_id is required.")
        if not isinstance(service_request_id, UUID):
            raise ValueError(
                "Opportunity service_request_id must be a valid UUID instance."
            )

        if isinstance(max_accesses, bool) or not isinstance(max_accesses, int):
            raise ValueError("Opportunity max_accesses must be an integer.")
        if max_accesses < 1:
            raise ValueError("Opportunity max_accesses must be at least 1.")

        service_request = self.service_request_repository.get_by_id(
            service_request_id,
        )
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")
        if service_request.status is not ServiceRequestStatus.OPEN:
            raise ValueError("ServiceRequest must be OPEN to create an Opportunity.")

        existing = self.opportunity_repository.get_by_service_request(
            service_request_id,
        )
        if existing is not None:
            raise ValueError("Opportunity for this ServiceRequest already exists.")

        now = datetime.now(timezone.utc)
        opportunity = Opportunity(
            id=uuid4(),
            service_request_id=service_request_id,
            status=OpportunityStatus.OPEN,
            max_accesses=max_accesses,
            created_at=now,
            updated_at=now,
        )
        return self.opportunity_repository.save(opportunity)


class GrantOpportunityAccess:
    def __init__(
        self,
        opportunity_repository: OpportunityRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        provider_repository: ProviderRepository,
    ):
        self.opportunity_repository = opportunity_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.provider_repository = provider_repository

    def execute(
        self,
        *,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityAccess:
        if opportunity_id is None:
            raise ValueError("OpportunityAccess opportunity_id is required.")
        if not isinstance(opportunity_id, UUID):
            raise ValueError(
                "OpportunityAccess opportunity_id must be a valid UUID instance."
            )

        if provider_id is None:
            raise ValueError("OpportunityAccess provider_id is required.")
        if not isinstance(provider_id, UUID):
            raise ValueError(
                "OpportunityAccess provider_id must be a valid UUID instance."
            )

        opportunity = self.opportunity_repository.get_by_id(opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity_id,
            provider_id=provider_id,
        )
        if existing is not None:
            raise ValueError("OpportunityAccess already exists for this provider.")

        # Eligibility checks (ProviderService, matching policies) are intentionally
        # out of scope for this sprint and will be handled by future discovery layers.
        granted_accesses = self.opportunity_access_repository.count_by_opportunity(
            opportunity_id,
        )
        if granted_accesses >= opportunity.max_accesses:
            raise ValueError("Opportunity max_accesses limit has been reached.")

        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opportunity_id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        return self.opportunity_access_repository.save(access)


class RankCandidates:
    def __init__(
        self,
        discover_candidates: DiscoverCandidates,
        service_request_repository: ServiceRequestRepository,
        matching_policy: MatchingPolicy,
    ):
        self.discover_candidates = discover_candidates
        self.service_request_repository = service_request_repository
        self.matching_policy = matching_policy

    def execute(
        self,
        *,
        service_request_id: UUID,
    ) -> list[MatchingResult]:
        if service_request_id is None:
            raise ValueError("ServiceRequest id is required.")
        if not isinstance(service_request_id, UUID):
            raise ValueError("ServiceRequest id must be a valid UUID instance.")

        # Let DiscoverCandidates run validation on service_request status/existence
        # and fetch technical candidates.
        providers = self.discover_candidates.execute(service_request_id=service_request_id)

        # Retrieve the service request domain object to pass context to the matching policy.
        service_request = self.service_request_repository.get_by_id(service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")

        results = [
            self.matching_policy.evaluate(service_request=service_request, provider=provider)
            for provider in providers
        ]

        # Deterministic ordering:
        # 1. score descending
        # 2. display_name casefold() (case-insensitive alphabetical)
        # 3. provider.id string
        return sorted(
            results,
            key=lambda res: (
                -res.score,
                res.provider.display_name.casefold(),
                str(res.provider.id),
            ),
        )


class InviteProviderToOpportunity:
    def __init__(
        self,
        opportunity_repository: OpportunityRepository,
        provider_repository: ProviderRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
    ):
        self.opportunity_repository = opportunity_repository
        self.provider_repository = provider_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository

    def execute(
        self,
        *,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityInvitation:
        if opportunity_id is None or not isinstance(opportunity_id, UUID):
            raise ValueError("Opportunity id is required and must be a UUID instance.")
        if provider_id is None or not isinstance(provider_id, UUID):
            raise ValueError("Provider id is required and must be a UUID instance.")

        opportunity = self.opportunity_repository.get_by_id(opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing = self.opportunity_invitation_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity_id,
            provider_id=provider_id,
        )
        if existing is not None:
            raise ValueError("OpportunityInvitation already exists for this provider.")

        invitation = OpportunityInvitation(
            id=uuid4(),
            opportunity_id=opportunity_id,
            provider_id=provider_id,
            created_at=datetime.now(timezone.utc),
        )
        return self.opportunity_invitation_repository.save(invitation)


class DistributeOpportunity:
    def __init__(
        self,
        opportunity_repository: OpportunityRepository,
        service_request_repository: ServiceRequestRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        rank_candidates: RankCandidates,
        invite_provider_to_opportunity: InviteProviderToOpportunity,
    ):
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.rank_candidates = rank_candidates
        self.invite_provider_to_opportunity = invite_provider_to_opportunity

    def execute(
        self,
        *,
        opportunity_id: UUID,
        max_invitations: int = 3,
    ) -> list[OpportunityInvitation]:
        if opportunity_id is None:
            raise ValueError("Opportunity id is required.")
        if not isinstance(opportunity_id, UUID):
            raise ValueError("Opportunity id must be a valid UUID instance.")

        if isinstance(max_invitations, bool) or not isinstance(max_invitations, int):
            raise ValueError("max_invitations must be an integer.")
        if max_invitations < 1:
            raise ValueError("max_invitations must be at least 1.")

        opportunity = self.opportunity_repository.get_by_id(opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        service_request = self.service_request_repository.get_by_id(opportunity.service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")

        # Rank candidates (this will also validate service request status/existence)
        ranked_results = self.rank_candidates.execute(service_request_id=service_request.id)

        # Get existing invitations
        existing_invitations = self.opportunity_invitation_repository.list_by_opportunity(opportunity.id)
        existing_provider_ids = {inv.provider_id for inv in existing_invitations}

        remaining_capacity = max_invitations - len(existing_invitations)
        if remaining_capacity <= 0:
            return []

        # Filter out providers who already have invitation
        candidates_to_invite = [
            result.provider
            for result in ranked_results
            if result.provider.id not in existing_provider_ids
        ]

        # Take up to remaining_capacity
        selected_providers = candidates_to_invite[:remaining_capacity]

        granted_invitations: list[OpportunityInvitation] = []
        for provider in selected_providers:
            invitation = self.invite_provider_to_opportunity.execute(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
            )
            granted_invitations.append(invitation)

        return granted_invitations


class RegisterOpportunityInterest:
    def __init__(
        self,
        opportunity_repository: OpportunityRepository,
        provider_repository: ProviderRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_interest_repository: OpportunityInterestRepository,
    ):
        self.opportunity_repository = opportunity_repository
        self.provider_repository = provider_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_interest_repository = opportunity_interest_repository

    def execute(
        self,
        *,
        invitation_id: UUID,
    ) -> OpportunityInterest:
        if invitation_id is None or not isinstance(invitation_id, UUID):
            raise ValueError("Invitation id is required and must be a UUID instance.")

        invitation = self.opportunity_invitation_repository.get_by_id(invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing = self.opportunity_interest_repository.get_by_invitation(invitation_id)
        if existing is not None:
            raise ValueError("OpportunityInterest already exists for this invitation.")

        interest = OpportunityInterest(
            id=uuid4(),
            invitation_id=invitation_id,
            created_at=datetime.now(timezone.utc),
        )
        return self.opportunity_interest_repository.save(interest)


class RequestOpportunityAccess:
    def __init__(
        self,
        opportunity_interest_repository: OpportunityInterestRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository,
        provider_repository: ProviderRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        access_entitlement_policy: AccessEntitlementPolicy,
        grant_opportunity_access: GrantOpportunityAccess,
    ):
        self.opportunity_interest_repository = opportunity_interest_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.provider_repository = provider_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.access_entitlement_policy = access_entitlement_policy
        self.grant_opportunity_access = grant_opportunity_access

    def execute(
        self,
        *,
        interest_id: UUID,
    ) -> RequestOpportunityAccessResult:
        if interest_id is None or not isinstance(interest_id, UUID):
            raise ValueError("Interest id is required and must be a UUID instance.")

        interest = self.opportunity_interest_repository.get_by_id(interest_id)
        if interest is None:
            raise ValueError("OpportunityInterest does not exist.")

        invitation = self.opportunity_invitation_repository.get_by_id(interest.invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing_access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity.id,
            provider_id=provider.id,
        )
        if existing_access is not None:
            raise ValueError("OpportunityAccess already exists for this provider and opportunity.")

        decision = self.access_entitlement_policy.decide(
            interest=interest,
            invitation=invitation,
            opportunity=opportunity,
            provider=provider,
        )

        access = None
        if decision.allowed:
            access = self.grant_opportunity_access.execute(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
            )

        return RequestOpportunityAccessResult(decision=decision, access=access)


class SettlementAwareAccessEntitlementPolicy(AccessEntitlementPolicy):
    def __init__(self, economic_settlement_repository: EconomicSettlementRepository):
        self.economic_settlement_repository = economic_settlement_repository

    def decide(
        self,
        *,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> AccessEntitlementDecision:
        settlement = self.economic_settlement_repository.get_by_interest(interest.id)
        if settlement is not None:
            return AccessEntitlementDecision(
                allowed=True,
                reason="economic_settlement_exists",
            )
        return AccessEntitlementDecision(
            allowed=False,
            reason="economic_settlement_required",
        )


class QuoteOpportunityAccessPrice:
    def __init__(
        self,
        opportunity_interest_repository: OpportunityInterestRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository,
        provider_repository: ProviderRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        opportunity_pricing_policy: OpportunityPricingPolicy,
    ):
        self.opportunity_interest_repository = opportunity_interest_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.provider_repository = provider_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.opportunity_pricing_policy = opportunity_pricing_policy

    def execute(
        self,
        *,
        interest_id: UUID,
    ) -> OpportunityPricingQuote:
        if interest_id is None or not isinstance(interest_id, UUID):
            raise ValueError("Interest id is required and must be a UUID instance.")

        interest = self.opportunity_interest_repository.get_by_id(interest_id)
        if interest is None:
            raise ValueError("OpportunityInterest does not exist.")

        invitation = self.opportunity_invitation_repository.get_by_id(interest.invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing_access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity.id,
            provider_id=provider.id,
        )
        if existing_access is not None:
            raise ValueError("OpportunityAccess already exists for this provider and opportunity.")

        return self.opportunity_pricing_policy.quote(
            interest=interest,
            invitation=invitation,
            opportunity=opportunity,
            provider=provider,
        )


class RecordEconomicSettlement:
    def __init__(
        self,
        opportunity_interest_repository: OpportunityInterestRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository,
        provider_repository: ProviderRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        economic_settlement_repository: EconomicSettlementRepository,
    ):
        self.opportunity_interest_repository = opportunity_interest_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.provider_repository = provider_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.economic_settlement_repository = economic_settlement_repository

    def execute(
        self,
        *,
        interest_id: UUID,
        method: SettlementMethod,
        amount: Money,
    ) -> EconomicSettlement:
        if interest_id is None or not isinstance(interest_id, UUID):
            raise ValueError("Interest id is required and must be a UUID instance.")

        if method is None or not isinstance(method, SettlementMethod):
            raise ValueError("Method is required and must be a SettlementMethod instance.")

        if amount is None or not isinstance(amount, Money):
            raise ValueError("Amount is required and must be a Money instance.")

        interest = self.opportunity_interest_repository.get_by_id(interest_id)
        if interest is None:
            raise ValueError("OpportunityInterest does not exist.")

        invitation = self.opportunity_invitation_repository.get_by_id(interest.invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing_access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity.id,
            provider_id=provider.id,
        )
        if existing_access is not None:
            raise ValueError("OpportunityAccess already exists for this provider and opportunity.")

        existing_settlement = self.economic_settlement_repository.get_by_interest(interest_id)
        if existing_settlement is not None:
            raise ValueError("EconomicSettlement already exists for this interest.")

        settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=interest_id,
            method=method,
            amount=amount,
            created_at=datetime.now(timezone.utc),
        )
        return self.economic_settlement_repository.save(settlement)


class CreateCreditWallet:
    def __init__(
        self,
        organization_repository: OrganizationRepository,
        credit_wallet_repository: CreditWalletRepository,
    ):
        self.organization_repository = organization_repository
        self.credit_wallet_repository = credit_wallet_repository

    def execute(
        self,
        *,
        organization_id: UUID,
    ) -> CreditWallet:
        if organization_id is None or not isinstance(organization_id, UUID):
            raise ValueError("Organization id is required and must be a UUID instance.")

        org = self.organization_repository.get_by_id(organization_id)
        if org is None:
            raise ValueError("Organization does not exist.")
        if not org.is_active:
            raise ValueError("Organization is inactive.")

        existing = self.credit_wallet_repository.get_by_organization(organization_id)
        if existing is not None:
            raise ValueError("CreditWallet already exists for this Organization.")

        now = datetime.now(timezone.utc)
        wallet = CreditWallet(
            id=uuid4(),
            organization_id=organization_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        return self.credit_wallet_repository.save(wallet)


class GetCreditWalletBalance:
    def __init__(
        self,
        credit_wallet_repository: CreditWalletRepository,
        credit_ledger_entry_repository: CreditLedgerEntryRepository,
    ):
        self.credit_wallet_repository = credit_wallet_repository
        self.credit_ledger_entry_repository = credit_ledger_entry_repository

    def execute(self, *, wallet_id: UUID) -> int:
        if wallet_id is None or not isinstance(wallet_id, UUID):
            raise ValueError("Wallet id is required and must be a UUID instance.")

        wallet = self.credit_wallet_repository.get_by_id(wallet_id)
        if wallet is None:
            raise ValueError("CreditWallet does not exist.")

        entries = self.credit_ledger_entry_repository.list_by_wallet(wallet_id)
        balance = 0
        for entry in entries:
            if entry.direction is CreditLedgerDirection.CREDIT:
                balance += entry.units
            elif entry.direction is CreditLedgerDirection.DEBIT:
                balance -= entry.units
        return balance


class RecordCredit:
    def __init__(
        self,
        credit_wallet_repository: CreditWalletRepository,
        credit_ledger_entry_repository: CreditLedgerEntryRepository,
    ):
        self.credit_wallet_repository = credit_wallet_repository
        self.credit_ledger_entry_repository = credit_ledger_entry_repository

    def execute(
        self,
        *,
        wallet_id: UUID,
        units: int,
        reason: str,
        reference: str | None = None,
    ) -> CreditLedgerEntry:
        if wallet_id is None or not isinstance(wallet_id, UUID):
            raise ValueError("Wallet id is required and must be a UUID instance.")

        wallet = self.credit_wallet_repository.get_by_id(wallet_id)
        if wallet is None:
            raise ValueError("CreditWallet does not exist.")
        if not wallet.is_active:
            raise ValueError("CreditWallet is inactive.")

        if units is None or isinstance(units, bool) or not isinstance(units, int) or units <= 0:
            raise ValueError("Units must be a positive integer.")

        # Entity __post_init__ will handle trimming and validating string contents for reason/reference
        entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=wallet_id,
            direction=CreditLedgerDirection.CREDIT,
            units=units,
            reason=reason,
            reference=reference,
            created_at=datetime.now(timezone.utc),
        )
        return self.credit_ledger_entry_repository.save(entry)


class RecordDebit:
    def __init__(
        self,
        credit_wallet_repository: CreditWalletRepository,
        credit_ledger_entry_repository: CreditLedgerEntryRepository,
    ):
        self.credit_wallet_repository = credit_wallet_repository
        self.credit_ledger_entry_repository = credit_ledger_entry_repository

    def execute(
        self,
        *,
        wallet_id: UUID,
        units: int,
        reason: str,
        reference: str | None = None,
    ) -> CreditLedgerEntry:
        if wallet_id is None or not isinstance(wallet_id, UUID):
            raise ValueError("Wallet id is required and must be a UUID instance.")

        wallet = self.credit_wallet_repository.get_by_id(wallet_id)
        if wallet is None:
            raise ValueError("CreditWallet does not exist.")
        if not wallet.is_active:
            raise ValueError("CreditWallet is inactive.")

        if units is None or isinstance(units, bool) or not isinstance(units, int) or units <= 0:
            raise ValueError("Units must be a positive integer.")

        # Retrieve entries and compute derived balance
        entries = self.credit_ledger_entry_repository.list_by_wallet(wallet_id)
        balance = 0
        for e in entries:
            if e.direction is CreditLedgerDirection.CREDIT:
                balance += e.units
            elif e.direction is CreditLedgerDirection.DEBIT:
                balance -= e.units

        if units > balance:
            raise ValueError("Insufficient balance to execute debit.")

        entry = CreditLedgerEntry(
            id=uuid4(),
            wallet_id=wallet_id,
            direction=CreditLedgerDirection.DEBIT,
            units=units,
            reason=reason,
            reference=reference,
            created_at=datetime.now(timezone.utc),
        )
        return self.credit_ledger_entry_repository.save(entry)


class SettleOpportunityWithCredits:
    def __init__(
        self,
        *,
        opportunity_interest_repository: OpportunityInterestRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository,
        provider_repository: ProviderRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        economic_settlement_repository: EconomicSettlementRepository,
        credit_wallet_repository: CreditWalletRepository,
        credit_ledger_entry_repository: CreditLedgerEntryRepository,
        opportunity_pricing_policy: OpportunityPricingPolicy,
        credit_cost_policy: CreditCostPolicy,
        atomic_writer: CreditSettlementAtomicWriter,
    ):
        self.opportunity_interest_repository = opportunity_interest_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.provider_repository = provider_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.economic_settlement_repository = economic_settlement_repository
        self.credit_wallet_repository = credit_wallet_repository
        self.credit_ledger_entry_repository = credit_ledger_entry_repository
        self.opportunity_pricing_policy = opportunity_pricing_policy
        self.credit_cost_policy = credit_cost_policy
        self.atomic_writer = atomic_writer

    def execute(self, *, interest_id: UUID) -> CreditSettlementResult:
        if interest_id is None or not isinstance(interest_id, UUID):
            raise ValueError("Interest id is required and must be a UUID instance.")

        interest = self.opportunity_interest_repository.get_by_id(interest_id)
        if interest is None:
            raise ValueError("OpportunityInterest does not exist.")

        invitation = self.opportunity_invitation_repository.get_by_id(interest.invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing_access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity.id,
            provider_id=provider.id,
        )
        if existing_access is not None:
            raise ValueError("OpportunityAccess already exists.")

        existing_settlement = self.economic_settlement_repository.get_by_interest(interest.id)
        if existing_settlement is not None:
            raise ValueError("EconomicSettlement already exists.")

        wallet = self.credit_wallet_repository.get_by_organization(provider.organization_id)
        if wallet is None:
            raise ValueError("Organization wallet does not exist.")
        if not wallet.is_active:
            raise ValueError("Organization wallet is inactive.")

        # Pricing and Conversion Cost policies
        quote = self.opportunity_pricing_policy.quote(
            opportunity=opportunity,
            provider=provider,
            interest=interest,
            invitation=invitation,
        )
        if quote is None or quote.amount is None:
            raise ValueError("OpportunityPricingQuote is invalid.")

        required_units = self.credit_cost_policy.units_required(
            price=quote.amount,
            interest=interest,
            invitation=invitation,
            opportunity=opportunity,
            provider=provider,
        )
        if required_units is None or isinstance(required_units, bool) or not isinstance(required_units, int) or required_units < 0:
            raise ValueError("CreditCostPolicy returned an invalid units value.")

        # Balance check for positive costs
        if required_units > 0:
            entries = self.credit_ledger_entry_repository.list_by_wallet(wallet.id)
            balance = sum(e.units for e in entries if e.direction is CreditLedgerDirection.CREDIT) - \
                      sum(e.units for e in entries if e.direction is CreditLedgerDirection.DEBIT)
            if required_units > balance:
                raise ValueError("Insufficient wallet credit balance.")

        # Prepare facts
        now = datetime.now(timezone.utc)
        debit_entry = None
        if required_units > 0:
            debit_entry = CreditLedgerEntry(
                id=uuid4(),
                wallet_id=wallet.id,
                direction=CreditLedgerDirection.DEBIT,
                units=required_units,
                reason="Opportunity access economic settlement",
                reference=f"opportunity-interest:{interest.id}",
                created_at=now,
            )

        settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=interest.id,
            method=SettlementMethod.CREDIT,
            amount=quote.amount,
            created_at=now,
            pricing_source=quote.pricing_source or quote.reason,
            pricing_configuration_id=quote.pricing_configuration_id,
            pricing_resolved_at=now,
        )

        # Atomic persistence
        self.atomic_writer.persist(
            debit_entry=debit_entry,
            settlement=settlement,
            wallet_id=wallet.id,
            required_units=required_units,
        )

        return CreditSettlementResult(
            pricing_quote=quote,
            credit_units=required_units,
            debit_entry=debit_entry,
            settlement=settlement,
        )


class GetProtectedCommercialData:
    def __init__(
        self,
        opportunity_access_repository: OpportunityAccessRepository,
        opportunity_repository: OpportunityRepository,
        service_request_repository: ServiceRequestRepository,
        provider_repository: ProviderRepository,
    ):
        self.opportunity_access_repository = opportunity_access_repository
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository
        self.provider_repository = provider_repository

    def execute(
        self,
        *,
        provider_id: UUID,
        opportunity_access_id: UUID,
    ) -> ProtectedCommercialData:
        if provider_id is None or not isinstance(provider_id, UUID):
            raise ValueError("provider_id is required and must be a UUID instance.")
        if opportunity_access_id is None or not isinstance(opportunity_access_id, UUID):
            raise ValueError("OpportunityAccess id is required and must be a UUID instance.")

        access = self.opportunity_access_repository.get_by_id(opportunity_access_id)
        if access is None:
            raise ValueError("OpportunityAccess does not exist.")

        if access.provider_id != provider_id:
            raise ValueError("Access entitlement ownership mismatch.")

        opportunity = self.opportunity_repository.get_by_id(access.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")

        service_request = self.service_request_repository.get_by_id(opportunity.service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")

        provider = self.provider_repository.get_by_id(access.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")

        req_name = service_request.requester_name.strip()
        req_email = service_request.requester_email.strip()
        req_phone = service_request.requester_phone.strip()
        if not req_name or (not req_email and not req_phone):
            raise ValueError("No protected contact information available for this legacy request.")

        return ProtectedCommercialData(
            requester_name=req_name,
            requester_email=req_email,
            requester_phone=req_phone,
        )


class GetOpportunityPreview:
    def __init__(
        self,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository,
        service_request_repository: ServiceRequestRepository,
        provider_repository: ProviderRepository,
    ):
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository
        self.provider_repository = provider_repository

    def execute(
        self,
        *,
        opportunity_invitation_id: UUID,
    ) -> OpportunityPreview:
        if opportunity_invitation_id is None or not isinstance(opportunity_invitation_id, UUID):
            raise ValueError("OpportunityInvitation id is required and must be a UUID instance.")

        invitation = self.opportunity_invitation_repository.get_by_id(opportunity_invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        service_request = self.service_request_repository.get_by_id(opportunity.service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")
        if service_request.status is not ServiceRequestStatus.OPEN:
            raise ValueError("ServiceRequest is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        return OpportunityPreview(
            opportunity_id=opportunity.id,
            service_request_id=service_request.id,
            service_id=service_request.service_id,
            title=service_request.title,
            description=service_request.description,
            status=opportunity.status,
            created_at=opportunity.created_at,
        )


class GetOpportunityUnlockQuote:
    def __init__(
        self,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository,
        service_request_repository: ServiceRequestRepository,
        provider_repository: ProviderRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        opportunity_pricing_policy: OpportunityPricingPolicy,
    ):
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository
        self.provider_repository = provider_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.opportunity_pricing_policy = opportunity_pricing_policy

    def execute(
        self,
        *,
        opportunity_invitation_id: UUID,
    ) -> OpportunityUnlockQuote:
        if opportunity_invitation_id is None or not isinstance(opportunity_invitation_id, UUID):
            raise ValueError("OpportunityInvitation id is required and must be a UUID instance.")

        invitation = self.opportunity_invitation_repository.get_by_id(opportunity_invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        service_request = self.service_request_repository.get_by_id(opportunity.service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")
        if service_request.status is not ServiceRequestStatus.OPEN:
            raise ValueError("ServiceRequest is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing_access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity.id,
            provider_id=provider.id,
        )
        if existing_access is not None:
            return OpportunityUnlockQuote(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                amount=None,
                quote_available=False,
                already_unlocked=True,
                reason="Opportunity already unlocked for this provider.",
            )

        try:
            pricing_quote = self.opportunity_pricing_policy.quote(
                invitation=invitation,
                opportunity=opportunity,
                provider=provider,
            )
            return OpportunityUnlockQuote(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                amount=pricing_quote.amount,
                quote_available=True,
                already_unlocked=False,
                reason=pricing_quote.reason,
            )
        except OpportunityPricingUnavailable:
            return OpportunityUnlockQuote(
                opportunity_id=opportunity.id,
                provider_id=provider.id,
                amount=None,
                quote_available=False,
                already_unlocked=False,
                reason="No commercial pricing configured for pre-access unlock.",
            )


class UnlockOpportunityWithCredits:
    def __init__(
        self,
        *,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository,
        service_request_repository: ServiceRequestRepository,
        provider_repository: ProviderRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        opportunity_interest_repository: OpportunityInterestRepository,
        economic_settlement_repository: EconomicSettlementRepository,
        credit_wallet_repository: CreditWalletRepository,
        credit_ledger_entry_repository: CreditLedgerEntryRepository,
        opportunity_pricing_policy: OpportunityPricingPolicy,
        credit_cost_policy: CreditCostPolicy,
        unlock_atomic_writer: OpportunityUnlockAtomicWriter,
    ):
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository
        self.provider_repository = provider_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.opportunity_interest_repository = opportunity_interest_repository
        self.economic_settlement_repository = economic_settlement_repository
        self.credit_wallet_repository = credit_wallet_repository
        self.credit_ledger_entry_repository = credit_ledger_entry_repository
        self.opportunity_pricing_policy = opportunity_pricing_policy
        self.credit_cost_policy = credit_cost_policy
        self.unlock_atomic_writer = unlock_atomic_writer

    def execute(
        self,
        *,
        opportunity_invitation_id: UUID,
    ) -> OpportunityUnlockResult:
        if opportunity_invitation_id is None or not isinstance(opportunity_invitation_id, UUID):
            raise ValueError("OpportunityInvitation id is required and must be a UUID instance.")

        invitation = self.opportunity_invitation_repository.get_by_id(opportunity_invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")

        opportunity = self.opportunity_repository.get_by_id(invitation.opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")
        if opportunity.status is not OpportunityStatus.OPEN:
            raise ValueError("Opportunity is not OPEN.")

        service_request = self.service_request_repository.get_by_id(opportunity.service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")
        if service_request.status is not ServiceRequestStatus.OPEN:
            raise ValueError("ServiceRequest is not OPEN.")

        provider = self.provider_repository.get_by_id(invitation.provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")
        if not provider.is_active:
            raise ValueError("Provider is inactive.")

        existing_access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity.id,
            provider_id=provider.id,
        )
        if existing_access is not None:
            interest = self.opportunity_interest_repository.get_by_invitation(invitation.id)
            settlement_id = None
            if interest is not None:
                settlement = self.economic_settlement_repository.get_by_interest(interest.id)
                if settlement is not None:
                    settlement_id = settlement.id
            return OpportunityUnlockResult(
                access=existing_access,
                already_unlocked=True,
                settlement_id=settlement_id,
                amount=None,
            )

        quote = self.opportunity_pricing_policy.quote(
            invitation=invitation,
            opportunity=opportunity,
            provider=provider,
        )
        if quote is None or quote.amount is None:
            raise ValueError("OpportunityPricingQuote is invalid.")

        interest = self.opportunity_interest_repository.get_by_invitation(invitation.id)
        if interest is None:
            interest = OpportunityInterest(
                id=uuid4(),
                invitation_id=invitation.id,
                created_at=datetime.now(timezone.utc),
            )

        required_units = self.credit_cost_policy.units_required(
            price=quote.amount,
            interest=interest,
            invitation=invitation,
            opportunity=opportunity,
            provider=provider,
        )
        if required_units is None or isinstance(required_units, bool) or not isinstance(required_units, int) or required_units < 0:
            raise ValueError("CreditCostPolicy returned an invalid units value.")

        wallet = self.credit_wallet_repository.get_by_organization(provider.organization_id)
        if wallet is None:
            raise ValueError("Organization wallet does not exist.")
        if not wallet.is_active:
            raise ValueError("Organization wallet is inactive.")

        if required_units > 0:
            entries = self.credit_ledger_entry_repository.list_by_wallet(wallet.id)
            balance = sum(e.units for e in entries if e.direction is CreditLedgerDirection.CREDIT) - \
                      sum(e.units for e in entries if e.direction is CreditLedgerDirection.DEBIT)
            if required_units > balance:
                raise ValueError("Insufficient wallet credit balance.")

        now = datetime.now(timezone.utc)
        debit_entry = None
        if required_units > 0:
            debit_entry = CreditLedgerEntry(
                id=uuid4(),
                wallet_id=wallet.id,
                direction=CreditLedgerDirection.DEBIT,
                units=required_units,
                reason="Opportunity access economic settlement",
                reference=f"opportunity-interest:{interest.id}",
                created_at=now,
            )

        settlement = EconomicSettlement(
            id=uuid4(),
            interest_id=interest.id,
            method=SettlementMethod.CREDIT,
            amount=quote.amount,
            created_at=now,
            pricing_source=quote.pricing_source or quote.reason,
            pricing_configuration_id=quote.pricing_configuration_id,
            pricing_resolved_at=now,
        )

        access = OpportunityAccess(
            id=uuid4(),
            opportunity_id=opportunity.id,
            provider_id=provider.id,
            created_at=now,
        )

        self.unlock_atomic_writer.persist_unlock(
            interest=interest,
            debit_entry=debit_entry,
            settlement=settlement,
            access=access,
            wallet_id=wallet.id,
            required_units=required_units,
        )

        return OpportunityUnlockResult(
            access=access,
            already_unlocked=False,
            settlement_id=settlement.id,
            amount=quote.amount,
        )


class ReconcileOpportunityEconomicAcquisition:
    def __init__(
        self,
        *,
        opportunity_repository: OpportunityRepository,
        provider_repository: ProviderRepository,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_interest_repository: OpportunityInterestRepository,
        opportunity_access_repository: OpportunityAccessRepository,
        economic_settlement_repository: EconomicSettlementRepository,
        credit_wallet_repository: CreditWalletRepository,
        credit_ledger_entry_repository: CreditLedgerEntryRepository,
    ):
        self.opportunity_repository = opportunity_repository
        self.provider_repository = provider_repository
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_interest_repository = opportunity_interest_repository
        self.opportunity_access_repository = opportunity_access_repository
        self.economic_settlement_repository = economic_settlement_repository
        self.credit_wallet_repository = credit_wallet_repository
        self.credit_ledger_entry_repository = credit_ledger_entry_repository

    def execute(
        self,
        *,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> EconomicAcquisitionReconciliation:
        if opportunity_id is None or not isinstance(opportunity_id, UUID):
            raise ValueError("Opportunity id is required and must be a UUID instance.")
        if provider_id is None or not isinstance(provider_id, UUID):
            raise ValueError("Provider id is required and must be a UUID instance.")

        opportunity = self.opportunity_repository.get_by_id(opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")

        issues: list[EconomicAcquisitionReconciliationIssue] = []
        access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity_id,
            provider_id=provider_id,
        )
        invitation = self.opportunity_invitation_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity_id,
            provider_id=provider_id,
        )
        interest = None
        settlement = None
        debits: list[CreditLedgerEntry] = []
        wallet = self.credit_wallet_repository.get_by_organization(provider.organization_id)

        if invitation is not None:
            if invitation.opportunity_id != opportunity_id:
                issues.append(EconomicAcquisitionReconciliationIssue.OPPORTUNITY_MISMATCH)
            if invitation.provider_id != provider_id:
                issues.append(EconomicAcquisitionReconciliationIssue.PROVIDER_MISMATCH)
            interest = self.opportunity_interest_repository.get_by_invitation(invitation.id)

        if interest is not None:
            settlement = self.economic_settlement_repository.get_by_interest(interest.id)
            reference = f"opportunity-interest:{interest.id}"
            debits = self.credit_ledger_entry_repository.list_debits_by_reference(reference)
            if wallet is not None:
                for debit in debits:
                    if debit.wallet_id != wallet.id:
                        issues.append(EconomicAcquisitionReconciliationIssue.ORGANIZATION_MISMATCH)

        if access is not None and settlement is None:
            issues.append(EconomicAcquisitionReconciliationIssue.ACCESS_WITHOUT_SETTLEMENT)

        if settlement is not None and settlement.method is SettlementMethod.CREDIT and settlement.amount.amount_minor > 0 and not debits:
            issues.append(EconomicAcquisitionReconciliationIssue.SETTLEMENT_WITHOUT_DEBIT)

        if debits and settlement is None:
            issues.append(EconomicAcquisitionReconciliationIssue.DEBIT_WITHOUT_SETTLEMENT)

        if len(debits) > 1:
            issues.append(EconomicAcquisitionReconciliationIssue.DUPLICATE_ECONOMIC_ACQUISITION)

        deduped_issues = tuple(dict.fromkeys(issues))
        return EconomicAcquisitionReconciliation(
            opportunity_id=opportunity_id,
            provider_id=provider_id,
            consistent=not deduped_issues,
            issues=deduped_issues,
            access_id=access.id if access is not None else None,
            interest_id=interest.id if interest is not None else None,
            settlement_id=settlement.id if settlement is not None else None,
            debit_entry_ids=tuple(debit.id for debit in debits),
        )


class GetUnlockedOpportunityContact:
    def __init__(
        self,
        *,
        opportunity_access_repository: OpportunityAccessRepository,
        opportunity_repository: OpportunityRepository,
        service_request_repository: ServiceRequestRepository,
        provider_repository: ProviderRepository,
        audit_writer: ProtectedDataReadAuditWriter,
    ):
        self.opportunity_access_repository = opportunity_access_repository
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository
        self.provider_repository = provider_repository
        self.audit_writer = audit_writer

    def execute(
        self,
        *,
        authenticated_user_id: UUID,
        provider_id: UUID,
        opportunity_id: UUID,
    ) -> UnlockedOpportunityContact:
        if authenticated_user_id is None or not isinstance(authenticated_user_id, UUID):
            raise ValueError("authenticated_user_id is required and must be a UUID instance.")
        if provider_id is None or not isinstance(provider_id, UUID):
            raise ValueError("provider_id is required and must be a UUID instance.")
        if opportunity_id is None or not isinstance(opportunity_id, UUID):
            raise ValueError("opportunity_id is required and must be a UUID instance.")

        # Resolve access entitlement
        access = self.opportunity_access_repository.get_by_opportunity_and_provider(
            opportunity_id=opportunity_id,
            provider_id=provider_id,
        )
        if access is None:
            raise ValueError("Access entitlement missing for this provider and opportunity.")

        opportunity = self.opportunity_repository.get_by_id(opportunity_id)
        if opportunity is None:
            raise ValueError("Opportunity does not exist.")

        service_request = self.service_request_repository.get_by_id(opportunity.service_request_id)
        if service_request is None:
            raise ValueError("ServiceRequest does not exist.")

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")

        # Persist success audit event first (exceptions propagate to block return of contact)
        self.audit_writer.record_contact_read(
            authenticated_user_id=authenticated_user_id,
            provider_id=provider_id,
            opportunity_id=opportunity_id,
            service_request_id=service_request.id,
        )

        # Allowlist projection
        return UnlockedOpportunityContact(
            opportunity_id=opportunity.id,
            service_request_id=service_request.id,
            requester_name=service_request.requester_name,
            requester_email=service_request.requester_email,
            requester_phone=service_request.requester_phone,
        )


class ListProviderOpportunityInbox:
    def __init__(
        self,
        *,
        opportunity_invitation_repository: OpportunityInvitationRepository,
        opportunity_repository: OpportunityRepository | None = None,
        service_request_repository: ServiceRequestRepository | None = None,
        provider_repository: ProviderRepository,
    ):
        self.opportunity_invitation_repository = opportunity_invitation_repository
        self.opportunity_repository = opportunity_repository
        self.service_request_repository = service_request_repository
        self.provider_repository = provider_repository

    def execute(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: OpportunityStatus | None = None,
    ) -> ProviderOpportunityInboxPage:
        import math

        if provider_id is None or not isinstance(provider_id, UUID):
            raise ValueError("provider_id is required and must be a UUID instance.")
        if page is None or isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be an integer >= 1.")
        if page_size is None or isinstance(page_size, bool) or not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            raise ValueError("page_size must be an integer between 1 and 100.")
        if status is not None and not isinstance(status, OpportunityStatus):
            raise ValueError("status must be an OpportunityStatus instance or None.")

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")

        items, total_items = self.opportunity_invitation_repository.list_inbox_items_by_provider_paginated(
            provider_id=provider_id,
            page=page,
            page_size=page_size,
            status=status,
        )

        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0

        return ProviderOpportunityInboxPage(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )


class ListProviderUnlockedOpportunities:
    def __init__(
        self,
        *,
        opportunity_access_repository: OpportunityAccessRepository,
        provider_repository: ProviderRepository,
    ):
        self.opportunity_access_repository = opportunity_access_repository
        self.provider_repository = provider_repository

    def execute(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> ProviderUnlockedOpportunityPage:
        import math

        if provider_id is None or not isinstance(provider_id, UUID):
            raise ValueError("provider_id is required and must be a UUID instance.")
        if page is None or isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be an integer >= 1.")
        if page_size is None or isinstance(page_size, bool) or not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            raise ValueError("page_size must be an integer between 1 and 100.")

        provider = self.provider_repository.get_by_id(provider_id)
        if provider is None:
            raise ValueError("Provider does not exist.")

        items, total_items = self.opportunity_access_repository.list_unlocked_items_by_provider_paginated(
            provider_id=provider_id,
            page=page,
            page_size=page_size,
        )

        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1

        return ProviderUnlockedOpportunityPage(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )


class AuthenticatedProviderMarketplaceService:
    """
    Application-layer façade that establishes the authenticated provider
    identity boundary for marketplace operations.

    Responsibility:
        - Resolve authenticated_user_id → trusted Provider via ProviderIdentityResolver.
        - Verify that the resolved Provider owns the invitation/access being used.
        - Delegate to existing use cases with a trusted provider_id.

    What this façade does NOT do:
        - Accept provider_id from external callers.
        - Perform pricing, settlement, or access creation.
        - Know anything about HTTP, Django, or auth frameworks.

    Security contract:
        - All public methods (inbox, preview, quote, unlock, get_contact) are
          secure by default — provider resolution and invitation ownership are enforced.
        - No alternate "unsafe" public path exists.
        - provider_id is NEVER accepted as a caller-supplied parameter.
    """

    def __init__(
        self,
        *,
        provider_identity_resolver: ProviderIdentityResolver,
        invitation_repository: OpportunityInvitationRepository,
        get_opportunity_preview: "GetOpportunityPreview",
        get_opportunity_unlock_quote: "GetOpportunityUnlockQuote",
        unlock_opportunity_with_credits: "UnlockOpportunityWithCredits",
        get_unlocked_opportunity_contact: "GetUnlockedOpportunityContact",
        list_provider_opportunity_inbox: ListProviderOpportunityInbox | None = None,
        list_provider_unlocked_opportunities: ListProviderUnlockedOpportunities | None = None,
    ):
        self._resolver = provider_identity_resolver
        self._invitation_repository = invitation_repository
        self._get_preview = get_opportunity_preview
        self._get_quote = get_opportunity_unlock_quote
        self._unlock = unlock_opportunity_with_credits
        self._get_contact = get_unlocked_opportunity_contact
        self._list_inbox = list_provider_opportunity_inbox
        self._list_unlocked = list_provider_unlocked_opportunities

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_provider(self, authenticated_user_id: UUID) -> Provider:
        """
        Resolve and return the trusted Provider for this caller.

        Propagates ProviderIdentityNotFound and AmbiguousProviderIdentity
        as-is.  Unexpected RuntimeError from the resolver also propagates.
        """
        if authenticated_user_id is None or not isinstance(authenticated_user_id, UUID):
            raise ValueError(
                "authenticated_user_id is required and must be a UUID instance."
            )
        return self._resolver.resolve(authenticated_user_id=authenticated_user_id)

    def _load_invitation_and_assert_ownership(
        self,
        *,
        invitation_id: UUID,
        caller_provider_id: UUID,
    ) -> OpportunityInvitation:
        """
        Load the invitation and assert that the caller owns it.

        Raises:
            ValueError: if invitation_id is invalid, invitation does not exist,
                        or the caller's provider does not own the invitation.
        """
        if invitation_id is None or not isinstance(invitation_id, UUID):
            raise ValueError(
                "opportunity_invitation_id is required and must be a UUID instance."
            )
        invitation = self._invitation_repository.get_by_id(invitation_id)
        if invitation is None:
            raise ValueError("OpportunityInvitation does not exist.")
        if invitation.provider_id != caller_provider_id:
            raise ValueError(
                "Invitation does not belong to the authenticated provider."
            )
        return invitation

    # ------------------------------------------------------------------
    # Public canonical surface — all methods secure by default
    # ------------------------------------------------------------------

    def inbox(
        self,
        *,
        authenticated_user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: OpportunityStatus | None = None,
    ) -> "ProviderOpportunityInboxPage":
        """
        List paginated opportunity invitations for the authenticated provider's inbox,
        optionally filtered by opportunity status.

        Security path:
            authenticated_user_id
            → resolve Provider
            → provider.id
            → ListProviderOpportunityInbox (provider-scoped)
        """
        if self._list_inbox is None:
            raise ValueError("ListProviderOpportunityInbox is not configured.")
        provider = self._resolve_provider(authenticated_user_id)
        return self._list_inbox.execute(
            provider_id=provider.id,
            page=page,
            page_size=page_size,
            status=status,
        )

    def unlocked_opportunities(
        self,
        *,
        authenticated_user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> ProviderUnlockedOpportunityPage:
        """
        List paginated historical unlocked opportunities (entitlements)
        for the authenticated provider.

        Security path:
            authenticated_user_id
            → resolve Provider
            → provider.id
            → ListProviderUnlockedOpportunities (provider-scoped)
        """
        if self._list_unlocked is None:
            raise ValueError("ListProviderUnlockedOpportunities is not configured.")
        provider = self._resolve_provider(authenticated_user_id)
        return self._list_unlocked.execute(
            provider_id=provider.id,
            page=page,
            page_size=page_size,
        )

    def preview(
        self,
        *,
        authenticated_user_id: UUID,
        opportunity_invitation_id: UUID,
    ) -> "OpportunityPreview":
        """
        Return a sanitized preview of an opportunity.

        Security path:
            authenticated_user_id
            → resolve Provider
            → load Invitation
            → invitation.provider_id == provider.id  (ownership check)
            → preview use case

        No OpportunityAccess is created.  Provider.is_active is not required.
        """
        provider = self._resolve_provider(authenticated_user_id)
        self._load_invitation_and_assert_ownership(
            invitation_id=opportunity_invitation_id,
            caller_provider_id=provider.id,
        )
        return self._get_preview.execute(
            opportunity_invitation_id=opportunity_invitation_id
        )

    def quote(
        self,
        *,
        authenticated_user_id: UUID,
        opportunity_invitation_id: UUID,
    ) -> "OpportunityUnlockQuote":
        """
        Return an unlock pricing quote for an opportunity.

        Security path:
            authenticated_user_id
            → resolve Provider
            → load Invitation
            → invitation.provider_id == provider.id  (ownership check)
            → quote use case

        Provider.is_active is not required for quote.
        """
        provider = self._resolve_provider(authenticated_user_id)
        self._load_invitation_and_assert_ownership(
            invitation_id=opportunity_invitation_id,
            caller_provider_id=provider.id,
        )
        return self._get_quote.execute(
            opportunity_invitation_id=opportunity_invitation_id
        )

    def unlock(
        self,
        *,
        authenticated_user_id: UUID,
        opportunity_invitation_id: UUID,
    ) -> "OpportunityUnlockResult":
        """
        Atomically unlock an opportunity (debit + settlement + access creation).

        Security path:
            authenticated_user_id
            → resolve Provider
            → load Invitation
            → invitation.provider_id == provider.id  (ownership check)
            → provider.is_active required  (operational eligibility)
            → unlock use case

        An inactive Provider cannot perform new unlocks.
        Pre-existing OpportunityAccess is NOT required before calling unlock;
        idempotency is enforced by the underlying use case.
        """
        provider = self._resolve_provider(authenticated_user_id)
        self._load_invitation_and_assert_ownership(
            invitation_id=opportunity_invitation_id,
            caller_provider_id=provider.id,
        )
        if not provider.is_active:
            raise ValueError(
                f"Provider {provider.id} is inactive and cannot perform new unlocks."
            )
        return self._unlock.execute(
            opportunity_invitation_id=opportunity_invitation_id
        )

    def get_contact(
        self,
        *,
        authenticated_user_id: UUID,
        opportunity_id: UUID,
    ) -> "UnlockedOpportunityContact":
        """
        Retrieve protected contact data for an opportunity.

        Security path:
            authenticated_user_id
            → resolve Provider
            → provider.id
            → GetUnlockedOpportunityContact (requires existing OpportunityAccess)

        Historical contact retrieval is allowed even if Provider is inactive —
        the entitlement was acquired before the Provider became inactive.

        The provider_id used in the underlying use case comes exclusively
        from the trusted identity resolver — not from the caller payload.
        """
        if opportunity_id is None or not isinstance(opportunity_id, UUID):
            raise ValueError(
                "opportunity_id is required and must be a UUID instance."
            )

        provider = self._resolve_provider(authenticated_user_id)

        return self._get_contact.execute(
            authenticated_user_id=authenticated_user_id,
            provider_id=provider.id,
            opportunity_id=opportunity_id,
        )
