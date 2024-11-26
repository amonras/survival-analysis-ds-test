"""
Implements different pool sampling strategies
"""

from typing import Optional

import numpy as np


class PoolSampling:
    """
    Implements a pool such that elements are drawn according to a specific logic
    """

    def __init__(self):
        self.pool = np.array([], dtype=int)

    def ingress(self, idx: int):
        """
        Add element to the pool
        """
        self.pool = np.append(self.pool, idx)

    def egress(self, idx: int):
        """
        Removed from the pool
        """
        # remove id from pool
        self.pool = self.pool[self.pool != idx]

    def remove(self, idx: int):
        """
        Remove an element from the pool, regardless of its due time
        """
        self.egress(idx)

    def draw(self, n: Optional[int]):
        """
        Draw n elements from the pool, according to the specific logic.
        Some implementations may ignore the parameter n,
        and return a different number of elements according to their own logic
        """

    def __repr__(self):
        return f"{self.__class__.__name__}({self.pool})"


class Poisson(PoolSampling):
    """
    Implements a pool where elements are drawn according to a Poisson process (memoryless)
    """

    def __init__(self, rate):
        super().__init__()
        self.rate = rate

    def draw(self, n: Optional[int]):
        drawn = np.random.choice([True, False],
                                 p=[self.rate, 1 - self.rate],
                                 size=len(self.pool), replace=True)
        return self.pool[drawn]


class LogNormal(PoolSampling):
    """
    Implements a pool where elements are drawn according to a Log-Normal distribution
    """

    def __init__(self, mean, std):
        super().__init__()
        self.pool = {}
        self.mean = mean
        self.std = std

    def ingress(self, idx: int):
        # initialize the counter for each element
        # Draw the number of steps from a Log-Normal distribution
        n = np.log(np.random.lognormal(self.mean, self.std))

        self.pool[idx] = n

    def egress(self, idx: int):
        # remove id from pool
        self.pool.pop(idx)

    def remove(self, idx: int):
        # remove id from pool
        self.pool.pop(idx)

    def draw(self, n: Optional[int]):
        # *******************************
        # *** Ignores the parameter n ***
        # *******************************

        # Return list of elements that are due to transition
        drawn = [id for id, steps in self.pool.items() if steps < 0]

        # update the counter for each element
        for idx in self.pool:
            self.pool[idx] -= 1

        return drawn


class Scrambling(PoolSampling):
    """
    Implements a scrambling pool where elements are drawn randomly,
    irrespectively of the order they enter the pool
    """

    def draw(self, n: Optional[int]):
        if n > len(self.pool):
            return self.pool
        return np.random.choice(self.pool, n)


class LIFO(PoolSampling):
    """
    Implements a pool such that elements are drawn according to a Last-In-First-Out policy
    """

    def draw(self, n: Optional[int]):
        drawn = self.pool[len(self.pool) - n:] if n <= len(self.pool) else self.pool
        return drawn


class FIFO(PoolSampling):
    """
    Implements a pool such that elements are drawn according to a First-In-First-Out policy,
    but only after a given delay
    """

    def __init__(self, delay=0):
        super().__init__()
        self.pool = {k: np.array([]) for k in range(delay + 1)}
        self.delay = delay

    def ingress(self, idx: int):
        self.pool[self.delay] = np.append(self.pool[self.delay], idx)

    def egress(self, idx: int):
        assert idx in self.pool[0], f"Element {idx} is not due to egress"
        self.pool[0] = self.pool[0][self.pool[0] != idx]

    def remove(self, idx: int):
        for k in range(self.delay + 1):
            self.pool[k] = self.pool[k][self.pool[k] != idx]

    def draw(self, n: Optional[int]):
        drawn = self.pool[0][:n] if n <= len(self.pool[0]) else self.pool[0]

        # Move all elements one step forward
        if self.delay > 0:
            # Keep the elements already due, but add next batch
            self.pool[0] = np.concat([self.pool[0], self.pool[1]])
            for k in range(1, self.delay):
                self.pool[k] = self.pool[k + 1]
            self.pool[self.delay] = np.array([])
        return drawn


class Sink(PoolSampling):
    """
    Implements a pool such that elements are never drawn
    """

    def draw(self, n: Optional[int]):
        return []
