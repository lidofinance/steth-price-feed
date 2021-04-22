import pytest
from scripts.deploy import deploy_stEth_price_feed
from utils.config import (get_is_live, get_deployer_account)
from brownie import (CurvePoolMock, StableSwapOracleMock)


@pytest.fixture(scope='module')
def deployer():
    return get_deployer_account(get_is_live())


@pytest.fixture(scope='module')
def stEth_price_feed(deployer, stable_swap_oracle, curve_pool):
    return deploy_stEth_price_feed(
        max_safe_price_difference=500,
        stable_swap_oracle_address=stable_swap_oracle,
        curve_pool_address=curve_pool,
        admin=deployer,
        tx_params={"from": deployer})


@pytest.fixture(scope='module')
def stable_swap_oracle(deployer):
    return StableSwapOracleMock.deploy(1e18, {"from": deployer}, publish_source=False)


@pytest.fixture(scope='module')
def curve_pool(deployer):
    return CurvePoolMock.deploy(1e18, {"from": deployer},
                                       publish_source=False)
