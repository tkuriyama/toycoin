"""Helpers for converting objects sent over network to strings.
"""

from toycoin import block, transaction # type: ignore
from toycoin.network import serialize # type: ignore
from typing import List # type: ignore


################################################################################


def show_txn_pair(txn_pair: transaction.TxnPair) -> str:
    """Return string of transaction pair."""
    tokens, txn = txn_pair

    tokens_s = show_tokens(tokens)
    s1 = f'Tokens\n{tokens_s}'

    txn_s = serialize.pack_txn(txn, True, True)
    s2 = f'Transaction\n{txn_s}'

    return f'\n{"-" * 80}\n{s1}\n\n{s2}'


def show_tokens(tokens: List[transaction.Token]) -> str:
    """Return string of tokens."""
    return '\n'.join(serialize.pack_token(token, True, True)
                     for token in tokens)


################################################################################


def show_blockchain(chain: block.Blockchain) -> str:
    """Return string of blockchain."""
    txn_count = sum(len(b['txns']) for b in chain)
    valid = block.valid_blockchain(chain)
    stats = f'Blocks: {len(chain)} | Total Txns: {txn_count} | Valid: {valid}'

    s = f'\n{"-" * 80}\nBlockchain\n{stats}\n'

    for i, b in enumerate(chain):
        hdr_s = serialize.pack_block_header(b['header'], True, True)
        txn_hashes_s = show_txn_hashes(b['txns'])
        s += f'\nBlock {i} Header:\n{hdr_s}'
        s += f'\nTxns Hashes:\n{txn_hashes_s}'

    return s


def show_txn_hashes(txns: List[transaction.Transaction]) -> str:
    """Return string of (previous hashes -> this hash) for txn."""
    b2s = serialize.get_b2s(True)

    prev_to_str = lambda hs: ', '.join(f'{b2s(h)}' for h in hs)
    this_to_str = lambda t: f'{b2s(transaction.hash_txn(t))}'

    s = '\n'.join(f'{prev_to_str(txn["previous_hashes"])} -> {this_to_str(txn)}'
                  for txn in txns)

    return s
