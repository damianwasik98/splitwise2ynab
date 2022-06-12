from splitwise2ynab.config import Splitwise2YNABConfig
from splitwise2ynab.splitwise.client import SplitwiseClient
from splitwise2ynab.splitwise.helpers import did_i_pay
from splitwise2ynab.splitwise.models import SplitwiseError
from splitwise2ynab.ynab.client import YNABClient
from splitwise2ynab.ynab.helpers import parse_decimal_to_ynab_amount
from splitwise2ynab.ynab.models import (
    ClearedEnum,
    ColorEnum,
    YNABSubTransaction,
    YNABTransaction,
)


def main(config: Splitwise2YNABConfig):
    ynab_client = YNABClient(api_key=config.YNAB_API_KEY.get_secret_value())
    budget_id = ynab_client.get_budget_id_by_name(name=config.YNAB_BUDGET_NAME)
    ynab_splitwise_account_id = (
        ynab_client.find_in_budget_active_account_id_by_name(
            budget_id=budget_id,
            account_name=config.YNAB_SPLITWISE_ACCOUNT_NAME,
        )
    )
    ynab_splitwise_category_id = ynab_client.get_category_id_by_name(
        name=config.YNAB_SPLITWISE_CATEGORY_NAME,
        budget_id=budget_id,
    )

    splitwise_client = SplitwiseClient(
        api_key=config.SPLITWISE_API_KEY.get_secret_value(),
        consumer_key=config.SPLITWISE_CONSUMER_KEY.get_secret_value(),
        consumer_secret=config.SPLITWISE_CONSUMER_SECRET.get_secret_value(),
    )
    current_user_id = splitwise_client.get_current_user_id()
    groups_ids = splitwise_client.get_groups_ids_from_names(
        config.SPLITWISE_GROUPS
    )

    for group_id in groups_ids:
        ynab_transactions_to_be_created = []

        splitwise_expenses = splitwise_client.generate_all_expenses(
            group_id=group_id, updated_after=config.SPLITWISE_EXPENSES_AFTER
        )
        for splitwise_expense in splitwise_expenses:
            if splitwise_expense.payment or splitwise_expense.deleted_at:
                continue

            try:
                current_user_participant = splitwise_expense.get_participant(
                    participant_id=current_user_id
                )
            except SplitwiseError:
                continue

            if did_i_pay(current_user_participant):
                continue
                # TODO: check if transaction already exists in ynab, match it and add splited splitwise category,
                # otherwise add a new unapproved transaction in Gotówka account without payee name and without category

                # ynab_transaction = YNABTransaction(
                #     account_id=ynab_splitwise_account_id,
                #     date=splitwise_expense.date,
                #     amount=parse_decimal_to_ynab_amount(splitwise_expense.cost),
                #     memo=splitwise_expense.description,
                #     payee_name=None,
                #     subtransactions=[],
                #     cleared="cleared"
                # )
            else:
                paid_participant = splitwise_expense.get_paid_participant()
                ynab_transaction = YNABTransaction(
                    account_id=ynab_splitwise_account_id,
                    date=splitwise_expense.date,
                    amount=0,
                    memo=splitwise_expense.description,
                    payee_name=paid_participant.fullname,
                    category_id=None,
                    subtransactions=[
                        YNABSubTransaction(
                            payee_name=paid_participant.fullname,
                            category_id=ynab_splitwise_category_id,
                            memo=splitwise_expense.description,
                            amount=parse_decimal_to_ynab_amount(
                                current_user_participant.owed
                            ),
                        ),
                        YNABSubTransaction(
                            payee_name=paid_participant.fullname,
                            category_id=None,
                            memo=splitwise_expense.description,
                            amount=-parse_decimal_to_ynab_amount(
                                current_user_participant.owed
                            ),
                        ),
                    ],
                    cleared=ClearedEnum.cleared,
                    flag_color=ColorEnum.red
                    if splitwise_expense.reciept_url
                    else None,
                )

            ynab_transactions_to_be_created.append(ynab_transaction)

        if len(ynab_transactions_to_be_created) > 0:
            ynab_client.create_multiple_transactions(
                budget_id=budget_id,
                transactions=ynab_transactions_to_be_created,
            )


if __name__ == "__main__":
    config = Splitwise2YNABConfig()
    main(config)
