"""Construct blocks.
A block consists of a collection of transactions (of some limited number),
plus additional metadata in a header. Blocks are generated with proof-of-work.
"""

import math # type: ignore
from toycoin import hash, merkle, transaction, utils # type: ignore
from typing import List, Optional, Tuple, TypedDict # type: ignore


################################################################################


Transactions = List[transaction.Transaction]


class BlockHeader(TypedDict):
    timestamp: bytes
    previous_hash: hash.Hash
    nonce: bytes
    merkle_root: hash.Hash
    this_hash: hash.Hash


class Block(TypedDict):
    header: BlockHeader
    txns: Transactions


################################################################################
# Constructor


BLOCK_TXNS = 10 # magic number: max transactions per block


def gen_block(previous_hash: hash.Hash,
              txns: Transactions,
              difficulty: int
              ) -> Tuple[Optional[Block], Transactions]:
    """Attempt to generate a block from transactions.
    Return a block (or None if failure), and remainder transactions.
    """
    if not txns:
        return None, []

    txns_, rest = txns[:BLOCK_TXNS], txns[BLOCK_TXNS:]

    tree = gen_merkle(txns_)
    header = proof_of_work(previous_hash, tree.label, difficulty)
    block : Block = {'header': header,
                     'txns': txns_}

    return block, rest


def gen_merkle(txns: Transactions) -> merkle.MerkleTree:
    """Generate Merkle Tree given (non-empty) transactions."""
    tree = merkle.from_list(txns)
    assert tree is not None
    return tree


################################################################################
# Proof of Work


def next_difficulty(length: int) -> int:
    """Determine difficulty of next block, given length of current chain."""
    return 1 if length < 1 else 1 + int(math.log2(length))


def proof_of_work(p: hash.Hash,
                  root: hash.Hash,
                  difficulty: int
                  ) -> BlockHeader:
    """Naive POW solver."""
    now = utils.int_to_bytes(utils.timestamp())

    nonce = 0
    h = b''
    while not solved(h, difficulty):
        nonce += 1
        h = hash.hash(now + utils.int_to_bytes(nonce) + p + root)

    return {'timestamp': now,
            'previous_hash': p,
            'nonce': utils.int_to_bytes(nonce),
            'merkle_root': root,
            'this_hash': h}


def solved(h: hash.Hash, n: int) -> bool:
    """Check if first n bytes are zeros."""
    return h[:n] == bytes(n)


################################################################################
# Validation


def valid_header(header: BlockHeader) -> bool:
    """Check if header is valid."""
    h = hash.hash(header['timestamp'] +
                header['nonce'] +
                header['previous_hash'] +
                header['merkle_root'])

    return header['this_hash'] == h
