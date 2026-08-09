from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


@dataclass(slots=True)
class ServiceCategory:
    id: UUID
    name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        normalized_slug = self.slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service category name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service category slug cannot be empty.")

        self.name = normalized_name
        self.slug = normalized_slug
        self.description = self.description.strip()

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(slots=True)
class Service:
    id: UUID
    category_id: UUID
    name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.category_id is None:
            raise ValueError("Service category_id is required.")
        if not isinstance(self.category_id, UUID):
            raise ValueError(
                "Service category_id must be a valid UUID instance."
            )

        normalized_name = self.name.strip()
        normalized_slug = self.slug.strip().lower()

        if not normalized_name:
            raise ValueError("Service name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Service slug cannot be empty.")

        self.name = normalized_name
        self.slug = normalized_slug
        self.description = self.description.strip()

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(slots=True)
class Provider:
    id: UUID
    organization_id: UUID
    display_name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.organization_id is None:
            raise ValueError("Provider organization_id is required.")
        if not isinstance(self.organization_id, UUID):
            raise ValueError(
                "Provider organization_id must be a valid UUID instance."
            )

        normalized_display_name = self.display_name.strip()
        normalized_slug = self.slug.strip().lower()

        if not normalized_display_name:
            raise ValueError("Provider display_name cannot be empty.")

        if not normalized_slug:
            raise ValueError("Provider slug cannot be empty.")

        self.display_name = normalized_display_name
        self.slug = normalized_slug
        self.description = self.description.strip()

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(slots=True)
class ProviderService:
    id: UUID
    provider_id: UUID
    service_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.provider_id is None:
            raise ValueError("ProviderService provider_id is required.")
        if not isinstance(self.provider_id, UUID):
            raise ValueError(
                "ProviderService provider_id must be a valid UUID instance."
            )

        if self.service_id is None:
            raise ValueError("ProviderService service_id is required.")
        if not isinstance(self.service_id, UUID):
            raise ValueError(
                "ProviderService service_id must be a valid UUID instance."
            )

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


class ServiceRequestStatus(StrEnum):
    OPEN = "open"
    CANCELLED = "cancelled"
    CLOSED = "closed"


@dataclass(slots=True)
class ServiceRequest:
    id: UUID
    organization_id: UUID
    service_id: UUID
    title: str
    description: str
    status: ServiceRequestStatus
    created_at: datetime
    updated_at: datetime
    requester_name: str = ""
    requester_email: str = ""
    requester_phone: str = ""

    def __post_init__(self) -> None:
        if self.organization_id is None:
            raise ValueError("ServiceRequest organization_id is required.")
        if not isinstance(self.organization_id, UUID):
            raise ValueError(
                "ServiceRequest organization_id must be a valid UUID instance."
            )

        if self.service_id is None:
            raise ValueError("ServiceRequest service_id is required.")
        if not isinstance(self.service_id, UUID):
            raise ValueError(
                "ServiceRequest service_id must be a valid UUID instance."
            )

        normalized_title = self.title.strip()
        if not normalized_title:
            raise ValueError("ServiceRequest title cannot be empty.")

        if not isinstance(self.status, ServiceRequestStatus):
            raise ValueError("ServiceRequest status must be a ServiceRequestStatus.")

        if self.requester_name is None or not isinstance(self.requester_name, str):
            raise ValueError("ServiceRequest requester_name must be a string.")
        if self.requester_email is None or not isinstance(self.requester_email, str):
            raise ValueError("ServiceRequest requester_email must be a string.")
        if self.requester_phone is None or not isinstance(self.requester_phone, str):
            raise ValueError("ServiceRequest requester_phone must be a string.")

        self.title = normalized_title
        self.description = self.description.strip()
        self.requester_name = self.requester_name.strip()
        self.requester_email = self.requester_email.strip()
        self.requester_phone = self.requester_phone.strip()

    def cancel(self) -> None:
        if self.status is not ServiceRequestStatus.OPEN:
            raise ValueError("Only OPEN service requests can be cancelled.")
        self.status = ServiceRequestStatus.CANCELLED

    def close(self) -> None:
        if self.status is not ServiceRequestStatus.OPEN:
            raise ValueError("Only OPEN service requests can be closed.")
        self.status = ServiceRequestStatus.CLOSED


