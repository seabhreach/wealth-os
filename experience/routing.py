"""Deterministic intent routing for the bounded pre-AI Experience shell."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from experience.models import GoalId


@dataclass(frozen=True, slots=True)
class RoutedQuestion:
    """A supported goal plus any explicit temporary exploration value."""

    goal_id: GoalId
    retirement_age: int | None = None
    retirement_spending: Decimal | None = None
    calendar_year: int | None = None


def route_question(question: str) -> RoutedQuestion | None:
    """Route obvious natural questions without pretending to be general AI."""

    normalized = " ".join(question.casefold().replace("-", " ").split())

    spending_amount = _money_amount(normalized)
    if _contains_any(
        normalized,
        (
            "cash decline",
            "cash fall",
            "cash falling",
            "cash drop",
            "cash going down",
            "cash balance",
            "explain my cash",
        ),
    ):
        return RoutedQuestion(GoalId.CASH_DECLINE, calendar_year=_calendar_year(normalized))

    if _contains_any(
        normalized,
        (
            "employer shares",
            "company shares",
            "employer equity",
            "equity concentration",
            "share exposure",
            "stock awards",
            "rsus",
            "vesting",
        ),
    ):
        return RoutedQuestion(GoalId.EMPLOYER_EQUITY)

    if _contains_any(
        normalized,
        (
            "investment property",
            "rental property",
            "another property",
            "property investment",
        ),
    ):
        return RoutedQuestion(GoalId.INVESTMENT_PROPERTY)

    if _contains_any(
        normalized,
        (
            "spend more in retirement",
            "spent more in retirement",
            "higher retirement spending",
            "increase retirement spending",
            "retirement spending",
            "extra spending",
        ),
    ) or ("spend" in normalized and spending_amount is not None):
        return RoutedQuestion(
            GoalId.HIGHER_SPENDING,
            retirement_spending=spending_amount,
        )

    retirement_language = _contains_any(
        normalized,
        (
            "retire",
            "retirement age",
            "stop working",
            "finish working",
        ),
    )
    if retirement_language:
        return RoutedQuestion(GoalId.RETIRE_EARLIER, retirement_age=_retirement_age(normalized))

    return None


def _contains_any(value: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in value for phrase in phrases)


def _retirement_age(value: str) -> int | None:
    explicit = re.search(
        r"(?:retire|retirement|working)\s+(?:at|by|before|from)\s+(\d{2})\b", value
    )
    if explicit is None:
        return None
    return int(explicit.group(1))


def _calendar_year(value: str) -> int | None:
    match = re.search(r"\b(20\d{2})\b", value)
    return int(match.group(1)) if match else None


def _money_amount(value: str) -> Decimal | None:
    match = re.search(r"(?:€|eur\s*)?(\d{2,3})(?:[ ,]?(\d{3}))?\s*(k)?\b", value)
    if match is None:
        return None
    leading, trailing, thousands = match.groups()
    if trailing:
        return Decimal(f"{leading}{trailing}")
    if thousands:
        return Decimal(leading) * Decimal("1000")
    amount = Decimal(leading)
    return amount if amount >= Decimal("10000") else None
