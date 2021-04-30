import pytest
from brownie import reverts, Contract


@pytest.fixture(scope='module')
def feed_proxy(stEth_price_feed, UpgradableProxy):
   return Contract.from_abi('UpgradableProxy', stEth_price_feed.address, UpgradableProxy.abi)


def test_upgrade(feed_proxy, accounts, StEthPriceFeed):
    admin = feed_proxy.getProxyAdmin()
    new_price_feed_contract = StEthPriceFeed.deploy({'from': admin})
    feed_proxy.upgradeTo(new_price_feed_contract, {'from': admin})

    assert feed_proxy.implementation() == new_price_feed_contract


def test_upgrade_fails_by_stanger(feed_proxy, stranger, StEthPriceFeed):
    admin = feed_proxy.getProxyAdmin()
    new_price_feed_contract = StEthPriceFeed.deploy({'from': admin})
    with reverts():
        feed_proxy.upgradeTo(new_price_feed_contract, {'from': stranger})


def test_set_proxy_owner(feed_proxy, accounts):
    old_owner = feed_proxy.getProxyAdmin()
    new_owner = accounts[2]
    feed_proxy.changeProxyAdmin(new_owner, {'from': old_owner})

    assert feed_proxy.getProxyAdmin() == new_owner

    feed_proxy.changeProxyAdmin(old_owner, {'from': new_owner})


def test_set_proxy_owner_fails_by_stranger(feed_proxy, stranger):
    with reverts():
        feed_proxy.changeProxyAdmin(stranger, {'from': stranger})
