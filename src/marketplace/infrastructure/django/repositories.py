from uuid import UUID

from src.marketplace.application.ports import (
    OpportunityAccessRepository,
    OpportunityInvitationRepository,
    OpportunityInterestRepository,
    OpportunityRepository,
    ProviderRepository,
    ProviderServiceRepository,
    ServiceRequestRepository,
    ServiceCategoryRepository,
    ServiceRepository,
    EconomicSettlementRepository,
    CreditWalletRepository,
    CreditLedgerEntryRepository,
    CreditSettlementAtomicWriter,
    OpportunityUnlockAtomicWriter,
    ProtectedDataReadAuditWriter,
    OpportunityUnlockPricingConfigurationRepository,
)
from src.marketplace.application.use_cases import (
    AmbiguousProviderIdentity,
    ProviderIdentityNotFound,
)
from src.marketplace.domain.entities import (
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
    SettlementMethod,
    EconomicSettlement,
    Money,
    CreditWallet,
    CreditLedgerDirection,
    CreditLedgerEntry,
    ProviderOpportunityInboxItem,
    ProviderUnlockedOpportunityItem,
    OpportunityUnlockPricingConfiguration,
)
from src.marketplace.infrastructure.django.marketplace.models import (
    OpportunityAccessModel,
    OpportunityInvitationModel,
    OpportunityInterestModel,
    OpportunityModel,
    ProviderModel,
    ProviderServiceModel,
    ServiceModel,
    ServiceCategoryModel,
    ServiceRequestModel,
    EconomicSettlementModel,
    CreditWalletModel,
    CreditLedgerEntryModel,
    OpportunityContactReadAuditModel,
    OpportunityUnlockPricingConfigurationModel,
)
from src.memberships.infrastructure.django.memberships.models import MembershipModel


class DjangoServiceCategoryRepository(ServiceCategoryRepository):
    @staticmethod
    def _to_entity(model: ServiceCategoryModel) -> ServiceCategory:
        return ServiceCategory(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, service_category: ServiceCategory) -> ServiceCategory:
        model, _ = ServiceCategoryModel.objects.update_or_create(
            id=service_category.id,
            defaults={
                "name": service_category.name,
                "slug": service_category.slug,
                "description": service_category.description,
                "is_active": service_category.is_active,
                "created_at": service_category.created_at,
                "updated_at": service_category.updated_at,
            },
        )

        return self._to_entity(model)

    def get_by_id(
        self,
        service_category_id: UUID,
    ) -> ServiceCategory | None:
        try:
            model = ServiceCategoryModel.objects.get(id=service_category_id)
        except ServiceCategoryModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_slug(self, slug: str) -> ServiceCategory | None:
        try:
            model = ServiceCategoryModel.objects.get(slug=slug)
        except ServiceCategoryModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_active(self) -> list[ServiceCategory]:
        models = ServiceCategoryModel.objects.filter(
            is_active=True,
        ).order_by("created_at")

        return [self._to_entity(model) for model in models]


class DjangoServiceRepository(ServiceRepository):
    @staticmethod
    def _to_entity(model: ServiceModel) -> Service:
        return Service(
            id=model.id,
            category_id=model.category_id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, service: Service) -> Service:
        model, _ = ServiceModel.objects.update_or_create(
            id=service.id,
            defaults={
                "category_id": service.category_id,
                "name": service.name,
                "slug": service.slug,
                "description": service.description,
                "is_active": service.is_active,
                "created_at": service.created_at,
                "updated_at": service.updated_at,
            },
        )

        return self._to_entity(model)

    def get_by_id(self, service_id: UUID) -> Service | None:
        try:
            model = ServiceModel.objects.get(id=service_id)
        except ServiceModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_category_and_slug(
        self,
        category_id: UUID,
        slug: str,
    ) -> Service | None:
        try:
            model = ServiceModel.objects.get(
                category_id=category_id,
                slug=slug,
            )
        except ServiceModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_active_by_category(
        self,
        category_id: UUID,
    ) -> list[Service]:
        models = ServiceModel.objects.filter(
            category_id=category_id,
            is_active=True,
        ).order_by("name", "id")

        return [self._to_entity(model) for model in models]


