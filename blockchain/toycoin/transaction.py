"""Construct and verify transactions and tokens.

Transactions consume and produce tokens, which are unique, immutable
stores of value that reference transactions from which they were
produced.
"""


from cryptography.hazmat.primitives.asymmetric import rsa # type: ignore
from toycoin import hash # type: ignore
from toycoin import signature, utils # type: ignore
from typing import List, Optional, TypedDict # type: ignore


################################################################################


Address = bytes


class Transaction(TypedDict):
    previous_hashes: List[hash.Hash]
    receiver: Address
    receiver_value: int
    receiver_signature: signature.Signature
    sender: Address
    sender_change: int
    sender_signature: signature.Signature


class Token(TypedDict):
    txn_hash: hash.Hash
    owner: Address
    value: int
    signature: signature.Signature


################################################################################
# Send


def send(receiver_pub: bytes,
         sender_pub: bytes,
         sender_priv: rsa.RSAPrivateKey,
         send_value: int,
         tokens: List[Token]
         ) -> Optional[Transaction]:
    """Generate a send transaction.
    Assumes token authenticity has been verified!
    Returns None if token value is insufficient, and provides change if
    token value is greater than the send value.
    """
    sum_value = sum_tokens(tokens)

    if sum_value < send_value:
        return None

    hs = [token['txn_hash'] for token in tokens]
    txn : Transaction
    txn = {'previous_hashes': hs,
           'receiver': receiver_pub,
           'receiver_value': send_value,
           'receiver_signature': signature.sign(sender_priv,
                                                b''.join(hs) + receiver_pub),
           'sender': sender_pub,
           'sender_change': sum_value - send_value,
           'sender_signature': signature.sign(sender_priv,
                                              b''.join(hs) + sender_pub)
           }

    return txn



################################################################################
# Validation


def valid_token(txn: Transaction, token: Token) -> bool:
    """Verify that token matches its parent transaction."""
    if token['owner'] == txn['receiver']:
        valid_val = token['value'] == txn['receiver_value']
        valid_sig = token['signature'] == txn['receiver_signature']
    else:
        valid_val = token['value'] == txn['sender_change']
        valid_sig = token['signature'] == txn['sender_signature']

    return (token['txn_hash'] == hash_txn(txn) and
            valid_val and
            valid_sig)


def valid_txn(tokens: List[Token], txn: Transaction) -> bool:
    """Validate transaction signatures."""
    owners = [token['owner'] for token in tokens]

    if len(set(owners)) > 1:
        return False

    owner = owners[0]
    hs = b''.join(txn['previous_hashes'])

    v1 = signature.verify(txn['receiver_signature'],
                          signature.load_pub_key_bytes(owner),
                          hs + txn['receiver'])
    v2 = signature.verify(txn['sender_signature'],
                          signature.load_pub_key_bytes(owner),
                          hs + txn['sender'])

    return v1 and v2


################################################################################
# Helpers


def sum_tokens(tokens: List[Token]) -> int:
    """Sum value of given Tokens."""
    return sum(token['value'] for token in tokens)


def hash_txn(txn: Transaction) -> hash.Hash:
    """Hash Transaction."""
    return hash.hash(b''.join(txn['previous_hashes']) +
                     txn['receiver'] +
                     utils.int_to_bytes(txn['receiver_value']) +
                     txn['receiver_signature'] +
                     txn['sender'] +
                     utils.int_to_bytes(txn['sender_change']) +
                     txn['sender_signature'])
