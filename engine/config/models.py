"""Validated immutable models for the single-household MVP configuration."""

from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.assets import InvestmentAssetType, InvestmentHolding


class HouseholdConfig(BaseModel):
    """Identity and life-stage inputs for the household being projected."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    current_age: int = Field(ge=0)
    spouse_age: int = Field(ge=0)
    planned_retirement_age: int = Field(ge=0)
    life_expectancy: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_age_order(self) -> Self:
        """Ensure the projection ages are chronologically possible."""
        if self.planned_retirement_age < self.current_age:
            raise ValueError("planned_retirement_age must be at least current_age")
        if self.life_expectancy < self.planned_retirement_age:
            raise ValueError("life_expectancy must be at least planned_retirement_age")
        return self


class EmploymentConfig(BaseModel):
    """Working-years income and direct annual investment contribution."""

    model_config = ConfigDict(frozen=True)

    salary: Decimal = Field(ge=0)
    annual_savings: Decimal = Field(ge=0)


class InvestmentConfig(BaseModel):
    """Cash plus the canonical ordinary taxable-investment holdings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cash_balance: Decimal = Field(ge=0)
    holdings: tuple[InvestmentHolding, ...]
    taxable_investment_growth_rate: Decimal

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_etf_input(cls, value: object) -> object:
        """Adapt the legacy aggregate ETF schema into one canonical holding."""
        if not isinstance(value, dict):
            return value
        data = dict(value)
        has_legacy_value = "etf_value" in data
        has_legacy_growth = "etf_growth_rate" in data
        if not has_legacy_value and not has_legacy_growth:
            return data
        if has_legacy_value != has_legacy_growth:
            raise ValueError("Legacy ETF input requires both etf_value and etf_growth_rate.")
        if "holdings" in data or "taxable_investment_growth_rate" in data:
            raise ValueError("Legacy ETF input cannot be combined with canonical holdings.")
        legacy_value = data.pop("etf_value")
        data["taxable_investment_growth_rate"] = data.pop("etf_growth_rate")
        data["holdings"] = (
            {
                "holding_id": "legacy-etf",
                "name": "Legacy ETF holding",
                "asset_type": InvestmentAssetType.ETF,
                "current_value": legacy_value,
            },
        )
        return data

    @model_validator(mode="after")
    def validate_holding_ids(self) -> Self:
        """Require stable holding identities within one Financial Picture."""
        holding_ids = [holding.holding_id for holding in self.holdings]
        if len(holding_ids) != len(set(holding_ids)):
            raise ValueError("Investment holding IDs must be unique.")
        return self

    @property
    def taxable_investment_value(self) -> Decimal:
        """Derive the aggregate engine balance from canonical holdings."""
        return sum((holding.current_value for holding in self.holdings), start=Decimal("0"))


class AmazonRsuConfig(BaseModel):
    """Amazon restricted-stock-unit inputs."""

    model_config = ConfigDict(frozen=True)

    vested_shares: Decimal = Field(ge=0)
    annual_grant_shares: Decimal = Field(ge=0)
    share_price_usd: Decimal = Field(ge=0)
    eur_usd_exchange_rate: Decimal = Field(gt=0)
    annual_growth_rate: Decimal
    sell_on_vest: bool