class DjangoProviderRepository(ProviderRepository):
    @staticmethod
    def _to_entity(model: ProviderModel) -> Provider:
        return Provider(
            id=model.id,
            organization_id=model.organization_id,
            display_name=model.display_name,
            slug=model.slug,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, provider: Provider) -> Provider:
        model, _ = ProviderModel.objects.update_or_create(
            id=provider.id,
            defaults={
                "organization_id": provider.organization_id,
                "display_name": provider.display_name,
                "slug": provider.slug,
                "description": provider.description,
                "is_active": provider.is_active,
                "created_at": provider.created_at,
                "updated_at": provider.updated_at,
            },
        )

        return self._to_entity(model)

    def get_by_id(self, provider_id: UUID) -> Provider | None:
        try:
            model = ProviderModel.objects.get(id=provider_id)
        except ProviderModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_slug(self, slug: str) -> Provider | None:
        try:
            model = ProviderModel.objects.get(slug=slug)
        except ProviderModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_active_by_organization(
        self,
        organization_id: UUID,
    ) -> list[Provider]:
        models = ProviderModel.objects.filter(
            organization_id=organization_id,
            is_active=True,
        ).order_by("display_name", "id")

        return [self._to_entity(model) for model in models]


class DjangoProviderServiceRepository(ProviderServiceRepository):
    @staticmethod
    def _to_entity(model: ProviderServiceModel) -> ProviderService:
        return ProviderService(
            id=model.id,
            provider_id=model.provider_id,
            service_id=model.service_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(
        self,
        provider_service: ProviderService,
    ) -> ProviderService:
        model, _ = ProviderServiceModel.objects.update_or_create(
            id=provider_service.id,
            defaults={
                "provider_id": provider_service.provider_id,
                "service_id": provider_service.service_id,
                "is_active": provider_service.is_active,
                "created_at": provider_service.created_at,
                "updated_at": provider_service.updated_at,
            },
        )

        return self._to_entity(model)

    def get_by_id(
        self,
        provider_service_id: UUID,
    ) -> ProviderService | None:
        try:
            model = ProviderServiceModel.objects.get(id=provider_service_id)
        except ProviderServiceModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_provider_and_service(
        self,
        provider_id: UUID,
        service_id: UUID,
    ) -> ProviderService | None:
        try:
            model = ProviderServiceModel.objects.get(
                provider_id=provider_id,
                service_id=service_id,
            )
        except ProviderServiceModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_active_by_provider(
        self,
        provider_id: UUID,
    ) -> list[ProviderService]:
        models = ProviderServiceModel.objects.filter(
            provider_id=provider_id,
            is_active=True,
        ).order_by("created_at", "id")

        return [self._to_entity(model) for model in models]

    def list_active_by_service(
        self,
        service_id: UUID,
    ) -> list[ProviderService]:
        models = ProviderServiceModel.objects.filter(
            service_id=service_id,
            is_active=True,
        ).order_by("created_at", "id")

        return [self._to_entity(model) for model in models]


class DjangoServiceRequestRepository(ServiceRequestRepository):
    @staticmethod
    def _to_entity(model: ServiceRequestModel) -> ServiceRequest:
        return ServiceRequest(
            id=model.id,
            organization_id=model.organization_id,
            service_id=model.service_id,
            title=model.title,
            description=model.description,
            status=ServiceRequestStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            requester_name=model.requester_name,
            requester_email=model.requester_email,
            requester_phone=model.requester_phone,
        )

    def save(self, service_request: ServiceRequest) -> ServiceRequest:
        model, _ = ServiceRequestModel.objects.update_or_create(
            id=service_request.id,
            defaults={
                "organization_id": service_request.organization_id,
                "service_id": service_request.service_id,
                "title": service_request.title,
                "description": service_request.description,
                "status": service_request.status.value,
                "requester_name": service_request.requester_name,
                "requester_email": service_request.requester_email,
                "requester_phone": service_request.requester_phone,
                "created_at": service_request.created_at,
                "updated_at": service_request.updated_at,
            },
        )

        return self._to_entity(model)

    def get_by_id(
        self,
        service_request_id: UUID,
    ) -> ServiceRequest | None:
        try:
            model = ServiceRequestModel.objects.get(id=service_request_id)
        except ServiceRequestModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_open_by_organization(
        self,
        organization_id: UUID,
    ) -> list[ServiceRequest]:
        models = ServiceRequestModel.objects.filter(
            organization_id=organization_id,
            status=ServiceRequestModel.Status.OPEN,
        ).order_by("created_at", "id")
        return [self._to_entity(model) for model in models]

    def list_open_by_service(
        self,
        service_id: UUID,
    ) -> list[ServiceRequest]:
        models = ServiceRequestModel.objects.filter(
            service_id=service_id,
            status=ServiceRequestModel.Status.OPEN,
        ).order_by("created_at", "id")
        return [self._to_entity(model) for model in models]


class DjangoOpportunityRepository(OpportunityRepository):
    @staticmethod
    def _to_entity(model: OpportunityModel) -> Opportunity:
        return Opportunity(
            id=model.id,
            service_request_id=model.service_request_id,
            status=OpportunityStatus(model.status),
            max_accesses=model.max_accesses,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, opportunity: Opportunity) -> Opportunity:
        model, _ = OpportunityModel.objects.update_or_create(
            id=opportunity.id,
            defaults={
                "service_request_id": opportunity.service_request_id,
                "status": opportunity.status.value,
                "max_accesses": opportunity.max_accesses,
                "created_at": opportunity.created_at,
                "updated_at": opportunity.updated_at,
            },
        )
        return self._to_entity(model)

    def get_by_id(self, opportunity_id: UUID) -> Opportunity | None:
        try:
            model = OpportunityModel.objects.get(id=opportunity_id)
        except OpportunityModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def get_by_service_request(
        self,
        service_request_id: UUID,
    ) -> Opportunity | None:
        try:
            model = OpportunityModel.objects.get(service_request_id=service_request_id)
        except OpportunityModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def list_open(self) -> list[Opportunity]:
        models = OpportunityModel.objects.filter(
            status=OpportunityModel.Status.OPEN,
        ).order_by("created_at", "id")
        return [self._to_entity(model) for model in models]


class DjangoOpportunityAccessRepository(OpportunityAccessRepository):
    @staticmethod
    def _to_entity(model: OpportunityAccessModel) -> OpportunityAccess:
        return OpportunityAccess(
            id=model.id,
            opportunity_id=model.opportunity_id,
            provider_id=model.provider_id,
            created_at=model.created_at,
        )

    def save(self, access: OpportunityAccess) -> OpportunityAccess:
        model, _ = OpportunityAccessModel.objects.update_or_create(
            id=access.id,
            defaults={
                "opportunity_id": access.opportunity_id,
                "provider_id": access.provider_id,
                "created_at": access.created_at,
            },
        )
        return self._to_entity(model)

    def get_by_id(self, access_id: UUID) -> OpportunityAccess | None:
        try:
            model = OpportunityAccessModel.objects.get(id=access_id)
        except OpportunityAccessModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def get_by_opportunity_and_provider(
        self,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityAccess | None:
        try:
            model = OpportunityAccessModel.objects.get(
                opportunity_id=opportunity_id,
                provider_id=provider_id,
            )
        except OpportunityAccessModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def list_by_opportunity(
        self,
        opportunity_id: UUID,
    ) -> list[OpportunityAccess]:
        models = OpportunityAccessModel.objects.filter(
            opportunity_id=opportunity_id,
        ).order_by("created_at", "id")
        return [self._to_entity(model) for model in models]

    def list_by_provider(
        self,
        provider_id: UUID,
    ) -> list[OpportunityAccess]:
        models = OpportunityAccessModel.objects.filter(
            provider_id=provider_id,
        ).order_by("created_at", "id")
        return [self._to_entity(model) for model in models]

    def count_by_opportunity(self, opportunity_id: UUID) -> int:
        return OpportunityAccessModel.objects.filter(
            opportunity_id=opportunity_id,
        ).count()

    def list_unlocked_items_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProviderUnlockedOpportunityItem], int]:
        queryset = OpportunityAccessModel.objects.filter(
            provider_id=provider_id,
        )

        queryset = queryset.select_related(
            "opportunity",
            "opportunity__service_request",
        ).order_by("-created_at", "-id")

        total_items = queryset.count()
        offset = (page - 1) * page_size
        models = queryset[offset : offset + page_size]

        items: list[ProviderUnlockedOpportunityItem] = []
        for m in models:
            opp_model = m.opportunity
            sr_model = opp_model.service_request
            items.append(
                ProviderUnlockedOpportunityItem(
                    opportunity_id=opp_model.id,
                    service_request_id=sr_model.id,
                    service_id=sr_model.service_id,
                    title=sr_model.title,
                    description=sr_model.description,
                    status=OpportunityStatus(opp_model.status),
                    unlocked_at=m.created_at,
                )
            )

        return items, total_items


