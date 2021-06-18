
from toycoin import signature


################################################################################


class TestSignature:

    def test_roundtrip(self):
        """Test sign and verify."""

        msg = b'hello world'

        priv_key = signature.gen_priv_key()
        pub_key = signature.get_pub_key(priv_key)

        s = signature.sign(priv_key, msg)

        assert signature.verify(s, pub_key, msg) is True
        assert signature.verify(s[:-1], pub_key, msg) is False
        assert signature.verify(s, pub_key, msg[:-1]) is False
