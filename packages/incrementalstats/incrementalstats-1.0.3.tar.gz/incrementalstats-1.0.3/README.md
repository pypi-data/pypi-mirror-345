# Incremental stats

`pip install incrementalstats`

A few incremental 1st order statistics in numpy. Currently:

- Correlation (Pearson)
- Covariance
- Variance
- Mean
- Welch-t

## Setup a venv

    mkdir venv
    virtualenv -p `which python3` venv
    source venv/bin/activate

## Option 1: Checkout hackable project

    python -m pip install --upgrade pip
    git clone https://github.com/ceesb/python-incrementalstats
    pip install -e python-incrementalstats
    cd python-incrementalstats

Now all the changes you make to this project source code are "live".

## Option 2: Build a wheel

    git clone https://github.com/ceesb/python-incrementalstats
    cd python-incrementalstats
    python -m build

Now you can distribute or install the wheel created in the `dist` folder.

    $ ls dist/
    incrementalstats-0.0.1-py3-none-any.whl  incrementalstats-0.0.1.tar.gz
    pip install dist/incrementalstats-0.0.1-py3-none-any.whl

## Run the tests

    python -m unittest
