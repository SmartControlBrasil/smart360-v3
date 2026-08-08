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
    ServiceRequest,
    ServiceRequestStatus,
    AccessEntitlementDecision,
    RequestOpportunityAccessResult,
    OpportunityPricingQuote,
    Money,
    SettlementMethod,
    EconomicSettlement,
    CreditWallet,
)
from src.organizations.application.ports import OrganizationRepository


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

        now = datetime.now(timezone.utc)
        service_request = ServiceRequest(
            id=uuid4(),
            organization_id=organization_id,
            service_id=service_id,
            title=normalized_title,
            description=normalized_description,
            status=ServiceRequestStatus.OPEN,
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
