import pytest
from scripts.deploy import deploy_stEth_price_feed


@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]


@pytest.fixture(scope='module')
def stEth_price_feed(deployer, stable_swap_oracle, curve_pool):
    return deploy_stEth_price_feed(
        max_safe_price_difference=500,
        stable_swap_oracle_address=stable_swap_oracle,
        curve_pool_address=curve_pool,
        admin=deployer,
        tx_params={"from": deployer})


@pytest.fixture(scope='module')
def stable_swap_oracle(deployer, StableSwapOracleMock):
    return StableSwapOracleMock.deploy(1e18, {"from": deployer})


@pytest.fixture(scope='module')
def curve_pool(deployer, CurvePoolMock):
    return CurvePoolMock.deploy(1e18, {"from": deployer})


@pytest.fixture(scope='module')
def stranger(accounts):
    return accounts[9]
