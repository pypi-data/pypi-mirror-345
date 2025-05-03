from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Balance:
    asset: str
    free: Decimal
    locked: Decimal


@dataclass
class AccountInformation:
    can_trade: bool
    can_withdraw: bool
    can_deposit: bool
    update_time: int | None
    account_type: str
    balances: list[Balance]
    permissions: list[str]
