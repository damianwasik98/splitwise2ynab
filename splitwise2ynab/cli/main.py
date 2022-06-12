import datetime
from pathlib import Path
from typing import Optional

import pydantic
import typer

import splitwise2ynab.cli.config as cli_config
from splitwise2ynab.cli.helpers import parse_groups_str
from splitwise2ynab.config import Splitwise2YNABConfig
from splitwise2ynab.main import main

app = typer.Typer(
    help="App which automates entering expenses from Splitwise to YNAB"
)
app.add_typer(cli_config.app, name="config")


@app.command()
def run(
    splitwise_expenses_after: Optional[datetime.datetime] = typer.Argument(
        (datetime.datetime.now()).strftime("%Y-%m-%d"),
        formats=["%Y-%m-%d"],
        help="Splitwise transactions with update date after provided date will be downloaded",
    ),
    ynab_budget_name: Optional[str] = typer.Option(None),
    ynab_splitwise_account_name: Optional[str] = typer.Option(None),
    ynab_splitwise_category_name: Optional[str] = typer.Option(None),
    splitwise_groups: Optional[str] = typer.Option(None),
    config_file: Optional[Path] = typer.Option(
        cli_config.default_config_file_path
    ),
):
    """Runs the script"""
    config_kwargs = {
        "YNAB_BUDGET_NAME": ynab_budget_name,
        "YNAB_SPLITWISE_ACCOUNT_NAME": ynab_splitwise_account_name,
        "YNAB_SPLITWISE_CATEGORY_NAME": ynab_splitwise_category_name,
        "SPLITWISE_GROUPS": parse_groups_str(splitwise_groups)
        if splitwise_groups
        else None,
    }
    config_kwargs = {k: v for k, v in config_kwargs.items() if v}
    try:
        config = Splitwise2YNABConfig(
            SPLITWISE_EXPENSES_AFTER=splitwise_expenses_after,
            **config_kwargs,
            _env_file=config_file,
        )
    except pydantic.error_wrappers.ValidationError as e:
        typer.echo(
            f'Missing config! Check your config file "{config_file}" for missing vars. \n{str(e)}'
        )
    else:
        typer.echo(f"Running the script with config {config}")
        try:
            main(config)
        except Exception as e:
            typer.echo(f"Script failed with error: {repr(e)}")
        else:
            typer.echo(f"Script finished succesfully 🥳")


def cli():
    app()


if __name__ == "__main__":
    cli()
