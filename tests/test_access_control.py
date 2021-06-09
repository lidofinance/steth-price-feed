import pytest
from brownie import reverts, Contract, PriceFeedProxy, ZERO_ADDRESS


@pytest.fixture(scope='module')
def admin(accounts):
    return accounts[7]


@pytest.fixture(scope='function')
def price_feed(deploy_price_feed, deployer, admin):
    return deploy_price_feed(max_safe_price_difference=500, deployer=deployer, admin=admin)


def as_proxy(price_feed):
    return Contract.from_abi('PriceFeedProxy', price_feed.address, PriceFeedProxy.abi)


def test_non_admin_cannot_set_price_difference(price_feed, deployer, stranger):
    with reverts():
        price_feed.set_max_safe_price_difference(1000, {'from': stranger})

    with reverts():
        price_feed.set_max_safe_price_difference(1000, {'from': deployer})


def test_non_admin_cannot_set_admin(price_feed, deployer, stranger):
    with reverts():
        price_feed.set_admin(deployer, {'from': stranger})

    with reverts():
        price_feed.set_admin(stranger, {'from': deployer})


def test_non_admin_cannot_upgrade(price_feed, deployer, stranger, StEthPriceFeed):
    proxy = as_proxy(price_feed)
    new_feed_impl = StEthPriceFeed.deploy({'from': deployer})

    with reverts():
        proxy.upgradeTo(new_feed_impl, b'', {'from': stranger})

    with reverts():
        proxy.upgradeTo(new_feed_impl, b'', {'from': deployer})

def test_admin_can_set_zero_admin(price_feed, admin):
    price_feed.set_admin(ZERO_ADDRESS, {'from': admin})
    assert price_feed.admin() == ZERO_ADDRESS
