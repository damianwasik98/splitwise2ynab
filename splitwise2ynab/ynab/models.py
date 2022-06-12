import datetime
from enum import Enum

from pydantic import BaseModel


class ClearedEnum(Enum):
    cleared: str = "cleared"
    uncleared: str = "uncleared"


class ColorEnum(Enum):
    red: str = "red"


class YNABSubTransaction(BaseModel):
    amount: int
    memo: str | None = None
    payee_name: str | None = None
    category_id: str | None = None
    deleted: bool = False


class YNABTransaction(YNABSubTransaction):
    account_id: str
    date: datetime.date
    cleared: ClearedEnum = ClearedEnum.uncleared
    approved: bool = False
    flag_color: ColorEnum | None = None
    subtransactions: list[YNABSubTransaction] = []
