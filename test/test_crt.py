import pytest
from datetime import date
from synthetic.state_machine import CRT


def test_initial_state():
    crt = CRT(created_at=date.today())
    assert crt.state == 'home'
    assert crt.created_at == date.today()


def test_state_transitions():
    crt = CRT(created_at=date.today())

    crt.rent()
    assert crt.state == 'rented'

    crt.recall()
    assert crt.state == 'home'


def test_lose():
    """check crates can be lost from any state"""
    crt = CRT(created_at=date.today())
    crt.next(date.today())
    crt.lose(date.today())
    assert crt.state == 'lost'


def test_multiple_instances():
    crt1 = CRT(created_at=date.today())
    crt2 = CRT(created_at=date.today())

    assert crt1.id != crt2.id


def test_next():
    """
    Test the next method evolves the state machine correctly
    """
    today = date.today()
    crt = CRT(created_at=date, reporting_callback=lambda x: x)
    crt.next(today)
    assert crt.state == 'rented'

    crt.next(today)
    assert crt.state == 'home'

    crt.next(today)
    assert crt.state == 'rented'

    crt.next(today)
    assert crt.state == 'home'


if __name__ == "__main__":
    pytest.main()