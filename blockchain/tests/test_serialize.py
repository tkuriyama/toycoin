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

token1 = {'txn_hash': b'random hash',
         'owner': b'some owner',
         'value': 100,
         'signature': b'some signature'
          }

token2 = {'txn_hash': b'random hash2',
         'owner': b'some owner2',
         'value': 50,
         'signature': b'some signature2'
          }

token3 = {'txn_hash': b'random hash3',
         'owner': b'some owner3',
         'value': 50,
         'signature': b'some signature3'
    }


################################################################################

class TestSerialize:

    def test_pack_unpack_token(self):
        """Test round trip pack and unpack for token."""
        f = serialize.pack_token
        g = serialize.unpack_token

        assert g(f(token1)) == token1
        assert g(f(token1)) != token2


    def test_pack_unpack_txn(self):
        """Test round trip pack and unpack for txn."""

        f = serialize.pack_txn
        g = serialize.unpack_txn

        assert g(f(txn0a)) == txn0a
        assert g(f(txn0b)) == txn0b
        assert g(f(txn0a)) != txn0b

    def test_pack_unoack_txn_pairs(self):
          """Test round trip pack and unpack for tokens, txn pairs."""
          f = serialize.pack_txn_pair
          g = serialize.unpack_txn_pair

          pair1 = ([token1], txn0a)
          pair2 = ([token2, token3], txn0b)

          assert g(f(pair1)) == pair1
          assert g(f(pair2)) == pair2
