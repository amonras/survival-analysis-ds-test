import pytest
import numpy as np
from synthetic.pool_sampling import FIFO


class TestFIFO:

    def test_ingress(self):
        fifo = FIFO(delay=2)
        fifo.ingress(1)
        fifo.ingress(2)
        assert 1 in fifo.pool[2]
        assert 2 in fifo.pool[2]

    def test_undue_egress(self):
        fifo = FIFO(delay=2)
        fifo.ingress(1)
        fifo.ingress(2)
        # should raise an exception because 1 is not due to egress
        with pytest.raises(AssertionError):
            fifo.egress(1)

    def test_due_egress(self):
        fifo = FIFO(delay=2)
        fifo.ingress(1)
        fifo.ingress(2)
        fifo.draw(1)
        assert 1 in fifo.pool[1]
        assert 2 in fifo.pool[1]
        fifo.draw(1)

        fifo.egress(1)
        assert 1 not in fifo.pool[0]
        assert 2 in fifo.pool[0]

    def test_draw(self):
        fifo = FIFO(delay=2)
        fifo.ingress(1)
        fifo.ingress(2)
        fifo.pool[0] = np.array([3, 4] + list(fifo.pool[0]))
        drawn = fifo.draw(1)
        assert len(drawn) == 1
        assert drawn[0] == 3

    def test_draw_more_than_available(self):
        fifo = FIFO(delay=2)
        fifo.ingress(1)
        fifo.ingress(2)
        fifo.pool[0] = np.array([3, 4])
        drawn = fifo.draw(5)
        assert len(drawn) == 2
        assert 3 in drawn
        assert 4 in drawn

    def test_delay_mechanism(self):
        fifo = FIFO(delay=2)
        fifo.ingress(1)
        fifo.ingress(2)
        fifo.draw(0)  # Move elements forward
        assert 1 in fifo.pool[1]
        assert 2 in fifo.pool[1]
        fifo.draw(0)  # Move elements forward again
        assert 1 in fifo.pool[0]
        assert 2 in fifo.pool[0]