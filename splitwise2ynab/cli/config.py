import os
import subprocess
from pathlib import Path
from typing import Optional

import typer

from splitwise2ynab.cli.helpers import parse_groups_str

app = typer.Typer(help="Configuration of the script")


default_config_file_path: Path = (
    f"{Path.home()}/.config/splitwise2ynab/config.env"
)


@app.command()
def init(config_file: Optional[Path] = typer.Option(default_config_file_path)):
    """Initializes first run and script configuration"""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.touch(exist_ok=True)

    typer.echo("Providing authorization details of Splitwise account...")
    SPLITWISE_API_KEY: str = typer.prompt("Type your Splitwise API Key")
    SPLITWISE_CONSUMER_KEY: str = typer.prompt(
        "Type your Splitwise Consumer Key"
    )
    SPLITWISE_CONSUMER_SECRET: str = typer.prompt(
        "Type your Splitwise Consumer Secret"
    )
    SPLITWISE_GROUPS: list[str] = typer.prompt(
        'Type list of Splitwise groups from which script should download expenses (seperated by ",")',
        value_proc=parse_groups_str,
    )

    typer.echo("Providing authorization details of YNAB account...")
    YNAB_API_KEY: str = typer.prompt("Type your YNAB API key")
    YNAB_BUDGET_NAME: str = typer.prompt("Type your YNAB budget name")
    YNAB_SPLITWISE_ACCOUNT_NAME: str = typer.prompt(
        "Type your YNAB account name for splitwise transactions (create it on YNAB app first if u don't have one)"
    )
    YNAB_SPLITWISE_CATEGORY_NAME: str = typer.prompt(
        "Type your YNAB category name for splitwise transactions (create it on YNAB app first if u don't have one)"
    )

    lines = [
        f"SPLITWISE_API_KEY = {SPLITWISE_API_KEY}\n",
        f"SPLITWISE_CONSUMER_KEY = {SPLITWISE_CONSUMER_KEY}\n",
        f"SPLITWISE_CONSUMER_SECRET = {SPLITWISE_CONSUMER_SECRET}\n",
        f"SPLITWISE_GROUPS = {SPLITWISE_GROUPS}\n",
        f"YNAB_API_KEY = {YNAB_API_KEY}\n",
        f"YNAB_BUDGET_NAME = {YNAB_BUDGET_NAME}\n",
        f"YNAB_SPLITWISE_ACCOUNT_NAME = {YNAB_SPLITWISE_ACCOUNT_NAME}\n",
        f"YNAB_SPLITWISE_CATEGORY_NAME = {YNAB_SPLITWISE_CATEGORY_NAME}\n",
    ]
    with open(config_file, "w") as f:
        f.writelines(lines)

    typer.echo(f'Successfully writed configuration to file: "{config_file}"')


@app.command()
def show(config_file: Optional[Path] = typer.Option(default_config_file_path)):
    """Show current configuration"""
    with open(config_file, "r") as f:
        file_content = f.read()

    typer.echo(file_content)


@app.command()
def edit(config_file: Optional[Path] = typer.Option(default_config_file_path)):
    """Interactively edit configuration file"""

    editor = os.environ.get("EDITOR", "nano")
    result = subprocess.run([editor, config_file])
    if result.returncode == 0:
        typer.echo(f'Succesfully edited config file "{config_file}"')
    else:
        typer.echo(f'Failed on editing config file "{config_file}"')
