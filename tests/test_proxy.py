import pytest
from brownie import reverts, Contract, PriceFeedProxy


@pytest.fixture(scope='function')
def price_feed(deploy_price_feed):
    return deploy_price_feed(max_safe_price_difference=500)


def as_proxy(price_feed):
    return Contract.from_abi('PriceFeedProxy', price_feed.address, PriceFeedProxy.abi)


def test_upgrade(
    price_feed,
    stable_swap_oracle,
    curve_pool,
    stranger,
    NewStEthPriceFeed,
    helpers
):
    curve_pool.set_price(0.98 * 1e18)
    stable_swap_oracle.set_price(1e18)

    price_feed.update_safe_price({'from': stranger})
    assert price_feed.safe_price_value() == 0.98 * 1e18

    prev_timestamp = price_feed.safe_price_timestamp()
    prev_feed_admin = price_feed.admin()

    feed_proxy = as_proxy(price_feed)
    admin = feed_proxy.getProxyAdmin()

    new_feed_impl = NewStEthPriceFeed.deploy({'from': admin})

    tx = feed_proxy.upgradeTo(new_feed_impl, b'', {'from': admin})

    assert feed_proxy.implementation() == new_feed_impl
    assert price_feed.safe_price() == (0, 42)

    # state is preserved
    assert price_feed.safe_price_value() == 0.98 * 1e18
    assert price_feed.safe_price_timestamp() == prev_timestamp
    assert price_feed.admin() == prev_feed_admin

    helpers.assert_single_event_named('Upgraded', tx, {'implementation': new_feed_impl})


def test_upgrade_with_setup(price_feed, NewStEthPriceFeed, helpers):
    feed_proxy = as_proxy(price_feed)
    admin = feed_proxy.getProxyAdmin()

    new_feed_impl = NewStEthPriceFeed.deploy({'from': admin})
    price = 0.94242 * 10**18

    calldata = new_feed_impl.perform_upgrade.encode_input(price)
    tx = feed_proxy.upgradeTo(new_feed_impl, calldata, {'from': admin})

    assert feed_proxy.implementation() == new_feed_impl
    assert price_feed.safe_price() == (price, 42)

    helpers.assert_single_event_named('Upgraded', tx, {'implementation': new_feed_impl})


def test_upgrade_fails_by_stanger(price_feed, stranger, StEthPriceFeed):
    feed_proxy = as_proxy(price_feed)
    admin = feed_proxy.getProxyAdmin()
    new_feed_impl = StEthPriceFeed.deploy({'from': admin})

    with reverts('ERC1967: unauthorized'):
        feed_proxy.upgradeTo(new_feed_impl, b'', {'from': stranger})


def test_set_proxy_admin(price_feed, accounts, helpers):
    feed_proxy = as_proxy(price_feed)

    old_admin = feed_proxy.getProxyAdmin()
    new_admin = accounts[2]
    tx = feed_proxy.changeProxyAdmin(new_admin, {'from': old_admin})

    assert feed_proxy.getProxyAdmin() == new_admin

    helpers.assert_single_event_named('AdminChanged', tx, {
        'previousAdmin': old_admin,
        'newAdmin': new_admin
    })

    tx = feed_proxy.changeProxyAdmin(old_admin, {'from': new_admin})

    helpers.assert_single_event_named('AdminChanged', tx, {
        'previousAdmin': new_admin,
        'newAdmin': old_admin
    })


def test_set_proxy_admin_fails_by_stranger(price_feed, stranger):
    feed_proxy = as_proxy(price_feed)

    with reverts('ERC1967: unauthorized'):
        feed_proxy.changeProxyAdmin(stranger, {'from': stranger})