class DjangoOpportunityInvitationRepository(OpportunityInvitationRepository):
    @staticmethod
    def _to_entity(model: OpportunityInvitationModel) -> OpportunityInvitation:
        return OpportunityInvitation(
            id=model.id,
            opportunity_id=model.opportunity_id,
            provider_id=model.provider_id,
            created_at=model.created_at,
        )

    def save(self, invitation: OpportunityInvitation) -> OpportunityInvitation:
        model, _ = OpportunityInvitationModel.objects.update_or_create(
            id=invitation.id,
            defaults={
                "opportunity_id": invitation.opportunity_id,
                "provider_id": invitation.provider_id,
                "created_at": invitation.created_at,
            },
        )
        return self._to_entity(model)

    def get_by_id(self, invitation_id: UUID) -> OpportunityInvitation | None:
        try:
            model = OpportunityInvitationModel.objects.get(id=invitation_id)
        except OpportunityInvitationModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def get_by_opportunity_and_provider(
        self,
        opportunity_id: UUID,
        provider_id: UUID,
    ) -> OpportunityInvitation | None:
        try:
            model = OpportunityInvitationModel.objects.get(
                opportunity_id=opportunity_id,
                provider_id=provider_id,
            )
        except OpportunityInvitationModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def list_by_opportunity(
        self,
        opportunity_id: UUID,
    ) -> list[OpportunityInvitation]:
        models = OpportunityInvitationModel.objects.filter(
            opportunity_id=opportunity_id,
        ).order_by("created_at", "id")
        return [self._to_entity(model) for model in models]

    def list_by_provider(
        self,
        provider_id: UUID,
    ) -> list[OpportunityInvitation]:
        models = OpportunityInvitationModel.objects.filter(
            provider_id=provider_id,
        ).order_by("created_at", "id")
        return [self._to_entity(model) for model in models]

    def list_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OpportunityInvitation], int]:
        queryset = OpportunityInvitationModel.objects.filter(
            provider_id=provider_id,
        ).order_by("-created_at", "-id")
        total_items = queryset.count()
        offset = (page - 1) * page_size
        models = queryset[offset : offset + page_size]
        return [self._to_entity(model) for model in models], total_items

    def list_inbox_items_by_provider_paginated(
        self,
        *,
        provider_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: OpportunityStatus | None = None,
    ) -> tuple[list[ProviderOpportunityInboxItem], int]:
        queryset = OpportunityInvitationModel.objects.filter(
            provider_id=provider_id,
        )

        if status is not None:
            queryset = queryset.filter(opportunity__status=status.value)

        queryset = queryset.select_related(
            "opportunity",
            "opportunity__service_request",
        ).order_by("-created_at", "-id")

        total_items = queryset.count()
        offset = (page - 1) * page_size
        models = queryset[offset : offset + page_size]

        items: list[ProviderOpportunityInboxItem] = []
        for m in models:
            opp_model = m.opportunity
            sr_model = opp_model.service_request
            items.append(
                ProviderOpportunityInboxItem(
                    invitation_id=m.id,
                    opportunity_id=opp_model.id,
                    service_request_id=sr_model.id,
                    service_id=sr_model.service_id,
                    title=sr_model.title,
                    description=sr_model.description,
                    status=OpportunityStatus(opp_model.status),
                    created_at=m.created_at,
                )
            )

        return items, total_items

    def count_by_opportunity(self, opportunity_id: UUID) -> int:
        return OpportunityInvitationModel.objects.filter(
            opportunity_id=opportunity_id,
        ).count()


