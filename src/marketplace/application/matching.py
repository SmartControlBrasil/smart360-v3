from src.marketplace.domain.entities import MatchingResult, Provider, ServiceRequest


class TechnicalMatchingPolicyV1:
    def evaluate(
        self,
        *,
        service_request: ServiceRequest,
        provider: Provider,
    ) -> MatchingResult:
        return MatchingResult(
            provider=provider,
            score=100,
            reasons=("technical_service_match",)
        )
