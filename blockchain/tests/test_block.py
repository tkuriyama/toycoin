
from toycoin import block, hash, signature, transaction, utils, wallet # type: ignore


################################################################################

class TestGenBlock:


    def test_empty_block(self):
        """Test gen_block with no transactions."""
        f = block.gen_block

        assert f(hash.hash(b'previous'), [], 1) == (None, [])


    def test_gen_block(self):
        """Test block gen with some transactions."""
        """Test sending and receiving tokens via transactions."""

        # genesis transactions and block
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

        a_wallet.receive(txn0a)
        a_wallet.receive(txn0b)

        b0, _ = block.gen_block(block.GENESIS,
                                [txn0a, txn0b],
                                block.next_difficulty(0))

        b0_, _ = block.gen_block(block.GENESIS + b'1',
                                 [txn0a, txn0b],
                                 block.next_difficulty(0))

        assert block.valid_block(b0, block.next_difficulty(0))
        assert block.valid_blockchain([b0])
        assert block.valid_blockchain([b0_]) is False


        # some more transactions and next blocks

        _, txn1 = a_wallet.send(10, b_wallet.public_key)
        _, txn2 = a_wallet.send(10, c_wallet.public_key)
        txn3_fail = a_wallet.send(10, d_wallet.public_key)
        assert txn3_fail is None # cannot send tokens we don't have

        b1, _ = block.gen_block(b0['header']['this_hash'],
                                [txn1, txn2],
                                block.next_difficulty(1))

        a_wallet.confirm_send(transaction.hash_txn(txn1))
        a_wallet.confirm_send(transaction.hash_txn(txn2))

        a_wallet.receive(txn1)
        b_wallet.receive(txn1)
        a_wallet.receive(txn2)
        c_wallet.receive(txn2)

        assert block.valid_block(b1, block.next_difficulty(1))
        assert block.valid_blockchain([b0, b1])
        assert block.valid_blockchain([b1, b0]) is False


        # we have change now, so A can send token to D
        _, txn3 = a_wallet.send(10, d_wallet.public_key)
        b2, _ = block.gen_block(b1['header']['this_hash'],
                                [txn3],
                                block.next_difficulty(2))

        a_wallet.confirm_send(transaction.hash_txn(txn3))
        a_wallet.receive(txn3)
        d_wallet.receive(txn3)

        assert block.valid_block(b2, block.next_difficulty(2))
        assert block.valid_blockchain([b0, b1, b2])
        assert block.valid_blockchain([b1, b0, b2]) is False



class TestProofOfWork:


    def test_next_difficulty(self):
        """Test next_difficulty"""
        f = block.next_difficulty

        assert f(0) == 1
        assert f(1) == 1
        assert f(2) == 2


    def test_proof_of_work(self):
        """Test proof of work"""
        f = block.proof_of_work

        previous = hash.hash(b'hello world')
        root = hash.hash(b'root')

        b = f(previous, root, 2)

        assert b['previous_hash'] == previous
        assert b['merkle_root'] == root
        assert b['this_hash'][:2] == b'\x00\x00'
        # processing time should be easily < 60 seconds
        assert abs(int(b['timestamp']) - utils.timestamp()) < 60
        assert block.valid_header(b, 2)


    def test_solved(self):
        """Test solved"""
        f = block.solved

        assert f(b'\x01\x02', 0) is True
        assert f(b'\x01\x02', 1) is False

        assert f(b'\x00\x00\x01\x02', 1) is True
        assert f(b'\x00\x00\x01\x02', 2) is True
        assert f(b'\x00\x00\x01\x02', 3) is False


################################################################################
# Helpers


def gen_wallet() -> wallet.Wallet:
    """Generate wallet."""
    priv_key = signature.gen_priv_key()
    pub_key = signature.get_pub_key_bytes(priv_key)
    return wallet.Wallet(pub_key, priv_key)
