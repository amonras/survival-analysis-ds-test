"""
Generate synthetic data for testing
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
from matplotlib import pyplot as plt
from tqdm.auto import tqdm
import pandas as pd

from synthetic.records import Registry
from synthetic.state_machine import CRTPool


def initparser():
    """
    Generate synthetic data for testing
    - path: output path for assets
    - n: number of records
    - T: Mean Trip duration
    - s: Shrinkage rate
    :return:
    """
    cli_parser = argparse.ArgumentParser(description='Generate synthetic data for testing',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cli_parser.add_argument('-t', '--target',
                        help='target path for output assets',
                        default=Path(__file__).parent.parent / "data/")
    cli_parser.add_argument('-n', '--n_assets',
                            type=int, help='number of assets', default=2000)
    cli_parser.add_argument('-T', '--trip_duration',
                            type=int, help='Mean Trip duration', default=100)
    cli_parser.add_argument('-s', '--shrinkage_rate',
                            type=float, help='Shrinkage rate', default=0.15)
    cli_parser.add_argument('-r', '--replenish_rate',
                            type=float, help='Replenishment rate', default=1)
    cli_parser.add_argument('-d', '--days',
                            type=int, help='Number of days to simulate', default=2000)

    return cli_parser


def generate(
        n: int,
        T: int,  # pylint: disable=invalid-name
        shrinkage_rate: float,
        replenishment_rate: float,
        demand: pd.DataFrame
) -> Tuple[
    pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic data for testing
    :param n: number of records
    :param T: Mean Trip duration (in days)
    :param shrinkage_rate: Shrinkage rate
    :param replenishment_rate: Replenishment rate (CRTs per day)
    :param demand: Demand time series

    :return: A tuple of two pd.DataFrames:
        - The first one contains the registry of all recorded trips
        with trip_id, crt_id, start, end and state
        - The second one contains the daily reports of the CRT pools
    """

    registry = Registry()

    daily_loss_rate = shrinkage_rate / (T * (1 - shrinkage_rate))
    pool = CRTPool(
        n_crates=n,
        mean_trip_duration=T,
        daily_loss_rate=daily_loss_rate,
        start_date=demand.index.min(),
        replenishment_rate=replenishment_rate,
        registry=registry
    )

    reports = []
    for _, demand_value in tqdm(demand.iterrows(), total=len(demand)):
        reports.append(pool.proceed(demand=int(demand_value['demand'])))

    # for k, v in registry.registry.items():
    #     print(k, v)

    return registry.dump(), pd.DataFrame(reports, index=demand.index)


def generate_demand(n: int) -> pd.DataFrame:
    """
    Generate a synthetic demand time series with weekly, monthly
    and yearly seasonality, plus a trend, for n days.
    :param n: Number of days
    :return: A pd.DataFrame with a single column 'demand'
    """
    np.random.seed(42)
    scale = .3

    date_range = pd.date_range(end=datetime.now().date(), periods=n, freq='D')

    weekly_phase, monthly_phase, yearly_phase = 2 * np.pi * np.random.rand(3)
    weekly_amplitude = scale * np.random.randint(0, 3, size=n)
    monthly_amplitude = scale * np.random.randint(2, 5, size=n)
    yearly_amplitude = scale * np.random.randint(2, 20, size=n)

    weekly_seasonality = weekly_amplitude * np.power(
        np.sin(2 * np.pi * np.arange(n) / 7 + weekly_phase),
        2
    )
    monthly_seasonality = monthly_amplitude * np.sin(2 * np.pi * np.arange(n) / 30 + monthly_phase)
    yearly_seasonality = yearly_amplitude * np.sin(2 * np.pi * np.arange(n) / 365 + yearly_phase)

    trend = scale * (25 + np.arange(n) / 100)

    demand = pd.DataFrame(
        {
            'demand': trend + weekly_seasonality + monthly_seasonality + yearly_seasonality
        },
        index=date_range
    )
    return demand


def main(path: Optional[Path] = None, **kwargs):
    """
    Main function to generate synthetic data
    """
    if path is None:
        path = Path(__file__).parent.parent / "data"

    n = kwargs["n_assets"]
    T = kwargs["trip_duration"]  # pylint: disable=invalid-name
    shrinkage_rate = kwargs["shrinkage_rate"]
    replenishment_rate = kwargs["replenish_rate"]
    days = kwargs["days"]

    demand = generate_demand(days)
    ax = demand.plot(figsize=(15, 5), title="Daily Demand", legend=False)
    ax.set_ylim(0, 20)
    ax.set_xlabel("Date")
    ax.get_figure().savefig(path / "demand.png")
    demand.to_parquet(path / "demand.parquet")
    trips, df = generate(
        n=n,
        T=T,
        shrinkage_rate=shrinkage_rate,
        replenishment_rate=replenishment_rate,
        demand=demand
    )
    print("\nSummary")
    print("-----------------------------------")
    print(f"Total trips generated: {len(trips)}")
    print(f"Total CRTs lost: {len(trips[trips['state'] == 'lost'])}")
    print(f"Final CRTs rented: {len(trips[trips['state'] == 'rented'])}")
    print(f"Final CRTs pool (home + rented): {len(trips[trips['state'].isin(['home', 'rented'])])}")
    print(f"Average trip length: "
          f"{(trips['end'] - trips['start']).mean() / pd.Timedelta(days=1):.2f} days")
    print(f"Shrinkage Rate: {(trips['state'] == 'lost').mean():.2%}")
    print("-----------------------------------")

    trips.to_parquet(path / "trips.parquet")

    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(12, 8))

    demand.plot(ax=ax[0])
    df.plot.area(ax=ax[1], stacked=True, legend=True)
    ax[0].set_title("Demand")
    ax[1].set_title("CRT Pool")
    ax[1].set_ylabel("Number of CRTs")
    ax[1].set_xlabel("Date")
    plt.tight_layout()

    df.to_parquet(path / "daily_reports.parquet")
    fig.get_figure().savefig(path / "output.png")


if __name__ == "__main__":
    parser = initparser()
    args = parser.parse_args()
    print(args)

    main(path=Path(args.target), **args.__dict__)
