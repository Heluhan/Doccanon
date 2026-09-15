"""Usage and revenue reporting."""

from billing import monthly_total


def revenue_for(accounts) -> int:
    return sum(monthly_total(account.plan, account.seats) for account in accounts)
