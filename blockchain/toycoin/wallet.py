"""Wallet for clients on the blockchain.
A wallet can hold coins (in the form of transactions), as well as send
and receive coins (again, by generating or processing transactions).
"""


from cryptography.hazmat.primitives.asymmetric import rsa # type: ignore
from toycoin import transaction # type: ignore
from typing import List, Optional, Tuple # type: ignore


################################################################################


class Wallet:
    """Wallet, initialized with owner's RSA keys."""


    def __init__(self,
                 public_key: bytes,
                 private_key: rsa.RSAPrivateKey):
        self.wallet : List[transaction.Token] = []
        self.pending : List[Tuple[bytes, transaction.Token]] = []
        self.public_key = public_key
        self.private_key = private_key


    def balance(self) -> int:
        """Return current wallet balance (exclude pending)."""
        return sum(token['value'] for token in self.wallet)


    def send(self,
             send_value: int,
             receiver: bytes
             ) -> Optional[transaction.Transaction]:
        """Attempt to generate transaction that sends value.
        Tokens included in the transaction are placed in pending state.
        """
        if send_value > self.balance():
            return []

        # FIFO
        sum_value, i = 0, 0
        while sum_value < send_value:
            sum_value += self.wallet[i]['value']
            i += 1

        txn = transaction.send(receiver,
                               self.public_key,
                               self.private_key,
                               send_value,
                               self.wallet[:i])

        self.pending.append((transaction.hash_txn(txn), self.wallet[:i]))
        self.wallet = self.wallet[i:]

        return txn


    def confirm_send(self, txn_hash: bytes):
        """Remove confirmed transaction from pending state."""
        self.pending = [(h, tokens) for h, tokens in self.pending
                        if h != txn_hash]


    def reject_send(self, txn_hash: bytes):
        """Return tokens to wallet from pending state."""
        pending = []
        for h, tokens in self.pending:
            if h == txn_hash:
                self.wallet = tokens + self.wallet
            else:
                pending.append((h, tokens))
        self.pending = pending


    def receive(self, txn: transaction.Transaction):
        """Add tokens to wallet."""
        if txn is None:
            return

        txn_hash = transaction.hash_txn(txn)
        if self.public_key == txn['receiver']:
            self.wallet.append({'txn_hash': txn_hash,
                                'owner': self.public_key,
                                'value': txn['receiver_value'],
                                'signature': txn['receiver_signature']})
        elif self.public_key == txn['sender']:
            self.wallet.append({'txn_hash': txn_hash,
                                'owner': self.public_key,
                                'value': txn['sender_change'],
                                'signature': txn['sender_signature']})

