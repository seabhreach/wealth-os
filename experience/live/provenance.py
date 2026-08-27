"""Stable serialization and provenance for deterministic live evidence."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from engine.config import WealthOsConfig
from experience.live.models import Provenance
from experience.models import GoalId

SIMULATION_VERSION = "wealth-os-v0.2.0:project_annually"
EVIDENCE_POLICY_VERSION = "experience-live-evidence-v1"


def stable_fingerprint(value: object) -> str:
    """Hash stable JSON without reprs, addresses, or incidental timestamps."""

    payload = json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def financial_picture_fingerprint(configuration: WealthOsConfig) -> str:
    """Identify the complete validated baseline configuration deterministically."""

    return stable_fingerprint(configuration)


def tax_rule_identifier(configuration: WealthOsConfig, repository_root: Path) -> str | None:
    """Identify the configured rules file without interpreting tax behavior."""

    if not configuration.tax.enabled:
        return None
    rules_path = repository_root / configuration.tax.rules_file
    rules_fingerprint = stable_fingerprint(rules_path.read_text(encoding="utf-8"))
    return f"{configuration.tax.rules_file}:{rules_fingerprint}"


def build_provenance(
    *,
    baseline_identifier: str,
    picture_fingerprint: str,
    goal_id: GoalId,
    scenario_overrides: tuple[tuple[str, str], ...],
    tax_identifier: str | None,
    deterministic_result: object,
    generated_at: datetime | None = None,
) -> Provenance:
    """Build provenance whose timestamp is excluded from deterministic result identity."""

    return Provenance(
        baseline_identifier=baseline_identifier,
        financial_picture_fingerprint=picture_fingerprint,
        goal_id=goal_id,
        scenario_overrides=tuple(sorted(scenario_overrides)),
        simulation_version=SIMULATION_VERSION,
        tax_rule_identifier=tax_identifier,
        evidence_policy_version=EVIDENCE_POLICY_VERSION,
        result_fingerprint=stable_fingerprint(
            {
                "baseline": baseline_identifier,
                "financial_picture": picture_fingerprint,
                "goal": goal_id.value,
                "overrides": tuple(sorted(scenario_overrides)),
                "simulation": SIMULATION_VERSION,
                "tax": tax_identifier,
                "result": deterministic_result,
            }
        ),
        generated_at=generated_at or datetime.now(UTC),
    )


def provenance_identity(provenance: Provenance) -> str:
    """Return provenance identity while deliberately excluding generation time."""

    return stable_fingerprint(
        {
            "baseline_identifier": provenance.baseline_identifier,
            "financial_picture_fingerprint": provenance.financial_picture_fingerprint,
            "goal_id": provenance.goal_id,
            "scenario_overrides": provenance.scenario_overrides,
            "simulation_version": provenance.simulation_version,
            "tax_rule_identifier": provenance.tax_rule_identifier,
            "evidence_policy_version": provenance.evidence_policy_version,
            "result_fingerprint": provenance.result_fingerprint,
        }
    )


def _canonical(value: object) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return _canonical(value.value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, BaseModel):
        return _canonical(value.model_dump(mode="python"))
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    raise TypeError(f"Unsupported fingerprint value: {type(value).__name__}")