@dataclass(frozen=True, slots=True)
class ProtectedCommercialData:
    requester_name: str
    requester_email: str
    requester_phone: str

    def __post_init__(self) -> None:
        if self.requester_name is None or not isinstance(self.requester_name, str):
            raise ValueError("requester_name must be a string.")
        if self.requester_email is None or not isinstance(self.requester_email, str):
            raise ValueError("requester_email must be a string.")
        if self.requester_phone is None or not isinstance(self.requester_phone, str):
            raise ValueError("requester_phone must be a string.")

        normalized_name = self.requester_name.strip()
        normalized_email = self.requester_email.strip()
        normalized_phone = self.requester_phone.strip()

        if not normalized_name:
            raise ValueError("requester_name cannot be empty.")

        if not normalized_email and not normalized_phone:
            raise ValueError("At least one usable contact channel must exist: email OR phone.")

        object.__setattr__(self, "requester_name", normalized_name)
        object.__setattr__(self, "requester_email", normalized_email)
        object.__setattr__(self, "requester_phone", normalized_phone)



class OpportunityStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Opportunity:
    id: UUID
    service_request_id: UUID
    status: OpportunityStatus
    max_accesses: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.service_request_id is None:
            raise ValueError("Opportunity service_request_id is required.")
        if not isinstance(self.service_request_id, UUID):
            raise ValueError(
                "Opportunity service_request_id must be a valid UUID instance."
            )

        if not isinstance(self.status, OpportunityStatus):
            raise ValueError("Opportunity status must be an OpportunityStatus.")

        if isinstance(self.max_accesses, bool) or not isinstance(
            self.max_accesses,
            int,
        ):
            raise ValueError("Opportunity max_accesses must be an integer.")
        if self.max_accesses < 1:
            raise ValueError("Opportunity max_accesses must be at least 1.")

    def close(self) -> None:
        if self.status is not OpportunityStatus.OPEN:
            raise ValueError("Only OPEN opportunities can be closed.")
        self.status = OpportunityStatus.CLOSED

    def cancel(self) -> None:
        if self.status is not OpportunityStatus.OPEN:
            raise ValueError("Only OPEN opportunities can be cancelled.")
        self.status = OpportunityStatus.CANCELLED


@dataclass(slots=True)
class OpportunityAccess:
    id: UUID
    opportunity_id: UUID
    provider_id: UUID
    created_at: datetime

    def __post_init__(self) -> None:
        if self.opportunity_id is None:
            raise ValueError("OpportunityAccess opportunity_id is required.")
        if not isinstance(self.opportunity_id, UUID):
            raise ValueError(
                "OpportunityAccess opportunity_id must be a valid UUID instance."
            )

        if self.provider_id is None:
            raise ValueError("OpportunityAccess provider_id is required.")
        if not isinstance(self.provider_id, UUID):
            raise ValueError(
                "OpportunityAccess provider_id must be a valid UUID instance."
            )


@dataclass(frozen=True, slots=True)
class OpportunityPreview:
    opportunity_id: UUID
    service_request_id: UUID
    service_id: UUID
    title: str
    description: str
    status: OpportunityStatus
    created_at: datetime

    def __post_init__(self) -> None:
        if self.opportunity_id is None or not isinstance(self.opportunity_id, UUID):
            raise ValueError("opportunity_id must be a UUID instance.")
        if self.service_request_id is None or not isinstance(self.service_request_id, UUID):
            raise ValueError("service_request_id must be a UUID instance.")
        if self.service_id is None or not isinstance(self.service_id, UUID):
            raise ValueError("service_id must be a UUID instance.")
        if self.title is None or not isinstance(self.title, str):
            raise ValueError("title must be a string.")
        if self.description is None or not isinstance(self.description, str):
            raise ValueError("description must be a string.")
        if self.status is None or not isinstance(self.status, OpportunityStatus):
            raise ValueError("status must be an OpportunityStatus instance.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime instance.")

        normalized_title = self.title.strip()
        normalized_description = self.description.strip()

        if not normalized_title:
            raise ValueError("title cannot be empty.")

        object.__setattr__(self, "title", normalized_title)
        object.__setattr__(self, "description", normalized_description)


