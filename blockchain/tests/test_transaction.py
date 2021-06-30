
from toycoin import signature, transaction # type: ignore


################################################################################


class TestTransaction:

    def test_chain(self):
        """Test chain of transactions."""

        a_priv, b_priv = signature.gen_priv_key(), signature.gen_priv_key()
        c_priv, d_priv = signature.gen_priv_key(), signature.gen_priv_key()

        txn0 = {'receiver': signature.get_pub_key_bytes(a_priv),
                'amount': 100.0,
                'signature': b'genesis_signature'
                }

        txn1 = transaction.send(signature.get_pub_key_bytes(b_priv),
                                a_priv,
                                99.0,
                                txn0)
        txn2 = transaction.send(signature.get_pub_key_bytes(c_priv),
                                b_priv,
                                99.0,
                                txn1)
        txn3 = transaction.send(signature.get_pub_key_bytes(d_priv),
                                c_priv,
                                98.0,
                                txn2)

        # undecidable
        assert transaction.valid([]) is None
        assert transaction.valid([txn0]) is None

        # chain
        assert transaction.valid([txn0, txn1, txn2, txn3])
