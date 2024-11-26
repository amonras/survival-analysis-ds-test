from dataclasses import dataclass
from datetime import date

from synthetic.records import AutoIncrement, Registry
from synthetic.state_machine import CRTPool


@dataclass
class ClassA(AutoIncrement):
    name: str


@dataclass
class ClassB(AutoIncrement):
    value: int


def test_independent_id_counters():
    # Create instances of ClassA
    a1 = ClassA(name="A1")
    a2 = ClassA(name="A2")

    # Create instances of ClassB
    b1 = ClassB(value=10)
    b2 = ClassB(value=20)

    # Check that ids are independent
    assert a1.id == 1
    assert a2.id == 2
    assert b1.id == 1
    assert b2.id == 2


class TestRecords:
    def test_trip_updates(self):
        """
        Test that the registry is updated only when the trip starts and ends
        """

        # Create a registry
        registry = Registry()
        # Create a Pool with zero shrinkage rate
        pool = CRTPool(n_crates=10,
                       daily_loss_rate=0,
                       mean_trip_duration=100,
                       replenishment_rate=0,
                       start_date=date.today(),
                       registry=registry)

        # Select a CRT from the pool
        crt = pool.pool[0]

        # Evolve until it goes to 'rented' state
        while crt.state != 'rented':
            pool.proceed(demand=5)

        # Check that a trip with this CRT is registered
        assert crt.id in [trip.crt_id for trip in registry.registry.values()]
        trip_id = [trip.id for trip in registry.registry.values() if trip.crt_id == crt.id][0]

        # Evolve until it goes to 'home' state
        while crt.state != 'home':
            pool.proceed(demand=5)

        # Check that the trip is updated
        trip = registry[trip_id]
        assert trip.states[-1][0] == 'home'

