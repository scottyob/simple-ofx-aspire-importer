import re

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from jsoncomment import JsonComment

from typing import Literal, Optional, List, Tuple
from decimal import Decimal


# Type aliases
Category = str
CategoryMap = List[Tuple[re.Pattern, Category]]


def load_category_map(filename: str) -> CategoryMap:
    regexes_map = JsonComment().loadf(filename)
    if not regexes_map:
        return []
    return [(re.compile(k), v) for k, v in regexes_map.items()]


@dataclass
class Transaction:
    """
    A financial transaction
    """

    date: str = ""
    transaction_type: Literal["DEBIT", "CREDIT"] = "DEBIT"
    amount: Decimal = Decimal(0)
    id: str = ""
    name: str = ""
    account_name: str = ""
    memo: Optional[str] = None
    category: Optional[Category] = None

    def set_category(self, category_map: CategoryMap):
        for r, category in category_map:
            if r.search(self.name) or (self.memo and r.match(self.memo)):
                self.category = category
                return
    
    def __str__(self):
        outflow = ""
        inflow = ""

        if self.transaction_type == "CREDIT":
            inflow = f"${self.amount}"
        else:
            outflow = f"${self.amount}"

        return f"{self.date}\t{outflow}\t{inflow}\t{self.category}\t{self.account_name}\t{self.name}"


@dataclass_json
@dataclass
class TransactionLog:
    """
    A log of a transaction
    """

    date: str
    id: str

    @classmethod
    def from_transaction(cls, t: Transaction) -> Transaction:
        return TransactionLog(t.date, t.id)
