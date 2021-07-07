"""Construct and verify transactions.


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


class TransactionToken(TypedDict):
    txn_hash: hash.Hash
    holder: Address
    value: int
    signature: signature.Signature


################################################################################
# Send


def send(receiver_pub: bytes,
         sender_pub: bytes,
         sender_priv: rsa.RSAPrivateKey,
         send_value: int,
         tokens: List[TransactionToken]
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



################################################################################
# Helpers


def sum_tokens(tokens: List[TransactionToken]) -> int:
    """Sum value of given TrasnactionTokens."""
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
