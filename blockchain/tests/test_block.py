
from toycoin import block, hash # type: ignore


################################################################################

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
        assert block.valid_header(b)


    def test_solved(self):
        """Test solved"""
        f = block.solved

        assert f(b'\x01\x02', 0) is True
        assert f(b'\x01\x02', 1) is False

        assert f(b'\x00\x00\x01\x02', 1) is True
        assert f(b'\x00\x00\x01\x02', 2) is True
        assert f(b'\x00\x00\x01\x02', 3) is False
