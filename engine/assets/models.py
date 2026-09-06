"""Bounded investment-holding concepts for the Financial Picture."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class InvestmentAssetType(StrEnum):
    """Supported non-cash investment categories."""

    ETF = "ETF"
    INVESTMENT_FUND = "INVESTMENT_FUND"
    INDIVIDUAL_EQUITY = "INDIVIDUAL_EQUITY"
    BOND = "BOND"
    COMMODITY = "COMMODITY"
    CRYPTOASSET = "CRYPTOASSET"
    OTHER = "OTHER"

    @property
    def customer_label(self) -> str:
        """Return the stable customer-facing category label."""
        return {
            InvestmentAssetType.ETF: "ETF",
            InvestmentAssetType.INVESTMENT_FUND: "Investment fund",
            InvestmentAssetType.INDIVIDUAL_EQUITY: "Individual shares",
            InvestmentAssetType.BOND: "Bonds / fixed income",
            InvestmentAssetType.COMMODITY: "Commodities",
            InvestmentAssetType.CRYPTOASSET: "Cryptoassets",
            InvestmentAssetType.OTHER: "Other",
        }[self]


class InvestmentHolding(BaseModel):
    """One non-cash, non-employer-equity investment holding."""

    model_config = ConfigDict(frozen=True)

    holding_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    asset_type: InvestmentAssetType
    current_value: Decimal = Field(ge=0)
    security_identifier: str | None = Field(default=None, min_length=1)
