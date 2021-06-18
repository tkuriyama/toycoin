
from toycoin import hash


################################################################################


class TestHash:

    def test_hash(self):
        """Test SHA512 hash."""
        msg = b'hello world'

        h = '309ecc489c12d6eb4cc40f50c902f2b4d0ed77ee511a7c7a9bcd'
        h += '3ca86d4cd86f989dd35bc5ff499670da34255b45b0cfd830e81'
        h += 'f605dcf7dc5542e93ae9cd76f'

        assert hash.hash(msg).hex() == h
