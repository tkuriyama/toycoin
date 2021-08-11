"""Construct blocks.
A block consists of a collection of transactions (of some limited number),
plus additional metadata in a header. Blocks are generated with a proof-of-work
hash.
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


Blockchain = List[Block]


################################################################################
# Constructor


GENESIS = hash.hash(b'genesis') # genesis block previous hash
BLOCK_MAX_TXNS = 10 # magic number: max transactions per block


def gen_block(previous_hash: hash.Hash,
              txns: Transactions,
              difficulty: int
              ) -> Tuple[Optional[Block], Transactions]:
    """Attempt to generate a block from transactions.
    Return a block (or None if failure), and remainder transactions.
    """
    if not txns:
        return None, []

    txns_, rest = txns[:BLOCK_MAX_TXNS], txns[BLOCK_MAX_TXNS:]

    tree = gen_merkle(txns_)
    header = proof_of_work(previous_hash, tree.label, difficulty)
    block : Block = {'header': header,
                     'txns': txns_}

    return block, rest


def gen_merkle(txns: Transactions) -> merkle.MerkleTree:
    """Generate Merkle Tree given (non-empty) transactions."""
    tree = merkle.from_list([transaction.hash_txn(txn) for txn in txns])
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
        h = hash.hash(now + p + utils.int_to_bytes(nonce) + root)

    return {'timestamp': now,
            'previous_hash': p,
            'nonce': utils.int_to_bytes(nonce),
            'merkle_root': root,
            'this_hash': h}


def solved(h: hash.Hash, n: int) -> bool:
    """Check if first n bytes are zeros."""
    return h[:n] == bytes(n)


################################################################################
# Block Validation


def valid_blockchain(chain: Blockchain) -> bool:
    """Check validity of blockchain."""
    pairs = zip(chain[1:], chain)
    v1 = all(valid_hash_pair(b1, b0) for b1, b0 in pairs)

    v2 = all(valid_block(block, next_difficulty(i))
             for i, block in enumerate(chain))

    v3 = chain[0]['header']['previous_hash'] == GENESIS

    v4 = all(valid_timestamp(b1, b0) for b1, b0 in pairs)

    return v1 and v2 and v3 and v4


def valid_block(block: Block, difficulty: int) -> bool:
    """Check if block transactions and header hashes are valid."""
    tree = gen_merkle(block['txns'])
    return (valid_header(block['header'], difficulty) and
            tree.label == block['header']['merkle_root'])


def valid_header(header: BlockHeader, difficulty: int) -> bool:
    """Check if block hash matches header data."""
    h = hash.hash(header['timestamp'] +
                  header['previous_hash'] +
                  header['nonce'] +
                  header['merkle_root'])
    return (header['this_hash'] == h and
            solved(header['this_hash'], difficulty))


def valid_hash_pair(b1: Block, b0: Block) -> bool:
    """B1 previous hash matches B0 hash."""
    return b1['header']['previous_hash'] == b0['header']['this_hash']


def valid_timestamp(b1: Block, b0: Block) -> bool:
    """B1 has later timestmap than B0."""
    return b1['header']['timestamp'] > b0['header']['timestamp']


# Token & Blockchain Validation


def valid_tokens(tokens: List[transaction.Token], chain: Blockchain) -> bool:
    """Tokens are unique and all come from prior txns in the blockchain."""
    # backdoor for coinbase tokens
    return (transaction.unique_tokens(tokens) and
            all(valid_token(token, chain) for token in tokens))


def valid_token(token: transaction.Token, chain: Blockchain):
    """Search blockchain backwards for txn source of token."""
    for block in chain[::-1]:
        txns = block['txns']
        for txn in txns:
            if transaction.valid_token(txn, token):
                return True

    return False
