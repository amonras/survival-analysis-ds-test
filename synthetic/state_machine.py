"""
Implements a simple state machine for a crate rental system, and a pool
of assets that keeps track of their states and simulates their evolution
"""

import datetime
from datetime import date

import numpy as np

from transitions import Machine

from synthetic.pool_sampling import FIFO, Sink, LogNormal
from synthetic.records import AutoIncrement, Trip, Registry

states = ['home', 'rented', 'lost']


class CRT(Machine, AutoIncrement):
    """
    Implements a simple state machine for a crate rental system
    """
    counter = 0

    def __init__(self, created_at=date, reporting_callback=None):
        super().__init__(
            states=states,
            transitions=[
                {'trigger': 'rent', 'source': 'home', 'dest': 'rented'},
                {'trigger': 'recall', 'source': 'rented', 'dest': 'home'},
                {'trigger': 'lose', 'source': 'rented', 'dest': 'lost'},
            ],
            initial='home'
        )
        self.created_at = created_at
        self.trip = None

        # Use this whenever the state changes
        if reporting_callback is not None:
            self.reporting_callback = reporting_callback
        else:
            self.reporting_callback = lambda x: x

        # Need to autoincrement manually because it's not a dataclass
        self.id = self._id_counter
        CRT._id_counter += 1

    def next(self, day: date):
        """
        Proceed to the next natural state
        """
        if self.state == 'home':
            self.trip = Trip(crt_id=self.id, created_at=day, states=[('rented', day)])
            self.reporting_callback(self.trip)
            self.rent()
        elif self.state == 'rented':
            # Terminate trip
            self.trip.states.append(('home', day))
            self.reporting_callback(self.trip)
            self.trip = None
            self.recall()
        else:
            self.lose(day)

    def lose(self, day):
        """
        Trigger an asset loss on date `day`
        """
        self.trip.states.append(('lost', day))
        self.to_lost()

    def __repr__(self):
        return f"CRT(id={self.id}, state={self.state})"


class CRTPool:
    """
    Implements a pool of assets that keeps track of their states and simulates their evolution
    """
    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
            self,
            n_crates,
            mean_trip_duration,
            daily_loss_rate,
            replenishment_rate,
            start_date,
            registry=None
    ):
        if registry is None:
            self.registry = Registry()
        else:
            self.registry = registry

        self.pool = []
        self.mean_trip_duration = mean_trip_duration
        self.shrinkage_rate = daily_loss_rate
        self.replenishment_rate = replenishment_rate
        self.date = start_date

        # Implements the delay logic for each state
        # Can be Markovian, FIFO, LIFO, Constant
        self.state_pools = {
            'home': FIFO(delay=7),
            'rented': LogNormal(mean_trip_duration, mean_trip_duration / 2),
            'lost': Sink()
        }

        # Create n instances of the CRT state machine
        for _ in range(n_crates):
            crt = CRT(reporting_callback=self.registry.register)
            self.state_pools[crt.state].ingress(crt.id)
            self.pool.append(crt)

    def proceed(self, demand: int):
        """
        Proceed one day in the simulation with the provided demand
        """
        # These are the CRTs that will transition out of each pool
        requests = {
            state: self.state_pools[state].draw(demand) for state in states
        }

        for crt in self.pool:
            source_pool = self.state_pools[crt.state]

            if crt.state in ['rented']:
                # Randomly lose some crates
                if np.random.rand() < self.shrinkage_rate:
                    source_pool.remove(crt.id)
                    crt.lose(self.date)  # Will never make it back to 'incoming'
                    target_pool = self.state_pools['lost']
                    target_pool.ingress(crt.id)
                    continue

            if crt.id in requests[crt.state]:
                # Time to move on
                source_pool.egress(crt.id)
                crt.next(self.date)
                target_pool = self.state_pools[crt.state]
                target_pool.ingress(crt.id)

        # Add new CRTs to the pool
        # Chose according to a poisson, how many new CRTs will be added
        n = np.random.poisson(self.replenishment_rate)
        for _ in range(n):
            crt = CRT(self.date, reporting_callback=self.registry.register)
            self.add_crt(crt)

        self.date += datetime.timedelta(days=1)

        # At the end, report the number of crates in each state
        return self.report()

    def add_crt(self, crt: CRT):
        """
        Add a CRT to the pool
        """
        self.state_pools[crt.state].ingress(crt.id)
        self.pool.append(crt)

    def report(self):
        """
        Return the number of crates in each state
        """
        report = {}
        for state in states:
            report[state] = len([crt for crt in self.pool if crt.state == state])
        return report
