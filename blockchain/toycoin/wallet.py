"""The chain global wallet.
The chain global wallet represents all valid coin holders and their coin
balances.
"""


from toycoin import transaction # type: ignore
from typing import Dict # type: ignore


################################################################################


Wallet = Dict[bytes, float]


################################################################################


def apply(wallet: Wallet, txns: List[transaction.Transaction]) -> Wallet
    """Apply zero or more transactions to wallet.
    By design, no validation is performed here.
    """
    for txn in txns:
        receiver = txn['receiver']
        if receiver in wallet:
            wallet[receiver] += txn['amount']
        else:
            wallet[receiver] = txn['amount']

    return wallet
