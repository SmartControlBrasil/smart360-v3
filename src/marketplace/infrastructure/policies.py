from src.marketplace.application.ports import OpportunityPricingPolicy, CreditCostPolicy
from src.marketplace.domain.entities import (
    Money,
    OpportunityPricingQuote,
    OpportunityPricingUnavailable,
    OpportunityInterest,
    OpportunityInvitation,
    Opportunity,
    Provider,
)


class UnconfiguredOpportunityPricingPolicy(OpportunityPricingPolicy):
    """
    Production policy when no commercial pricing model is configured.
    Always raises OpportunityPricingUnavailable to signal that pre-access pricing is unconfigured.
    """

    def quote(
        self,
        *,
        interest: OpportunityInterest | None = None,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> OpportunityPricingQuote:
        raise OpportunityPricingUnavailable(
            "No commercial pricing configured for pre-access unlock."
        )


class UnconfiguredCreditCostPolicy(CreditCostPolicy):
    """
    Production policy when no Money->Credit conversion rate is configured.
    Always raises ValueError to prevent economic debits without a legitimate commercial cost rule.
    """

    def units_required(
        self,
        *,
        price: Money,
        interest: OpportunityInterest,
        invitation: OpportunityInvitation,
        opportunity: Opportunity,
        provider: Provider,
    ) -> int:
        raise ValueError("No commercial credit cost conversion policy configured.")
