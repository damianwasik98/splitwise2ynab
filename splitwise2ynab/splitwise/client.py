import datetime
from typing import Iterator

from splitwise import Splitwise

from splitwise2ynab.splitwise.exceptions import SplitwiseError
from splitwise2ynab.splitwise.helpers import parse_splitwise_expense
from splitwise2ynab.splitwise.models import SplitwiseExpense


class SplitwiseClient:
    def __init__(self, api_key: str, consumer_key: str, consumer_secret: str):
        self.api_key = api_key
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self._client = Splitwise(
            api_key=api_key,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
        )

    def get_current_user_id(self) -> int:
        return self._client.getCurrentUser().id

    def get_groups_ids_from_names(self, groups_names: list[str]) -> list[int]:
        def _cleaned_str(string: str) -> str:
            return string.lower().strip()

        groups_names = [_cleaned_str(g) for g in groups_names]
        groups_ids = [
            group.id
            for group in self._client.getGroups()
            if _cleaned_str(group.name) in groups_names
        ]

        if len(groups_ids) != len(groups_names):
            raise SplitwiseError(f"Not all groups exist in Splitwise account")

        return groups_ids

    def get_expenses(
        self,
        group_id: int,
        updated_after: datetime.date,
        limit: int = 20,
        offset: int = 0,
    ) -> list[SplitwiseExpense]:
        raw_expenses = self._client.getExpenses(
            group_id=group_id,
            updated_after=updated_after,
            limit=limit,
            offset=offset,
        )
        expenses = []
        for expense in raw_expenses:
            expense = parse_splitwise_expense(expense)
            expenses.append(expense)

        return expenses

    def generate_all_expenses(
        self,
        group_id: int,
        updated_after: datetime.date,
        expenses_in_chunk: int = 50,
    ) -> Iterator[SplitwiseExpense]:
        offset = 0
        expenses = self.get_expenses(
            group_id=group_id,
            updated_after=updated_after,
            limit=expenses_in_chunk,
            offset=offset,
        )

        while len(expenses) > 0:
            for expense in expenses:
                yield expense
            offset += expenses_in_chunk
            expenses = self.get_expenses(
                group_id=group_id,
                updated_after=updated_after,
                limit=expenses_in_chunk,
                offset=offset,
            )
