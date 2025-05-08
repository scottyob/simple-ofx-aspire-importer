"""
Library to read OFX financial data
"""

import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from datetime import datetime
import pytz
from typing import List, Tuple
from ofxtools.Parser import OFXTree

from transactions import Transaction
AccountName = str


def to_transaction(record: ET.Element):
    transaction = Transaction()
    for e in record:
        if e.tag == "TRNTYPE":
            transaction.transaction_type = e.text
        elif e.tag == "DTPOSTED":
            transaction.date = _format_date(e.text)
        elif e.tag == "TRNAMT":
            transaction.amount = Decimal(e.text)
        elif e.tag == "FITID":
            transaction.id = e.text
        elif e.tag == "NAME":
            transaction.name = e.text
        elif e.tag == "MEMO":
            if e.text == "none":
                transaction.memo = None
            else:
                transaction.memo = e.text    

    if transaction.amount > 0:
        transaction.transaction_type = "CREDIT"
    transaction.amount = abs(transaction.amount)

    return transaction

def _format_date(original_string: str) -> str:
    # Original string
    # ... "20240104120000.000[0:GMT]"

    # Extract year, month, day from the original string
    year = int(original_string[:4])
    month = int(original_string[4:6])
    day = int(original_string[6:8])
    hours = int(original_string[8:10])
    minutes = int(original_string[10:12])
    seconds = int(original_string[12:14])

    # Create a datetime object
    dt_object = datetime(year, month, day, hours, minutes, seconds)

    # Define GMT time zone
    gmt = pytz.timezone("GMT")

    # Define GMT-7 time zone
    gmt_minus_7 = pytz.timezone("Etc/GMT+7")

    # Localize the datetime object to GMT
    dt_object_gmt = gmt.localize(dt_object)

    # Convert the datetime object to GMT-7
    dt_object_gmt_minus_7 = dt_object_gmt.astimezone(gmt_minus_7)

    # Format the datetime object to yyyy/mm/dd string
    return dt_object_gmt_minus_7.strftime("%Y/%m/%d")


def parse_file(filename: str) -> Tuple[List[Transaction], AccountName]:
    # Read the contents of the file into one big string
    parser = OFXTree()
    parser.parse(filename)

    tree = parser.getroot()
    transactions = tree.findall(".//STMTTRN")
    account_name = tree.find(".//ACCTID").text
    return ([
        to_transaction(t) for t in transactions
    ], account_name)


if __name__ == "__main__":
    transactions = parse_file(sys.argv[1])
    for t in transactions:
        print(t)