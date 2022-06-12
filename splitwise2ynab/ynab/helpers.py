from decimal import Decimal


def parse_decimal_to_ynab_amount(amount: Decimal) -> int:
    return round(amount * 1000)