@dataclass(slots=True, frozen=True)
class MatchingResult:
    provider: Provider
    score: int
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.provider, Provider):
            raise ValueError("MatchingResult provider must be a Provider domain object.")

        if isinstance(self.score, bool) or not isinstance(self.score, int):
            raise ValueError("MatchingResult score must be an integer.")

        if not (0 <= self.score <= 100):
            raise ValueError("MatchingResult score must be between 0 and 100.")

        if not isinstance(self.reasons, tuple):
            raise ValueError("MatchingResult reasons must be a tuple of strings.")

        if not self.reasons:
            raise ValueError("MatchingResult reasons cannot be empty.")

        normalized_reasons: list[str] = []
        for reason in self.reasons:
            if not isinstance(reason, str):
                raise ValueError("MatchingResult reason must be a string.")
            normalized = reason.strip()
            if not normalized:
                raise ValueError("MatchingResult reason cannot be empty or blank.")
            normalized_reasons.append(normalized)

        object.__setattr__(self, "reasons", tuple(normalized_reasons))


@dataclass(slots=True)
class OpportunityInvitation:
    id: UUID
    opportunity_id: UUID
    provider_id: UUID
    created_at: datetime

    def __post_init__(self) -> None:
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("OpportunityInvitation id must be a valid UUID instance.")
        if self.opportunity_id is None or not isinstance(self.opportunity_id, UUID):
            raise ValueError("OpportunityInvitation opportunity_id must be a valid UUID instance.")
        if self.provider_id is None or not isinstance(self.provider_id, UUID):
            raise ValueError("OpportunityInvitation provider_id must be a valid UUID instance.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("OpportunityInvitation created_at must be a datetime instance.")
        if self.created_at.tzinfo is None:
            raise ValueError("OpportunityInvitation created_at must be timezone-aware.")


@dataclass(slots=True)
class OpportunityInterest:
    id: UUID
    invitation_id: UUID
    created_at: datetime

    def __post_init__(self) -> None:
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("OpportunityInterest id must be a valid UUID instance.")
        if self.invitation_id is None or not isinstance(self.invitation_id, UUID):
            raise ValueError("OpportunityInterest invitation_id must be a valid UUID instance.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("OpportunityInterest created_at must be a datetime instance.")
        if self.created_at.tzinfo is None:
            raise ValueError("OpportunityInterest created_at must be timezone-aware.")


@dataclass(frozen=True, slots=True)
class AccessEntitlementDecision:
    allowed: bool
    reason: str

    def __post_init__(self) -> None:
        if self.allowed is None or not isinstance(self.allowed, bool):
            raise ValueError("AccessEntitlementDecision allowed must be a boolean.")

        if self.reason is None or not isinstance(self.reason, str):
            raise ValueError("AccessEntitlementDecision reason must be a string.")

        normalized_reason = self.reason.strip()
        if not normalized_reason:
            raise ValueError("AccessEntitlementDecision reason cannot be empty.")

        # In Python dataclass, slots are used, but we can set using object.__setattr__
        object.__setattr__(self, "reason", normalized_reason)


@dataclass(frozen=True, slots=True)
class RequestOpportunityAccessResult:
    decision: AccessEntitlementDecision
    access: OpportunityAccess | None

    def __post_init__(self) -> None:
        if self.decision is None or not isinstance(self.decision, AccessEntitlementDecision):
            raise ValueError("decision must be an AccessEntitlementDecision instance.")

        if self.decision.allowed:
            if self.access is None or not isinstance(self.access, OpportunityAccess):
                raise ValueError("access is required and must be an OpportunityAccess instance when allowed is True.")
        else:
            if self.access is not None:
                raise ValueError("access must be None when allowed is False.")


@dataclass(frozen=True, slots=True)
class Money:
    amount_minor: int
    currency: str

    def __post_init__(self) -> None:
        if self.amount_minor is None or isinstance(self.amount_minor, bool) or not isinstance(self.amount_minor, int):
            raise ValueError("Money amount_minor must be an integer.")
        if self.amount_minor < 0:
            raise ValueError("Money amount_minor must be non-negative.")

        if self.currency is None or not isinstance(self.currency, str):
            raise ValueError("Money currency must be a string.")

        normalized_currency = self.currency.strip().upper()
        if not normalized_currency:
            raise ValueError("Money currency cannot be empty.")
        if len(normalized_currency) != 3 or not normalized_currency.isalpha():
            raise ValueError("Money currency must be exactly 3 alphabetic characters.")

        object.__setattr__(self, "currency", normalized_currency)


@dataclass(frozen=True, slots=True)
class OpportunityPricingQuote:
    amount: Money
    reason: str

    def __post_init__(self) -> None:
        if self.amount is None or not isinstance(self.amount, Money):
            raise ValueError("OpportunityPricingQuote amount must be a Money instance.")

        if self.reason is None or not isinstance(self.reason, str):
            raise ValueError("OpportunityPricingQuote reason must be a string.")

        normalized_reason = self.reason.strip()
        if not normalized_reason:
            raise ValueError("OpportunityPricingQuote reason cannot be empty.")

        object.__setattr__(self, "reason", normalized_reason)


class OpportunityPricingUnavailable(Exception):
    pass


@dataclass(frozen=True, slots=True)
class OpportunityUnlockPricingConfiguration:
    id: UUID
    amount: Money
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("OpportunityUnlockPricingConfiguration id must be a UUID instance.")
        if self.amount is None or not isinstance(self.amount, Money):
            raise ValueError("OpportunityUnlockPricingConfiguration amount must be a Money instance.")
        if self.amount.amount_minor <= 0:
            raise ValueError("OpportunityUnlockPricingConfiguration amount must be greater than zero.")
        if self.is_active is None or not isinstance(self.is_active, bool):
            raise ValueError("OpportunityUnlockPricingConfiguration is_active must be a boolean.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("OpportunityUnlockPricingConfiguration created_at must be a datetime instance.")
        if self.created_at.tzinfo is None:
            raise ValueError("OpportunityUnlockPricingConfiguration created_at must be timezone-aware.")
        if self.updated_at is None or not isinstance(self.updated_at, datetime):
            raise ValueError("OpportunityUnlockPricingConfiguration updated_at must be a datetime instance.")
        if self.updated_at.tzinfo is None:
            raise ValueError("OpportunityUnlockPricingConfiguration updated_at must be timezone-aware.")
        if self.updated_at < self.created_at:
            raise ValueError("OpportunityUnlockPricingConfiguration updated_at cannot be before created_at.")


@dataclass(frozen=True, slots=True)
class OpportunityUnlockQuote:
    opportunity_id: UUID
    provider_id: UUID
    amount: Money | None
    quote_available: bool
    already_unlocked: bool
    reason: str

    def __post_init__(self) -> None:
        if self.opportunity_id is None or not isinstance(self.opportunity_id, UUID):
            raise ValueError("opportunity_id must be a UUID instance.")
        if self.provider_id is None or not isinstance(self.provider_id, UUID):
            raise ValueError("provider_id must be a UUID instance.")
        if self.amount is not None and not isinstance(self.amount, Money):
            raise ValueError("amount must be a Money instance or None.")
        if not isinstance(self.quote_available, bool):
            raise ValueError("quote_available must be a boolean.")
        if not isinstance(self.already_unlocked, bool):
            raise ValueError("already_unlocked must be a boolean.")
        if self.reason is None or not isinstance(self.reason, str):
            raise ValueError("reason must be a string.")

        normalized_reason = self.reason.strip()
        if not normalized_reason:
            raise ValueError("reason cannot be empty.")

        object.__setattr__(self, "reason", normalized_reason)

        if self.amount is not None and self.amount.amount_minor < 0:
            raise ValueError("amount cannot be negative.")


class SettlementMethod(StrEnum):
    MANUAL = "manual"
    COMPLIMENTARY = "complimentary"
    CREDIT = "credit"


@dataclass(frozen=True, slots=True)
class EconomicSettlement:
    id: UUID
    interest_id: UUID
    method: SettlementMethod
    amount: Money
    created_at: datetime

    def __post_init__(self) -> None:
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("EconomicSettlement id must be a UUID instance.")
        if self.interest_id is None or not isinstance(self.interest_id, UUID):
            raise ValueError("EconomicSettlement interest_id must be a UUID instance.")
        if self.method is None or not isinstance(self.method, SettlementMethod):
            raise ValueError("EconomicSettlement method must be a SettlementMethod instance.")
        if self.amount is None or not isinstance(self.amount, Money):
            raise ValueError("EconomicSettlement amount must be a Money instance.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("EconomicSettlement created_at must be a datetime instance.")
        if self.created_at.tzinfo is None:
            raise ValueError("EconomicSettlement created_at must be timezone-aware.")

        if self.method is SettlementMethod.COMPLIMENTARY and self.amount.amount_minor != 0:
            raise ValueError("COMPLIMENTARY settlement method requires amount_minor to be 0.")


@dataclass(slots=True)
class CreditWallet:
    id: UUID
    organization_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("CreditWallet id must be a valid UUID instance.")
        if self.organization_id is None or not isinstance(self.organization_id, UUID):
            raise ValueError("CreditWallet organization_id must be a valid UUID instance.")
        if self.is_active is None or not isinstance(self.is_active, bool):
            raise ValueError("CreditWallet is_active must be a boolean.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("CreditWallet created_at must be a datetime instance.")
        if self.created_at.tzinfo is None:
            raise ValueError("CreditWallet created_at must be timezone-aware.")
        if self.updated_at is None or not isinstance(self.updated_at, datetime):
            raise ValueError("CreditWallet updated_at must be a datetime instance.")
        if self.updated_at.tzinfo is None:
            raise ValueError("CreditWallet updated_at must be timezone-aware.")
        if self.updated_at < self.created_at:
            raise ValueError("CreditWallet updated_at cannot be before created_at.")

    def activate(self, current_time: datetime) -> None:
        if current_time is None or not isinstance(current_time, datetime) or current_time.tzinfo is None:
            raise ValueError("activate requires a timezone-aware datetime instance.")
        if current_time < self.updated_at:
            raise ValueError("current_time cannot be before updated_at.")
        self.is_active = True
        self.updated_at = current_time

    def deactivate(self, current_time: datetime) -> None:
        if current_time is None or not isinstance(current_time, datetime) or current_time.tzinfo is None:
            raise ValueError("deactivate requires a timezone-aware datetime instance.")
        if current_time < self.updated_at:
            raise ValueError("current_time cannot be before updated_at.")
        self.is_active = False
        self.updated_at = current_time


class CreditLedgerDirection(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"


@dataclass(frozen=True, slots=True)
class CreditLedgerEntry:
    id: UUID
    wallet_id: UUID
    direction: CreditLedgerDirection
    units: int
    reason: str
    reference: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("CreditLedgerEntry id must be a valid UUID instance.")
        if self.wallet_id is None or not isinstance(self.wallet_id, UUID):
            raise ValueError("CreditLedgerEntry wallet_id must be a valid UUID instance.")
        if self.direction is None or not isinstance(self.direction, CreditLedgerDirection):
            raise ValueError("CreditLedgerEntry direction must be a CreditLedgerDirection instance.")

        if self.units is None or isinstance(self.units, bool) or not isinstance(self.units, int):
            raise ValueError("CreditLedgerEntry units must be an integer.")
        if self.units <= 0:
            raise ValueError("CreditLedgerEntry units must be positive (> 0).")

        if self.reason is None or not isinstance(self.reason, str):
            raise ValueError("CreditLedgerEntry reason must be a string.")
        normalized_reason = self.reason.strip()
        if not normalized_reason:
            raise ValueError("CreditLedgerEntry reason cannot be empty.")
        object.__setattr__(self, "reason", normalized_reason)

        if self.reference is not None:
            if not isinstance(self.reference, str):
                raise ValueError("CreditLedgerEntry reference must be None or a string.")
            normalized_ref = self.reference.strip()
            if not normalized_ref:
                raise ValueError("CreditLedgerEntry reference cannot be empty when supplied.")
            object.__setattr__(self, "reference", normalized_ref)

        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("CreditLedgerEntry created_at must be a datetime instance.")
        if self.created_at.tzinfo is None:
            raise ValueError("CreditLedgerEntry created_at must be timezone-aware.")


@dataclass(frozen=True, slots=True)
class CreditSettlementResult:
    pricing_quote: OpportunityPricingQuote
    credit_units: int
    debit_entry: CreditLedgerEntry | None
    settlement: EconomicSettlement

    def __post_init__(self) -> None:
        if self.pricing_quote is None or not isinstance(self.pricing_quote, OpportunityPricingQuote):
            raise ValueError("pricing_quote must be an OpportunityPricingQuote instance.")
        if self.credit_units is None or isinstance(self.credit_units, bool) or not isinstance(self.credit_units, int):
            raise ValueError("credit_units must be an integer.")
        if self.credit_units < 0:
            raise ValueError("credit_units cannot be negative.")

        if self.credit_units == 0 and self.debit_entry is not None:
            raise ValueError("debit_entry must be None when credit_units is 0.")
        if self.credit_units > 0 and self.debit_entry is None:
            raise ValueError("debit_entry must be provided when credit_units > 0.")

        if self.debit_entry is not None:
            if not isinstance(self.debit_entry, CreditLedgerEntry):
                raise ValueError("debit_entry must be a CreditLedgerEntry instance.")
            if self.debit_entry.direction is not CreditLedgerDirection.DEBIT:
                raise ValueError("debit_entry direction must be DEBIT.")

        if self.settlement is None or not isinstance(self.settlement, EconomicSettlement):
            raise ValueError("settlement must be an EconomicSettlement instance.")
        if self.settlement.method is not SettlementMethod.CREDIT:
            raise ValueError("settlement method must be CREDIT.")


@dataclass(frozen=True, slots=True)
class OpportunityUnlockResult:
    access: OpportunityAccess
    already_unlocked: bool
    settlement_id: UUID | None
    amount: Money | None

    def __post_init__(self) -> None:
        if self.access is None or not isinstance(self.access, OpportunityAccess):
            raise ValueError("access must be an OpportunityAccess instance.")
        if self.already_unlocked is None or not isinstance(self.already_unlocked, bool):
            raise ValueError("already_unlocked must be a boolean.")
        if self.settlement_id is not None and not isinstance(self.settlement_id, UUID):
            raise ValueError("settlement_id must be a UUID instance or None.")
        if self.amount is not None and not isinstance(self.amount, Money):
            raise ValueError("amount must be a Money instance or None.")


@dataclass(frozen=True, slots=True)
class UnlockedOpportunityContact:
    opportunity_id: UUID
    service_request_id: UUID
    requester_name: str
    requester_email: str
    requester_phone: str

    def __post_init__(self) -> None:
        if self.opportunity_id is None or not isinstance(self.opportunity_id, UUID):
            raise ValueError("opportunity_id must be a UUID instance.")
        if self.service_request_id is None or not isinstance(self.service_request_id, UUID):
            raise ValueError("service_request_id must be a UUID instance.")
        if self.requester_name is None or not isinstance(self.requester_name, str):
            raise ValueError("requester_name must be a string.")
        if self.requester_email is None or not isinstance(self.requester_email, str):
            raise ValueError("requester_email must be a string.")
        if self.requester_phone is None or not isinstance(self.requester_phone, str):
            raise ValueError("requester_phone must be a string.")

        object.__setattr__(self, "requester_name", self.requester_name.strip())
        object.__setattr__(self, "requester_email", self.requester_email.strip())
        object.__setattr__(self, "requester_phone", self.requester_phone.strip())


@dataclass(frozen=True, slots=True)
class ProviderOpportunityInboxItem:
    invitation_id: UUID
    opportunity_id: UUID
    service_request_id: UUID
    service_id: UUID
    title: str
    description: str
    status: OpportunityStatus
    created_at: datetime

    def __post_init__(self) -> None:
        if self.invitation_id is None or not isinstance(self.invitation_id, UUID):
            raise ValueError("invitation_id must be a UUID instance.")
        if self.opportunity_id is None or not isinstance(self.opportunity_id, UUID):
            raise ValueError("opportunity_id must be a UUID instance.")
        if self.service_request_id is None or not isinstance(self.service_request_id, UUID):
            raise ValueError("service_request_id must be a UUID instance.")
        if self.service_id is None or not isinstance(self.service_id, UUID):
            raise ValueError("service_id must be a UUID instance.")
        if self.title is None or not isinstance(self.title, str):
            raise ValueError("title must be a string.")
        if self.description is None or not isinstance(self.description, str):
            raise ValueError("description must be a string.")
        if self.status is None or not isinstance(self.status, OpportunityStatus):
            raise ValueError("status must be an OpportunityStatus instance.")
        if self.created_at is None or not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime instance.")

        normalized_title = self.title.strip()
        normalized_description = self.description.strip()
        if not normalized_title:
            raise ValueError("title cannot be empty.")

        object.__setattr__(self, "title", normalized_title)
        object.__setattr__(self, "description", normalized_description)


@dataclass(frozen=True, slots=True)
class ProviderOpportunityInboxPage:
    items: list[ProviderOpportunityInboxItem]
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass(frozen=True, slots=True)
class ProviderUnlockedOpportunityItem:
    opportunity_id: UUID
    service_request_id: UUID
    service_id: UUID
    title: str
    description: str
    status: OpportunityStatus
    unlocked_at: datetime

    def __post_init__(self) -> None:
        if self.opportunity_id is None or not isinstance(self.opportunity_id, UUID):
            raise ValueError("opportunity_id must be a UUID instance.")
        if self.service_request_id is None or not isinstance(self.service_request_id, UUID):
            raise ValueError("service_request_id must be a UUID instance.")
        if self.service_id is None or not isinstance(self.service_id, UUID):
            raise ValueError("service_id must be a UUID instance.")
        if self.title is None or not isinstance(self.title, str):
            raise ValueError("title must be a string.")
        if self.description is None or not isinstance(self.description, str):
            raise ValueError("description must be a string.")
        if self.status is None or not isinstance(self.status, OpportunityStatus):
            raise ValueError("status must be an OpportunityStatus instance.")
        if self.unlocked_at is None or not isinstance(self.unlocked_at, datetime):
            raise ValueError("unlocked_at must be a datetime instance.")

        normalized_title = self.title.strip()
        normalized_description = self.description.strip()
        if not normalized_title:
            raise ValueError("title cannot be empty.")

        object.__setattr__(self, "title", normalized_title)
        object.__setattr__(self, "description", normalized_description)


@dataclass(frozen=True, slots=True)
class ProviderUnlockedOpportunityPage:
    items: list[ProviderUnlockedOpportunityItem]
    page: int
    page_size: int
    total_items: int
    total_pages: int
