
from toycoin import hash # type: ignore
from toycoin import merkle # type: ignore


################################################################################


class TestMerkle:

    def test_singleton_size(self):
        """Test size of from_singleton tree."""
        f = merkle.from_singleton

        assert f(hash.hash(b'hello world')).size == 2

    def test_list_size(self):
        """Test size of from_list trees."""
        f = merkle.from_list

        assert f([hash.hash(b'0')]).size == 2
        assert f([hash.hash(b'0'),
                  hash.hash(b'1')]).size == 3
        assert f([hash.hash(b'0'),
                  hash.hash(b'1'),
                  hash.hash(b'2')]).size == 6
        assert f([hash.hash(b'0'),
                  hash.hash(b'1'),
                  hash.hash(b'2'),
                  hash.hash(b'3')]).size == 7
        assert f([hash.hash(b'0'),
                  hash.hash(b'1'),
                  hash.hash(b'2'),
                  hash.hash(b'3'),
                  hash.hash(b'4')]).size == 10

    def test_valid_contains(self):
        """Test valid and contains functions."""
        f = merkle.from_list
        t1 = f([hash.hash(b'0')])
        t2 = f([hash.hash(b'0'),
                hash.hash(b'1'),
                hash.hash(b'2'),
                hash.hash(b'3'),
                hash.hash(b'4')])

        assert merkle.valid(t1)
        assert merkle.valid(t2)

        assert merkle.contains(t1, hash.hash(b'0'))
        assert not merkle.contains(t1, hash.hash(b'1'))
        assert merkle.contains(t2, hash.hash(b'1'))
        assert not merkle.contains(t1, hash.hash(b'10'))


    def test_second_preimage_attack(self):
        """Test second preimage attack."""
        f = merkle.from_list

        t = f([hash.hash(b'0'),
               hash.hash(b'1'),
               hash.hash(b'2'),
               hash.hash(b'3'),
               hash.hash(b'4')])

        h1, h2 = t.left.label, t.right.label
        t2 = f([h1, h2])

        # the attack fails
        assert t.label != t2.label

        # just checking the attack prevention is working as expected
        assert t.label[1:] == hash.hash(b'\x01' + h1[1:] +
                                        b'\x01' + h2[1:])
