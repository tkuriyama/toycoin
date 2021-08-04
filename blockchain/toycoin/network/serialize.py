"""De/serialization of toycoin data structures.
Mainly converting bytes to and from b64, and using JSON functions.
"""

import base64 # type: ignore
import json # type: ignore
from toycoin import transaction # type: ignore
from typing import List, Tuple # type: ignore


################################################################################
# Token

def pack_token(token: transaction.Token) -> str:
    """Pack token to JSON string with b64 for bytes."""
    token_ = {'txn_hash': b2s(token['txn_hash']),
              'owner': b2s(token['owner']),
              'value': token['value'],
              'signature': b2s(token['signature'])
              }
    return json.dumps(token_)


def unpack_token(s: str) -> transaction.Token:
    """Unpack token from JSON string with b64 for bytes."""
    token = json.loads(s)
    return {'txn_hash': s2b(token['txn_hash']),
              'owner': s2b(token['owner']),
              'value': token['value'],
              'signature': s2b(token['signature'])
              }


################################################################################
# Transaction

def pack_txn(txn: transaction.Transaction) -> str:
    """Pack txn to JSON string with b64 for bytes."""
    txn_ = {'previous_hashes': [b2s(h) for h in
                                txn['previous_hashes']],
            'receiver': b2s(txn['receiver']),
            'receiver_value': txn['receiver_value'],
            'receiver_signature': b2s(txn['receiver_signature']),
            'sender': b2s(txn['sender']),
            'sender_change': txn['sender_change'],
            'sender_signature': b2s(txn['sender_signature'])
            }
    return json.dumps(txn_)


def unpack_txn(s: str) -> transaction.Transaction:
    """Unpack txn from JSON string with b64 for bytes."""
    txn = json.loads(s)
    return {'previous_hashes': [s2b(h) for h in
                                txn['previous_hashes']],
            'receiver': s2b(txn['receiver']),
            'receiver_value': txn['receiver_value'],
            'receiver_signature': s2b(txn['receiver_signature']),
            'sender': s2b(txn['sender']),
            'sender_change': txn['sender_change'],
            'sender_signature': s2b(txn['sender_signature'])
            }


################################################################################
# Token & Transaction Pairs

Pair = Tuple[List[transaction.Token], transaction.Transaction]

def pack_txn_pairs(pairs: List[Pair]) -> str:
    """Pack (tokens, transaction) pairs."""
    pairs = [([pack_token(token) for token in tokens], pack_txn(txn))
             for tokens, txn in pairs]
    return json.dumps(pairs)

def unpack_txn_pairs(s: str) -> List[Pair]:
    """Unpack (tokens, transacion) pairs."""
    pairs = json.loads(s)
    return [([unpack_token(token) for token in tokens], unpack_txn(txn))
            for tokens, txn in pairs]



################################################################################
# Helpers


def b2s(bs: bytes) -> str:
    """Bytes to b64 string."""
    return base64.b64encode(bs).decode('utf-8')


def s2b(s: str) -> bytes:
    """b64 string to bytes."""
    return base64.b64decode(s)