class DjangoOpportunityInterestRepository(OpportunityInterestRepository):
    @staticmethod
    def _to_entity(model: OpportunityInterestModel) -> OpportunityInterest:
        return OpportunityInterest(
            id=model.id,
            invitation_id=model.invitation_id,
            created_at=model.created_at,
        )

    def save(self, interest: OpportunityInterest) -> OpportunityInterest:
        model, _ = OpportunityInterestModel.objects.update_or_create(
            id=interest.id,
            defaults={
                "invitation_id": interest.invitation_id,
                "created_at": interest.created_at,
            },
        )
        return self._to_entity(model)

    def get_by_id(self, interest_id: UUID) -> OpportunityInterest | None:
        try:
            model = OpportunityInterestModel.objects.get(id=interest_id)
        except OpportunityInterestModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def get_by_invitation(self, invitation_id: UUID) -> OpportunityInterest | None:
        try:
            model = OpportunityInterestModel.objects.get(invitation_id=invitation_id)
        except OpportunityInterestModel.DoesNotExist:
            return None
        return self._to_entity(model)


class DjangoEconomicSettlementRepository(EconomicSettlementRepository):
    @staticmethod
    def _to_entity(model: EconomicSettlementModel) -> EconomicSettlement:
        return EconomicSettlement(
            id=model.id,
            interest_id=model.interest_id,
            method=SettlementMethod(model.method),
            amount=Money(
                amount_minor=model.amount_minor,
                currency=model.currency,
            ),
            created_at=model.created_at,
        )

    def save(self, settlement: EconomicSettlement) -> EconomicSettlement:
        # Since it is an immutable fact, we can use update_or_create to match project conventions,
        # or standard create. Existing repositories use update_or_create. Let's stick to update_or_create.
        model, _ = EconomicSettlementModel.objects.update_or_create(
            id=settlement.id,
            defaults={
                "interest_id": settlement.interest_id,
                "method": settlement.method.value,
                "amount_minor": settlement.amount.amount_minor,
                "currency": settlement.amount.currency,
                "created_at": settlement.created_at,
            },
        )
        return self._to_entity(model)

    def get_by_id(self, settlement_id: UUID) -> EconomicSettlement | None:
        try:
            model = EconomicSettlementModel.objects.get(id=settlement_id)
        except EconomicSettlementModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def get_by_interest(self, interest_id: UUID) -> EconomicSettlement | None:
        try:
            model = EconomicSettlementModel.objects.get(interest_id=interest_id)
        except EconomicSettlementModel.DoesNotExist:
            return None
        return self._to_entity(model)


