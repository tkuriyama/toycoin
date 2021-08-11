"""De/serialization of toycoin data structures.
Mainly converting bytes to and from b64, and using JSON functions.
"""

import base64 # type: ignore
import json # type: ignore
from toycoin import block, transaction # type: ignore
from typing import List, Tuple # type: ignore


################################################################################
# Token

def pack_token(token: transaction.Token,
               abbrev: bool = False,
               pretty: bool = False
               ) -> str:
    """Pack token to JSON string with b64 for bytes."""
    f = get_b2s(abbrev)
    token_ = {'txn_hash': f(token['txn_hash']),
              'owner': f(token['owner']),
              'value': token['value'],
              'signature': f(token['signature'])
              }
    return json_dumps(token_, pretty)


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

def pack_txn(txn: transaction.Transaction,
             abbrev: bool = False,
             pretty: bool  = False
             ) -> str:
    """Pack txn to JSON string with b64 for bytes."""
    f = get_b2s(abbrev)
    txn_ = {'previous_hashes': [f(h) for h in
                                txn['previous_hashes']],
            'receiver': f(txn['receiver']),
            'receiver_value': txn['receiver_value'],
            'receiver_signature': f(txn['receiver_signature']),
            'sender': f(txn['sender']),
            'sender_change': txn['sender_change'],
            'sender_signature': f(txn['sender_signature'])
            }
    return json_dumps(txn_, pretty)


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

TxnPair = Tuple[List[transaction.Token], transaction.Transaction]

def pack_txn_pair(pair: TxnPair) -> str:
    """Pack (tokens, transaction) pair."""
    tokens, txn = pair
    pair = ([pack_token(token) for token in tokens], pack_txn(txn))
    return json.dumps(pair)

def unpack_txn_pair(s: str) -> TxnPair:
    """Unpack (tokens, transacion) pair."""
    tokens, txn = json.loads(s)
    return ([unpack_token(token) for token in tokens], unpack_txn(txn))


################################################################################
# Blocks


def pack_blockchain(blocks: block.Blockchain,
                    abbrev: bool = False,
                    pretty: bool = False) -> str:
    """Pack blockchain to JSON string with b64 for bytes."""
    blocks_ = [_pack_block(block, abbrev, pretty) for
               block in blocks]
    return json_dumps(blocks_, pretty)


def _pack_block(block: block.Block,
               abbrev: bool = False,
               pretty: bool = False,
               skip_pack: bool = True
               ) -> str:
    """Pack blockchain to JSON string with b64 for bytes."""
    f = get_b2s(abbrev)
    hdr, txns = block['header'], block['txns']
    hdr_ = {'timestamp': f(hdr['timestamp']),
            'previous_hash': f(hdr['previous_hash']),
            'nonce': f(hdr['nonce']),
            'merkle_root': f(hdr['merkle_root']),
            'this_hash': f(hdr['this_hash'])
            }
    txns_ = [pack_txn(txn) for txn in txns]
    return json.dumps({'header': hdr_, 'txns': txns_})


def unpack_blockchain(s: str) -> block.Blockchain:
    """Unapck blockchain from JSON string with b64 for bytes."""
    blocks = json.loads(s)
    return [_unpack_block(block) for block in blocks]


def _unpack_block(s: str) -> block.Block:
    """Unpack block from JSON string with b64 for bytes."""
    block = json.loads(s)
    hdr, txns = block['header'], block['txns']
    return {'header': {'timestamp': s2b(hdr['timestamp']),
                       'previous_hash': s2b(hdr['previous_hash']),
                       'nonce': s2b(hdr['nonce']),
                       'merkle_root': s2b(hdr['merkle_root']),
                       'this_hash': s2b(hdr['this_hash'])
                       },
            'txns': [unpack_txn(txn) for txn in txns]
            }


################################################################################
# Helpers


def b2s(bs: bytes) -> str:
    """Bytes to b64 string."""
    return base64.b64encode(bs).decode('utf-8')


def s2b(s: str) -> bytes:
    """b64 string to bytes."""
    return base64.b64decode(s)


def get_b2s(abbrev: bool):
    """Bytes to string function, optioanlly abbreviating output."""
    return b2s if not abbrev else lambda x: b2s(x)[:10] + '...'


def json_dumps(obj, pretty: bool) -> str:
    """Generate JSON, optionally with pretty printing."""
    return (json.dumps(obj) if not pretty else
            json.dumps(obj, indent=4, sort_keys=True))
