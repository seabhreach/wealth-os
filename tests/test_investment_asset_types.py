"""Contracts for the deliberately bounded investment taxonomy."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from engine.assets import InvestmentAssetType, InvestmentHolding


def test_supported_asset_types_and_customer_labels_are_exact() -> None:
    """The taxonomy remains small, stable, and presentation-ready."""
    assert {asset_type.value: asset_type.customer_label for asset_type in InvestmentAssetType} == {
        "ETF": "ETF",
        "INVESTMENT_FUND": "Investment fund",
        "INDIVIDUAL_EQUITY": "Individual shares",
        "BOND": "Bonds / fixed income",
        "COMMODITY": "Commodities",
        "CRYPTOASSET": "Cryptoassets",
        "OTHER": "Other",
    }


def test_precious_metals_use_commodity_while_identity_preserves_the_exposure() -> None:
    """Gold and silver do not expand the top-level category set."""
    gold = InvestmentHolding(
        holding_id="physical-gold",
        name="Physical gold",
        asset_type=InvestmentAssetType.COMMODITY,
        current_value=Decimal("25000"),
    )

    assert gold.name == "Physical gold"
    assert gold.asset_type is InvestmentAssetType.COMMODITY
    assert "PRECIOUS_METAL" not in InvestmentAssetType.__members__


def test_other_is_the_only_controlled_escape_hatch() -> None:
    """Unsupported investments use OTHER rather than enlarging the enum ad hoc."""
    holding = InvestmentHolding.model_validate(
        {
            "holding_id": "unclassified",
            "name": "Unclassified investment",
            "asset_type": "OTHER",
            "current_value": "1",
        }
    )

    assert holding.asset_type is InvestmentAssetType.OTHER
    assert "REIT" not in InvestmentAssetType.__members__
    assert "OTHER_LISTED" not in InvestmentAssetType.__members__


def test_cash_and_employer_equity_are_not_investment_holding_types() -> None:
    """Specialised cash and employer-equity domains remain authoritative."""
    assert "CASH" not in InvestmentAssetType.__members__
    assert "CASH_EQUIVALENT" not in InvestmentAssetType.__members__
    assert "EMPLOYER_EQUITY" not in InvestmentAssetType.__members__


def test_unknown_asset_type_is_rejected() -> None:
    """The category field cannot accept an unregistered free-form value."""
    with pytest.raises(ValidationError):
        InvestmentHolding.model_validate(
            {
                "holding_id": "listed-property-fund",
                "name": "Listed property fund",
                "asset_type": "REIT",
                "current_value": "1000",
            }
        )


def test_individual_equity_can_retain_security_identity() -> None:
    """A security identifier can support future issuer-level aggregation."""
    holding = InvestmentHolding(
        holding_id="individual-equity-position",
        name="Named company shares",
        asset_type=InvestmentAssetType.INDIVIDUAL_EQUITY,
        current_value=Decimal("10000"),
        security_identifier="EXAMPLE",
    )

    assert holding.security_identifier == "EXAMPLE"
