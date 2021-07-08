"""Test transaction.
This covers helper functions; eee test_wallet.py module for the bulk of tests.
"""


from toycoin import transaction # type: ignore


################################################################################


class TestTransactionHelpers:

    def test_sum_tokens(self):
        """Test sum_tokens."""
        f = transaction.sum_tokens

        t1 = {'txn_hash': b'',
              'owner': b'',
              'value': 100,
              'signature': b''}

        t2 = {'txn_hash': b'',
              'owner': b'',
              'value': 100,
              'signature': b''}

        assert f([]) == 0
        assert f([t1]) == 100
        assert f([t1, t2]) == 200
