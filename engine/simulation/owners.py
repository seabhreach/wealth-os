"""Owner-age resolution for age-dependent pension and State Pension rules."""

from engine.config.models import WealthOsConfig


def owner_age_in_year(config: WealthOsConfig, owner: str, calendar_year: int) -> int:
    """Return owner start age plus elapsed projection years using the deterministic convention."""
    return owner_start_age(config, owner) + (calendar_year - config.assumptions.start_year)


def owner_start_age(config: WealthOsConfig, owner: str) -> int:
    """Map the first configured pension owner to primary age and other owners to spouse age."""
    primary_owner = config.pensions[0].owner
    return config.household.current_age if owner == primary_owner else config.household.spouse_age
