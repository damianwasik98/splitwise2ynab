import datetime
from typing import Callable

from splitwise.expense import Expense

from splitwise2ynab.splitwise.models import (
    SplitwiseExpense,
    SplitwiseExpenseParticipant,
)


def did_i_pay(current_user_participant: SplitwiseExpenseParticipant) -> bool:
    return current_user_participant.paid > 0


def parse_splitwise_expense(expense: Expense) -> SplitwiseExpense:
    return SplitwiseExpense(
        cost=expense.cost,
        description=expense.description,
        payment=expense.payment,
        date=datetime.datetime.strptime(expense.date, "%Y-%m-%dT%H:%M:%S%z"),
        deleted_at=datetime.datetime.strptime(
            expense.deleted_at, "%Y-%m-%dT%H:%M:%S%z"
        )
        if expense.deleted_at
        else None,
        reciept_url=expense.receipt.original,
        participants=[
            SplitwiseExpenseParticipant(
                participant_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                paid=user.paid_share,
                owed=user.owed_share,
            )
            for user in expense.users
        ],
    )