class PensionConfig(BaseModel):
    """One pension's owner, balance, growth, and contribution inputs."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    current_value: Decimal = Field(ge=0)
    annual_growth_rate: Decimal
    annual_contribution: Decimal = Field(ge=0)
    access_age: int | None = Field(default=None, ge=0)
    annual_drawdown_rate: Decimal = Field(default=Decimal("0.04"), ge=0)
    maximum_annual_withdrawal: Decimal | None = Field(default=None, ge=0)
    enabled_for_drawdown: bool = False


class StatePensionConfig(BaseModel):
    """One user-supplied State Pension planning assumption."""

    model_config = ConfigDict(frozen=True)

    owner: str = Field(min_length=1)
    enabled: bool = False
    start_age: int = Field(ge=0)
    annual_amount: Decimal = Field(ge=0)
    inflation_linked: bool = False


class PropertyOwnerConfig(BaseModel):
    """A beneficial owner used solely for tax allocation."""

    model_config = ConfigDict(frozen=True)

    person: str = Field(min_length=1)
    share: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))


class RentalPropertyConfig(BaseModel):
    """Simplified rental-property inputs."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    purchase_year: int = Field(ge=1)
    purchase_price: Decimal = Field(ge=0)
    current_value: Decimal = Field(ge=0)
    annual_net_rent: Decimal = Field(ge=0)
    annual_growth_rate: Decimal
    owners: tuple[PropertyOwnerConfig, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def validate_owner_shares(self) -> Self:
        """Validate an explicitly supplied beneficial ownership split."""
        total_share = sum((owner.share for owner in self.owners), start=Decimal("0"))
        if self.owners and abs(total_share - Decimal("1")) > Decimal("0.000001"):
            raise ValueError("Property ownership shares must total 1.00.")
        return self


class PrimaryResidenceConfig(BaseModel):
    """Household home that is recorded but never active planning capital."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    purpose: Literal["PRIMARY_RESIDENCE"] = "PRIMARY_RESIDENCE"
    estimated_market_value: Decimal = Field(ge=0)
    mortgage_balance: Decimal = Field(default=Decimal("0"), ge=0)

    @property
    def equity(self) -> Decimal:
        """Return represented home equity without activating it for planning."""
        return self.estimated_market_value - self.mortgage_balance


class AssumptionsConfig(BaseModel):
    """Projection assumptions that apply to the household."""

    model_config = ConfigDict(frozen=True)

    start_year: int = Field(ge=1)
    inflation_rate: Decimal
    target_retirement_income: Decimal = Field(ge=0)


class TaxConfig(BaseModel):
    """Opt-in, planning-only Irish tax modelling configuration."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    rules_file: str = "data/tax/ireland_2026.yaml"
    assessment_basis: Literal["joint"] = "joint"
    assessable_spouse: str | None = None
    index_future_rules_with_inflation: bool = True
    reduced_usc_enabled: bool = False
    pension_prsi_enabled: bool = False
    rental_prsi_enabled: bool = False


class WealthOsConfig(BaseModel):
    """The complete configuration for one deterministic household projection."""

    model_config = ConfigDict(frozen=True)

    household: HouseholdConfig
    employment: EmploymentConfig
    investments: InvestmentConfig
    amazon_rsus: AmazonRsuConfig
    pensions: tuple[PensionConfig, ...] = Field(min_length=1)
    rental_properties: tuple[RentalPropertyConfig, ...] = Field(default_factory=tuple, max_length=3)
    primary_residence: PrimaryResidenceConfig | None = None
    assumptions: AssumptionsConfig
    state_pensions: tuple[StatePensionConfig, ...] = Field(default_factory=tuple, max_length=2)
    tax: TaxConfig = Field(default_factory=TaxConfig)

    @model_validator(mode="after")
    def validate_tax_references(self) -> Self:
        """Require explicit, valid ownership data only for opt-in tax modelling."""
        if not self.tax.enabled:
            return self

        people = {pension.owner for pension in self.pensions}
        if self.tax.assessable_spouse not in people:
            raise ValueError("tax.assessable_spouse must reference a configured household person.")
        for state_pension in self.state_pensions:
            if state_pension.owner not in people:
                raise ValueError(
                    "State Pension owner must reference a configured household person."
                )
        for property_config in self.rental_properties:
            if not property_config.owners:
                message = (
                    f"Property '{property_config.name}' requires owners when tax modelling "
                    "is enabled."
                )
                raise ValueError(message)
            unknown_owners = {owner.person for owner in property_config.owners} - people
            if unknown_owners:
                raise ValueError(
                    f"Property '{property_config.name}' has an unknown owner: "
                    f"{', '.join(sorted(unknown_owners))}."
                )
        return self
