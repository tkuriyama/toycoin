"""Test wallet (and transactions).
"""


from toycoin import transaction, wallet, signature # type: ignore


################################################################################


class TestWallet:

    def test_send_receive(self):
        """Test sending and receiving tokens via transactions."""
        a_wallet, b_wallet = gen_wallet(), gen_wallet()
        c_wallet, d_wallet = gen_wallet(), gen_wallet()

        txn0a = {'previous_hashes': [],
                 'receiver': a_wallet.public_key,
                 'receiver_value': 100,
                 'receiver_signature': b'',
                 'sender': b'genesis',
                 'sender_change': 0,
                 'sender_signature': b''
                 }
        txn0b = {'previous_hashes': [],
                 'receiver': a_wallet.public_key,
                 'receiver_value': 50,
                 'receiver_signature': b'',
                 'sender': b'genesis',
                 'sender_change': 0,
                 'sender_signature': b''
                 }

        # genesis receive (the genesis txn is not valid)
        assert transaction.valid_txn([], txn0a) is False
        assert transaction.valid_txn([], txn0b) is False

        assert a_wallet.balance() == 0
        a_wallet.receive(txn0a)
        assert a_wallet.balance() == 100

        a_wallet.receive(txn0b)
        assert a_wallet.balance() == 150

        assert transaction.valid_token(txn0a, a_wallet.wallet[0])
        assert transaction.valid_token(txn0b, a_wallet.wallet[1])

        # cannot send more than wallet total
        assert a_wallet.send(200, b_wallet.public_key) is None

        # A sends first token to B, with 50 in change (txn pending)
        _, txn1 = a_wallet.send(50, b_wallet.public_key)
        assert a_wallet.balance() == 50

        # rejecting the send restores A wallet
        assert len(a_wallet.pending) == 1
        a_wallet.reject_send(transaction.hash_txn(txn1))
        assert a_wallet.balance() == 150
        assert len(a_wallet.wallet) == 2
        assert len(a_wallet.pending) == 0

        # send again and confirm for A and B
        _, txn1 = a_wallet.send(50, b_wallet.public_key)

        a_wallet.confirm_send(transaction.hash_txn(txn1))
        assert a_wallet.balance() == 50
        assert a_wallet.pending == []
        a_wallet.receive(txn1)
        assert a_wallet.balance() == 100

        b_wallet.receive(txn1)
        assert b_wallet.balance() == 50

        # can't receive if you're not the recipient
        c_wallet.receive(txn1)
        assert c_wallet.balance() == 0

        # now let's send two tokens from A to C
        tokens2, txn2 = a_wallet.send(100, c_wallet.public_key)
        assert transaction.valid_txn(tokens2, txn2)

        assert a_wallet.balance() == 0
        a_wallet.confirm_send(transaction.hash_txn(txn2))
        assert a_wallet.balance() == 0

        c_wallet.receive(txn2)
        assert c_wallet.balance() == 100

        # now C sends to D
        tokens3, txn3 = c_wallet.send(100, d_wallet.public_key)

        # verify tokens and transations are valid
        for token in tokens3:
            assert transaction.valid_token(txn2, token)
        for token in tokens2:
            assert transaction.valid_token(txn2, token) is False

        assert transaction.valid_txn(tokens3, txn3)
        assert transaction.valid_txn(tokens2, txn3) is False

        # the balances are correct after wallets are updated
        c_wallet.confirm_send(transaction.hash_txn(txn3))
        d_wallet.receive(txn3)

        assert a_wallet.balance() == 0
        assert b_wallet.balance() == 50
        assert c_wallet.balance() == 0
        assert d_wallet.balance() == 100


        # finally let's send from B to D
        tokens4, txn4 = b_wallet.send(20, d_wallet.public_key)
        assert transaction.valid_txn(tokens4, txn4)

        # the balances are correct after wallets are updated
        b_wallet.confirm_send(transaction.hash_txn(txn4))
        b_wallet.receive(txn4)
        d_wallet.receive(txn4)

        assert a_wallet.balance() == 0
        assert b_wallet.balance() == 30
        assert c_wallet.balance() == 0
        assert d_wallet.balance() == 120


################################################################################
# Helpers


def gen_wallet() -> wallet.Wallet:
    """Generate wallet."""
    priv_key = signature.gen_priv_key()
    pub_key = signature.get_pub_key_bytes(priv_key)
    return wallet.Wallet(pub_key, priv_key)
