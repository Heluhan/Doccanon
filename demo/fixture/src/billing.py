"""Subscription billing."""

PLANS = {"free": 0, "pro": 20, "team": 60}


def monthly_total(plan: str, seats: int) -> int:
    return PLANS.get(plan, 0) * max(seats, 1)
