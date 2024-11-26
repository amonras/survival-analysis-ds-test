import pytest
from pytest import fixture

from datetime import date

import numpy as np

from synthetic.state_machine import CRT, CRTPool

np.random.seed(42)

pool_size = 10


@fixture
def crt_pool():
    pool = CRTPool(
        pool_size,
        mean_trip_duration=100,
        daily_loss_rate=.01,
        replenishment_rate=0,
        start_date=date.today()
    )
    # let's push the FIFO elements in the 'home' state
    for _ in range(7):
        pool.proceed(demand=0)

    yield pool


def test_crtpool_initialization(crt_pool):
    assert len(crt_pool.pool) == pool_size
    assert all(isinstance(crt, CRT) for crt in crt_pool.pool)


def test_crtpool_proceed(crt_pool):
    initial_report = crt_pool.report()
    crt_pool.proceed(demand=1)
    new_report = crt_pool.report()
    assert initial_report != new_report


def test_crtpool_report(crt_pool):
    report = crt_pool.report()
    assert isinstance(report, dict)
    assert all(state in report for state in
               ['home', 'rented', 'lost'])
    assert all(isinstance(count, int) for count in report.values())


if __name__ == "__main__":
    pytest.main()
