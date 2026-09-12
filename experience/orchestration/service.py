"""Narrow application service for provider interpretation and policy validation."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from time import perf_counter

from experience.orchestration.models import (
    OrchestrationRequest,
    OrchestrationResult,
    OrchestrationTelemetry,
)
from experience.orchestration.provider import OrchestrationProvider
from experience.orchestration.validation import validate_provider_response


class OrchestrationService:
    """Interpret one compact request without executing any proposed financial action."""

    def __init__(self, provider: OrchestrationProvider) -> None:
        self._provider = provider

    def interpret(self, request: OrchestrationRequest) -> OrchestrationResult:
        """Validate provider output and return it with provider-call telemetry."""

        started = perf_counter()
        response = self._provider.interpret(request)
        validate_provider_response(request, response)
        elapsed_ms = Decimal(str((perf_counter() - started) * 1000))
        return OrchestrationResult(
            response=response,
            telemetry=OrchestrationTelemetry(
                provider=self._provider.provider_name,
                model=self._provider.model_name,
                input_tokens=0 if not self._provider.makes_external_calls else None,
                output_tokens=0 if not self._provider.makes_external_calls else None,
                latency_ms=elapsed_ms,
                estimated_cost=Decimal("0"),
                interaction_id=request.interaction_id,
                session_id=request.session_id,
                success=True,
                timestamp=datetime.now(UTC),
                external_call=self._provider.makes_external_calls,
            ),
        )
