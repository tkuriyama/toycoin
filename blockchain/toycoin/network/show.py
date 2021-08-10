"""Helpers for converting objects sent over network to strings.
"""

from toycoin import block, transaction # type: ignore
from toycoin.network import serialize # type: ignore


################################################################################


def show_txn_pair(txn_pair: transaction.TxnPair) -> str:
    """Return stringoof transaction pair."""
    tokens, txn = txn_pair

    tokens = '\n'.join(serialize.pack_token(token, True, True)
                       for token in tokens)
    s1 = f'Tokens\n{tokens}'

    txn_ = serialize.pack_txn(txn, True, True)
    s2 = f'Transaction\n{txn_}'

    return f'\n{"-" * 80}\n{s1}\n\n{s2}'