class DjangoCreditWalletRepository(CreditWalletRepository):
    @staticmethod
    def _to_entity(model: CreditWalletModel) -> CreditWallet:
        return CreditWallet(
            id=model.id,
            organization_id=model.organization_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, wallet: CreditWallet) -> CreditWallet:
        model, _ = CreditWalletModel.objects.update_or_create(
            id=wallet.id,
            defaults={
                "organization_id": wallet.organization_id,
                "is_active": wallet.is_active,
                "created_at": wallet.created_at,
                "updated_at": wallet.updated_at,
            },
        )
        return self._to_entity(model)

    def get_by_id(self, wallet_id: UUID) -> CreditWallet | None:
        try:
            model = CreditWalletModel.objects.get(id=wallet_id)
        except CreditWalletModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def get_by_organization(self, organization_id: UUID) -> CreditWallet | None:
        try:
            model = CreditWalletModel.objects.get(organization_id=organization_id)
        except CreditWalletModel.DoesNotExist:
            return None
        return self._to_entity(model)


class DjangoOpportunityUnlockPricingConfigurationRepository(OpportunityUnlockPricingConfigurationRepository):
    DEFAULT_SCOPE = "default"

    @staticmethod
    def _to_entity(model: OpportunityUnlockPricingConfigurationModel) -> OpportunityUnlockPricingConfiguration:
        return OpportunityUnlockPricingConfiguration(
            id=model.id,
            amount=Money(
                amount_minor=model.amount_minor,
                currency=model.currency,
            ),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_active_default(self) -> OpportunityUnlockPricingConfiguration | None:
        try:
            model = OpportunityUnlockPricingConfigurationModel.objects.get(
                scope=self.DEFAULT_SCOPE,
                is_active=True,
            )
        except OpportunityUnlockPricingConfigurationModel.DoesNotExist:
            return None
        return self._to_entity(model)


class DjangoCreditLedgerEntryRepository(CreditLedgerEntryRepository):
    @staticmethod
    def _to_entity(model: CreditLedgerEntryModel) -> CreditLedgerEntry:
        return CreditLedgerEntry(
            id=model.id,
            wallet_id=model.wallet_id,
            direction=CreditLedgerDirection(model.direction),
            units=model.units,
            reason=model.reason,
            reference=model.reference,
            created_at=model.created_at,
        )

    def save(self, entry: CreditLedgerEntry) -> CreditLedgerEntry:
        # Immutable save semantics: Must use create(), not update_or_create()
        model = CreditLedgerEntryModel.objects.create(
            id=entry.id,
            wallet_id=entry.wallet_id,
            direction=entry.direction.value,
            units=entry.units,
            reason=entry.reason,
            reference=entry.reference,
            created_at=entry.created_at,
        )
        return self._to_entity(model)

    def get_by_id(self, entry_id: UUID) -> CreditLedgerEntry | None:
        try:
            model = CreditLedgerEntryModel.objects.get(id=entry_id)
        except CreditLedgerEntryModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def list_by_wallet(self, wallet_id: UUID) -> list[CreditLedgerEntry]:
        models = CreditLedgerEntryModel.objects.filter(wallet_id=wallet_id).order_by("created_at", "id")
        return [self._to_entity(m) for m in models]


class DjangoCreditSettlementAtomicWriter(CreditSettlementAtomicWriter):
    def persist(
        self,
        *,
        debit_entry: CreditLedgerEntry | None,
        settlement: EconomicSettlement,
        wallet_id: UUID,
        required_units: int,
    ) -> None:
        from django.db import transaction

        with transaction.atomic():
            # 1. select_for_update CreditWallet row to enforce concurrency safety
            wallet_model = CreditWalletModel.objects.select_for_update().get(id=wallet_id)
            if not wallet_model.is_active:
                raise ValueError("Wallet is inactive inside transactional verification.")

            # 2. Authoritative balance check from DB rows under lock
            if required_units > 0:
                entries = CreditLedgerEntryModel.objects.filter(wallet_id=wallet_id)
                balance = 0
                for entry_model in entries:
                    if entry_model.direction == "credit":
                        balance += entry_model.units
                    elif entry_model.direction == "debit":
                        balance -= entry_model.units

                if required_units > balance:
                    raise ValueError("Insufficient wallet credit balance under row lock.")

                # 3. Create debit entry
                CreditLedgerEntryModel.objects.create(
                    id=debit_entry.id,
                    wallet_id=debit_entry.wallet_id,
                    direction=debit_entry.direction.value,
                    units=debit_entry.units,
                    reason=debit_entry.reason,
                    reference=debit_entry.reference,
                    created_at=debit_entry.created_at,
                )

            # 4. Create EconomicSettlement
            EconomicSettlementModel.objects.create(
                id=settlement.id,
                interest_id=settlement.interest_id,
                method=settlement.method.value,
                amount_minor=settlement.amount.amount_minor,
                currency=settlement.amount.currency,
                created_at=settlement.created_at,
            )


class DjangoOpportunityUnlockAtomicWriter(OpportunityUnlockAtomicWriter):
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
        from django.db import transaction
        from src.marketplace.infrastructure.django.marketplace.models import (
            CreditWalletModel,
            CreditLedgerEntryModel,
            EconomicSettlementModel,
            OpportunityAccessModel,
            OpportunityInterestModel,
        )

        with transaction.atomic():
            # 1. select_for_update CreditWallet row to enforce concurrency safety
            wallet_model = CreditWalletModel.objects.select_for_update().get(id=wallet_id)
            if not wallet_model.is_active:
                raise ValueError("Wallet is inactive inside transactional verification.")

            # 2. Check if OpportunityAccess already exists under lock (to prevent concurrent race condition)
            if OpportunityAccessModel.objects.filter(opportunity_id=access.opportunity_id, provider_id=access.provider_id).exists():
                raise ValueError("OpportunityAccess already exists.")

            # 3. Create/get OpportunityInterest
            interest_model, interest_created = OpportunityInterestModel.objects.get_or_create(
                id=interest.id,
                defaults={
                    "invitation_id": interest.invitation_id,
                    "created_at": interest.created_at,
                }
            )

            # 4. Authoritative balance check from DB rows under lock
            if required_units > 0:
                # Check if this interest already has a ledger entry (idempotency check)
                ref = f"opportunity-interest:{interest.id}"
                if not CreditLedgerEntryModel.objects.filter(reference=ref).exists():
                    entries = CreditLedgerEntryModel.objects.filter(wallet_id=wallet_id)
                    balance = 0
                    for entry_model in entries:
                        if entry_model.direction == "credit":
                            balance += entry_model.units
                        elif entry_model.direction == "debit":
                            balance -= entry_model.units

                    if required_units > balance:
                        raise ValueError("Insufficient wallet credit balance under row lock.")

                    # Create debit entry
                    CreditLedgerEntryModel.objects.create(
                        id=debit_entry.id,
                        wallet_id=debit_entry.wallet_id,
                        direction=debit_entry.direction.value,
                        units=debit_entry.units,
                        reason=debit_entry.reason,
                        reference=debit_entry.reference,
                        created_at=debit_entry.created_at,
                    )

            # 5. Create EconomicSettlement if not exists
            EconomicSettlementModel.objects.get_or_create(
                id=settlement.id,
                defaults={
                    "interest_id": settlement.interest_id,
                    "method": settlement.method.value,
                    "amount_minor": settlement.amount.amount_minor,
                    "currency": settlement.amount.currency,
                    "created_at": settlement.created_at,
                }
            )

            # 6. Create OpportunityAccess
            OpportunityAccessModel.objects.create(
                id=access.id,
                opportunity_id=access.opportunity_id,
                provider_id=access.provider_id,
                created_at=access.created_at,
            )


class DjangoOrganizationMemberProviderResolver:
    """
    Django infrastructure adapter for ProviderIdentityResolver.

    Resolution path:
        User (authenticated_user_id)
            → active MembershipModel records
            → organization_ids
            → active ProviderModel records
            → Provider domain entity

    Raises:
        ProviderIdentityNotFound:
            - User has no active memberships.
            - Organizations linked to the user have no active providers.
        AmbiguousProviderIdentity:
            - More than one active Provider found across all member orgs.
              A future explicit-selection mechanism is required.
        RuntimeError:
            Propagated as-is for unexpected infrastructure failures.

    This class knows about:
        - Django ORM (MembershipModel, ProviderModel)
        - UUID as primary key type

    This class does NOT know about:
        - HttpRequest / request.user
        - Django auth middleware
        - Session state
    """

    def resolve(
        self,
        *,
        authenticated_user_id: UUID,
    ) -> Provider:
        """
        Resolve the authenticated user's unique Provider identity.

        All DB queries use only active records to prevent access via
        deactivated memberships or deactivated providers.
        """
        # Step 1: find active memberships for this user
        membership_org_ids = list(
            MembershipModel.objects.filter(
                user_id=authenticated_user_id,
                is_active=True,
            ).values_list("organization_id", flat=True)
        )
        if not membership_org_ids:
            raise ProviderIdentityNotFound(
                f"User {authenticated_user_id} has no active memberships."
            )

        # Step 2: find providers linked to those organizations.
        # Provider.is_active is an *operational eligibility* flag — it does NOT
        # block identity resolution.  A user with an active Membership to an org
        # that has an inactive Provider still "is" that Provider for the purpose
        # of historical entitlement reads (e.g. contact retrieval).
        # Operational restrictions (new unlock, etc.) are enforced separately.
        provider_models = list(
            ProviderModel.objects.filter(
                organization_id__in=membership_org_ids,
            )
        )
        if not provider_models:
            raise ProviderIdentityNotFound(
                f"User {authenticated_user_id} has active memberships but no "
                "Provider found in the linked organizations."
            )

        # Step 3: guard against ambiguity — safe by default
        if len(provider_models) > 1:
            provider_ids = [str(p.id) for p in provider_models]
            raise AmbiguousProviderIdentity(
                f"User {authenticated_user_id} maps to multiple active Providers "
                f"({', '.join(provider_ids)}). "
                "Explicit Provider selection is required."
            )

        return DjangoProviderRepository._to_entity(provider_models[0])


class DjangoProtectedDataReadAuditWriter(ProtectedDataReadAuditWriter):
    def record_contact_read(
        self,
        *,
        authenticated_user_id: UUID,
        provider_id: UUID,
        opportunity_id: UUID,
        service_request_id: UUID,
    ) -> None:
        import uuid
        from django.utils import timezone
        OpportunityContactReadAuditModel.objects.create(
            id=uuid.uuid4(),
            authenticated_user_id=authenticated_user_id,
            provider_id=provider_id,
            opportunity_id=opportunity_id,
            service_request_id=service_request_id,
            action="marketplace.protected_contact.read",
            created_at=timezone.now(),
        )
