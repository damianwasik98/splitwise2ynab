import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from splitwise2ynab.splitwise.exceptions import SplitwiseError


class SplitwiseExpenseParticipant(BaseModel):
    participant_id: int
    first_name: str
    last_name: Optional[str]
    paid: Decimal
    owed: Decimal

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class SplitwiseExpense(BaseModel):
    cost: Decimal
    description: str
    payment: bool
    date: datetime.date
    deleted_at: Optional[datetime.date]
    reciept_url: Optional[str]
    participants: list[SplitwiseExpenseParticipant]

    def get_participant(
        self, participant_id: int
    ) -> SplitwiseExpenseParticipant:
        for part in self.participants:
            if part.participant_id == participant_id:
                return part
        raise SplitwiseError(f"Participant {participant_id} not found")

    def get_paid_participant(self) -> SplitwiseExpenseParticipant:
        for part in self.participants:
            if part.paid > 0:
                return part
        raise SplitwiseError("No one paid in this transaction?")
