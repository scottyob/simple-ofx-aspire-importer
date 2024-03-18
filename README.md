Simple OFX Aspire Importer is a (very) simple Python script that's intent is to make it simpler to parse [OFX files](https://docs.fileformat.com/finance/ofx/) and spit out to the console transactions that be easily copied/pasted into [Aspire Budgeting](https://aspirebudget.com/).

## Features
**Processed Log:** keeps track of transaction IDs that have been processed, meaning you can have duplicate transaction entries in the OFX files, and the transactions with the IDs that have been already processed should be skipped over.  Using the "-w" (or "--update-processed-file") flag will append processed entries to this file.

**Accounts Map:** Maps some account suffix to the human readable account name in your Aspire spreadsheet.

**Categories.jsonc** Is a map of a substring (or regex really) to the Aspire category name.

## Setting Up
1. Create your virtual environment, install the dependencies
```
python3 -m venv env
pip install -r requirements.txt
```

2. Setup the data directory
```
mkdir data
```

Files should look something like:

*data/accounts.json*:
```
{
    "1234": "Account 1",
    "-e1a": "Some Credit Card"
}
```

*data/categories.jsonc*:
```
{
    "SAFEWAY": "Groceries",
    "COMCAST": "Telecom",
}
```

*data/processed.json*:
```
[]
```

NOTE:  expect data/processed.json to be populated as this is ran.

## Guide
Typically running this script is as simple as activating the virtualenv, then running it on an ofx file.

```
. ./env/bin/activate
./cli.py -w ~/Downloads/someOfxFile.ofx
```

Running without the -w option, will NOT update the processed.json log, useful for bulk updating categories before updating the log.

Items in RED will show transactions that don't have a bulk category match.