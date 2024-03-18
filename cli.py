#!/usr/bin/env python

from typing import Dict
import click
import ofx
import json

from transactions import TransactionLog, load_category_map
from colorama import init, Fore


def _to_account_name(account_map: Dict[str, str], account_id: str) -> str:
    for k, v in account_map.items():
        if account_id.endswith(k):
            return v
    return account_id


@click.command()
@click.argument("filename")
@click.option(
    "--processed-filename",
    help="Specify the processed filename.",
    default="data/processed.json",
)
@click.option(
    "-w", "--update-processed-file",
    is_flag=True,
    help="Flag to update processed file.",
)
@click.option(
    "--categories-filename",
    help="Filename to load the categories JSON file from",
    default="data/categories.jsonc",
)
@click.option(
    "--accounts-filename",
    help="The JSON file containing a map of account ID suffixes to their Aspire account name",
    default="data/accounts.json",
)
@click.option(
    "--debug",
    help="Debug mode",
    is_flag=True,
    default=False
)
def process(
    filename: str,
    processed_filename,
    update_processed_file,
    categories_filename,
    accounts_filename,
    debug: bool,
):
    """
    Process the given filename.
    """

    # Keep a log of the transactions that have been processed
    processed_log = {}
    category_map = load_category_map(categories_filename)

    # Load in the accounts map
    # Filename is a map of account ID suffix to Aspire account name
    with open(accounts_filename) as f:
        accounts_map: Dict[str, str] = json.load(f)

    # Build a list of transactions based on the file type
    transactions = []
    account_name = "UNKNOWN"
    if filename.endswith(".ofx"):
        transactions, acct = ofx.parse_file(filename)
        account_name = _to_account_name(accounts_map, acct) or acct

    # Update the log of items that have been processed
    if processed_filename:
        with open(processed_filename) as f:
            for i in json.load(f):
                log_entry = TransactionLog(**i)
                processed_log[log_entry.id] = log_entry

    # Strip out any recods from the file that have already been processed
    transactions = [t for t in transactions if t.id not in processed_log]

    # Set the categories
    for t in transactions:
        t.set_category(category_map)
        t.account_name = account_name

    # Process every new transaction
    for t in transactions:
        repr = str(t)
        if debug:
            repr = t.__repr__()
        if not t.category:
            print(Fore.RED + repr + Fore.RESET)
        else:
            print(repr)
        processed_log[t.id] = TransactionLog.from_transaction(t)

    # Update the transaction logfile
    if update_processed_file:
        with open(processed_filename, "w") as f:
            json.dump([t.to_dict() for t in processed_log.values()], f)


if __name__ == "__main__":
    process()
