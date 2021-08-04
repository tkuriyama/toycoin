

import random # type: ignore
from toycoin.network import txn_oracle # type: ignore


################################################################################


class TestHelpers:

    def test_draw_two(self):
        """Test draw two (non-deterministic(."""
        f = txn_oracle.draw_two

        for _ in range(1000):
            max_n = random.randint(4, 20)
            i, j = f(max_n)
            assert i != j
