"""
Data models for trips and a registry to keep track of them
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Tuple

import pandas as pd


class AutoIncrement:  # pylint: disable=too-few-public-methods
    """
    Implement an auto-incrementing id
    """
    id: int
    _id_counter = 1

    def __post_init__(self):
        self.id = self.__class__._id_counter  # pylint: disable=protected-access
        self.__class__._id_counter += 1


@dataclass
class Trip(AutoIncrement):
    """
    A trip contains a sequence of state transitions, from the moment a
    CRT goes out until it comes back in
    """
    crt_id: int
    created_at: date
    states: List[Tuple[str, date]]


class Registry:
    """
    A registry to keep track of all recorded trips
    """
    def __init__(self):
        self.registry = {}

    def register(self, trip: Trip):
        """
        Register a trip in the registry
        """
        self.registry[trip.id] = trip

    def __getitem__(self, item):
        return self.registry[item]

    def __repr__(self):
        return f"Registry({self.registry})"

    def dump(self):
        """
        Return a DataFrame with all the trips, their start and end dates (only if they have ended)
        """
        df = pd.DataFrame(
            [
                {
                    'trip_id': k,
                    'crt_id': v.crt_id,
                    'start': v.states[0][1],
                    'end': v.states[-1][1] if v.states[-1][0] == 'home' else None,
                    'state': v.states[-1][0]
                }
                for k, v in self.registry.items()
            ]
        )
        df['start'] = pd.to_datetime(df['start'])
        df['end'] = pd.to_datetime(df['end'])

        return df
