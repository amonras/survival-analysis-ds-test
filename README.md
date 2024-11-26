# IFCO Data Science Test Assignment

This repo contains the following parts:
- `Model.ipynb`: Jupyter notebook with the model and the explanation
- `synthetic/`: Python module to generate synthetic data
- `test/`: Unit tests for the synthetic module
- `Makefile`: Makefile to run the tests and setup the project
- `IFCO Presentation.pptx`: Presentation with the explanation of my approach

## Setup

To set up the project, create a virtual environment and
run the following command:

```sh
make setup
```
This will install the required dependencies listed in `requirements.txt` and register the current python 
environment to jupyter as `amonras-ifco`, so that the notebook can be executed without further setup.

## Running the tests
To run the unit tests, run the following command:
```sh
make test
```
This will ensure that your environment is operational and that the synthetic data generation module is working as expected.

## Generating synthetic data
To generate synthetic data, run the following command:
```sh
make generate
```

### The `synthetic.generate` Command Line Interface
Alternatively, you can use the `synthetic.generate` CLI to generate synthetic data with specific settings
```sh
$ python -m synthetic.generate --help
usage: generate.py [-h] [-t TARGET] [-n N_ASSETS] [-T TRIP_DURATION] [-s SHRINKAGE_RATE] [-r REPLENISH_RATE] [-d DAYS]

Generate synthetic data for testing

options:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        target path for output assets (default: ./data)
  -n N_ASSETS, --n_assets N_ASSETS
                        number of assets (default: 2000)
  -T TRIP_DURATION, --trip_duration TRIP_DURATION
                        Mean Trip duration (default: 100)
  -s SHRINKAGE_RATE, --shrinkage_rate SHRINKAGE_RATE
                        Shrinkage rate (default: 0.15)
  -r REPLENISH_RATE, --replenish_rate REPLENISH_RATE
                        Replenishment rate (default: 1)
  -d DAYS, --days DAYS  Number of days to simulate (default: 2000)
```

## Opening the notebook
To open the notebook, run the following command:
```sh
make notebook
```

This will open the Jupyter notebook in your browser.

If you want to open the notebook to use a different set of synthetic data, pass it as an env var:
```
DATA=your_data_path jupyter notebook Model.ipynb
```

## Requirements
This code has been tested with python 3.12. Using a virtual environment is strongly encouraged.
