import json
from functools import lru_cache

import requests

from splitwise2ynab.ynab.exceptions import YNABNotFoundError
from splitwise2ynab.ynab.models import YNABSubTransaction, YNABTransaction


class YNABClient:
    API_HOST: str = "https://api.youneedabudget.com/v1"

    def __init__(self, api_key: str) -> None:
        self._session = requests.Session()
        self._session.headers["Authorization"] = api_key

    @lru_cache(maxsize=10)
    def _get_all_budgets(self) -> list[dict]:
        endpoint = f"{self.API_HOST}/budgets"
        response = self._session.get(
            endpoint, params={"include_accounts": True}
        )
        return response.json()["data"]["budgets"]

    def _get_all_categories(self, budget_id: str) -> list[dict]:
        endpoint = f"{self.API_HOST}/budgets/{budget_id}/categories"
        response = self._session.get(endpoint)
        category_groups = response.json()["data"]["category_groups"]
        categories = []
        for category_group in category_groups:
            for category in category_group["categories"]:
                categories.append(category)
        return categories

    def get_budget_id_by_name(self, name: str) -> str:
        for budget in self._get_all_budgets():
            if budget["name"] == name:
                return budget["id"]
        raise YNABNotFoundError(name)

    def get_category_id_by_name(self, name: str, budget_id: str) -> str:
        for category in self._get_all_categories(budget_id=budget_id):
            if category["name"] == name:
                return category["id"]
        raise YNABNotFoundError(name)

    def find_in_budget_active_account_id_by_name(
        self, budget_id: str, account_name: str
    ) -> str:
        for budget in self._get_all_budgets():
            if budget["id"] != budget_id:
                continue
            for account in budget["accounts"]:
                if (
                    account["name"] == account_name
                    and account["deleted"] is False
                ):
                    return account["id"]
        raise YNABNotFoundError(account_name)

    def _create_transactions_request(self, budget_id: str, data: dict) -> dict:
        response = self._session.post(
            f"{self.API_HOST}/budgets/{budget_id}/transactions",
            json=data,
        )
        return response.json()

    def create_transaction(
        self, budget_id: str, transaction: YNABTransaction
    ) -> dict:
        data = {"transaction": json.loads(transaction.json())}
        return self._create_transactions_request(
            budget_id=budget_id, data=data
        )

    def create_multiple_transactions(
        self, budget_id: str, transactions: list[YNABSubTransaction]
    ) -> list[YNABSubTransaction]:
        data = {"transactions": [json.loads(t.json()) for t in transactions]}
        return self._create_transactions_request(
            budget_id=budget_id, data=data
        )
