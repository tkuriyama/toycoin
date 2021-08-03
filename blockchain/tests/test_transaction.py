"""Test transaction.
This covers helper functions; eee test_wallet.py module for the bulk of tests.
"""


from toycoin import transaction # type: ignore


################################################################################
# Sample Data


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

################################################################################


class TestTransactionHelpers:

    def test_sum_tokens(self):
        """Test sum_tokens."""
        f = transaction.sum_tokens

        t1 = {'txn_hash': b'',
              'owner': b'',
              'value': 100,
              'signature': b''
              }

        t2 = {'txn_hash': b'',
              'owner': b'',
              'value': 50,
              'signature': b''
              }

        assert f([]) == 0
        assert f([t1]) == 100
        assert f([t1, t2]) == 150


    def test_pack_unpack(self):
        """Test round trip pack and unpack"""

        f = transaction.pack
        g = transaction.unpack

        assert g(f(txn0a)) == txn0a
        assert g(f(txn0b)) == txn0b
        assert g(f(txn0a)) != txn0b
