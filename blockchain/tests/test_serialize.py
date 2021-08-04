"""Test de/serialization.
"""

from toycoin.network import serialize # type: ignore

################################################################################


txn0a = {'previous_hashes': [b'0', b'1'],
         'receiver': b'receiver_public',
         'receiver_value': 100,
         'receiver_signature': b'receiver_signature',
         'sender': b'genesis',
         'sender_change': 0,
         'sender_signature': b'sender_signature'
         }


txn0b = {'previous_hashes': [b'2'],
         'receiver': b'receiver2_public',
         'receiver_value': 50,
         'receiver_signature': b'receiver2_signature',
         'sender': b'genesis',
         'sender_change': 0,
         'sender_signature': b'sender2_signature'
         }

token = {'txn_hash': b'random hash',
         'owner': b'some owner',
         'value': 100,
         'signature': b'some signature'
         }


################################################################################

class TestSerialize:

    def test_pack_unpack_token(self):
        """Test round trip pack and unpack for token."""
        f = serialize.pack_token
        g = serialize.unpack_token

        assert g(f(token)) == token


    def test_pack_unpack_txn(self):
        """Test round trip pack and unpack for txn."""

        f = serialize.pack_txn
        g = serialize.unpack_txn

        assert g(f(txn0a)) == txn0a
        assert g(f(txn0b)) == txn0b
        assert g(f(txn0a)) != txn0b
