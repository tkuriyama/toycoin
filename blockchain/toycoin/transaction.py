"""Construct and verify transactions.
Logically, a transaction is a transfer of some positive amount from A to B,
signed by A. No mechanisms for providing change is implemented.
"""


from cryptography.hazmat.primitives.asymmetric import rsa # type: ignore
from toycoin import hash # type: ignore
from toycoin import signature # type: ignore
from typing import List, Optional, TypedDict # type: ignore


################################################################################


Address = bytes
Hash = bytes

class Transaction(TypedDict):
    sender: Address
    receiver: Address
    amount: float
    signature: signature.Signature


################################################################################
# Transactions


def send(receiver: bytes,
         sender: rsa.RSAPrivateKey,
         amount: float,
         previous_txn: Transaction
         ) -> Transaction:
    """Generate a new transaction."""
    h = hash_txn(previous_txn)
    return {'sender': signature.get_pub_key_bytes(sender),
            'receiver': receiver,
            'amount': amount,
            'signature': signature.sign(sender, h + receiver)}


def valid(txns: List[Transaction]) -> Optional[bool]:
    """Verify signatures of a list of transactions."""
    if len(txns) <= 1:
        return None

    pairs = zip(txns, txns[1:])
    return all(valid_pair(prev, this) for prev, this in pairs)


def valid_pair(previous: Transaction, this: Transaction) -> bool:
    """Verify signature of one transaction."""
    return signature.verify(this['signature'],
                            signature.load_pub_key_bytes(previous['receiver']),
                            hash_txn(previous) + this['receiver'])


################################################################################
# Helpers


def hash_txn(txn: Transaction) -> Hash:
    """Hash Transaction."""
    return hash.hash(txn['sender'] +
                     txn['receiver'] +
                     bytes(str(txn['amount']).encode('utf-8')) +
                     txn['signature'])
