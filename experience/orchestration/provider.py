"""Provider abstraction for orchestration interpretation."""

from __future__ import annotations

from typing import Protocol

from experience.orchestration.models import OrchestrationRequest, OrchestrationResponse


class OrchestrationProvider(Protocol):
    """Provider-neutral interpretation interface; providers do not execute actions."""

    provider_name: str
    model_name: str | None
    makes_external_calls: bool

    def interpret(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """Return an untrusted structured interpretation for platform validation."""
