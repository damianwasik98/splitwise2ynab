import datetime
from typing import List

from pydantic import BaseSettings, SecretStr


class Splitwise2YNABConfig(BaseSettings):
    SPLITWISE_API_KEY: SecretStr
    SPLITWISE_CONSUMER_KEY: SecretStr
    SPLITWISE_CONSUMER_SECRET: SecretStr
    SPLITWISE_EXPENSES_AFTER: datetime.date
    SPLITWISE_GROUPS: List[str]
    YNAB_API_KEY: SecretStr
    YNAB_BUDGET_NAME: str
    YNAB_SPLITWISE_ACCOUNT_NAME: str
    YNAB_SPLITWISE_CATEGORY_NAME: str

    class Config:
        env_file = ".env"
