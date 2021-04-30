import pytest
from brownie import (reverts, StEthPriceFeed)
from brownie.network.state import Chain
from brownie.convert import to_bytes


def test_max_safe_price_difference(stEth_price_feed):
    stEth_price_feed.max_safe_price_difference()


def test_safe_price_should_reverts_on_price_set(stEth_price_feed):
    with reverts():
        stEth_price_feed.safe_price()


def test_safe_current_price(stable_swap_oracle, curve_pool, stEth_price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    assert stEth_price_feed.current_price() == (9.8 * 1e17, True)


def test_unsafe_current_price_gte_1(stable_swap_oracle, curve_pool,
                                    stEth_price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(1.02 * 1e18)
    assert stEth_price_feed.current_price() == (1.02 * 1e18, False)


def test_unsafe_current_price_diff_gt_max_diff(stable_swap_oracle, curve_pool,
                                               stEth_price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.4 * 1e17)
    assert stEth_price_feed.current_price() == (9.4 * 1e17, False)


def test_update_safe_price(stable_swap_oracle, curve_pool, stEth_price_feed,
                           stranger):
    chain = Chain()
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    stEth_price_feed.update_safe_price({"from": stranger})
    assert stEth_price_feed.safe_price() == (9.8 * 1e17, chain[-1].timestamp)


def test_update_safe_price_fails_on_unsafe(stable_swap_oracle, curve_pool,
                                           stEth_price_feed, stranger):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    stEth_price_feed.update_safe_price({"from": stranger})
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9 * 1e17)
    with reverts("price is not safe"):
        stEth_price_feed.update_safe_price({"from": stranger})


def test_update_safe_price_with_gt_1(stable_swap_oracle, curve_pool,
                                     stEth_price_feed, stranger):
    chain = Chain()
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    stEth_price_feed.update_safe_price({"from": stranger})
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(1.02 * 1e18)
    stEth_price_feed.update_safe_price({"from": stranger})
    assert stEth_price_feed.safe_price() == (1e18, chain[-1].timestamp)


def test_set_admin(stEth_price_feed, accounts):
    old_admin = stEth_price_feed.admin()
    new_admin = accounts[2]
    stEth_price_feed.set_admin(new_admin, {"from": old_admin})
    assert stEth_price_feed.admin() == new_admin
    stEth_price_feed.set_admin(old_admin, {"from": new_admin})


def test_set_admin_acl_fails(stEth_price_feed, stranger):
    new_admin = stranger
    with reverts():
        stEth_price_feed.set_admin(new_admin, {"from": new_admin})


def test_set_max_safe_price_difference(stEth_price_feed):
    admin = stEth_price_feed.admin()
    stEth_price_feed.set_max_safe_price_difference(5000, {"from": admin})
    assert stEth_price_feed.max_safe_price_difference() == 5000


def test_set_max_safe_price_difference_acl_fails(stEth_price_feed, stranger):
    with reverts():
        stEth_price_feed.set_max_safe_price_difference(5000,
                                                       {"from": stranger})


def test_upgade(proxy, stEth_price_feed, accounts):
    admin = proxy.getProxyAdmin()
    new_price_feed_contract = StEthPriceFeed.deploy({"from": admin})
    proxy.upgradeTo(new_price_feed_contract, {"from": admin})

    assert proxy.implementation() == new_price_feed_contract


def test_upgade_fails_by_stanger(proxy, stEth_price_feed, stranger):
    admin = proxy.getProxyAdmin()
    new_price_feed_contract = StEthPriceFeed.deploy({"from": admin})
    with reverts():
        proxy.upgradeTo(new_price_feed_contract, {"from": stranger})


def test_set_proxy_owner(proxy, accounts):
    old_owner = proxy.getProxyAdmin()
    new_owner = accounts[2]
    proxy.changeProxyAdmin(new_owner, {"from": old_owner})

    assert proxy.getProxyAdmin() == new_owner

    proxy.changeProxyAdmin(old_owner, {"from": new_owner})


def test_set_proxy_owner_fails_by_stranger(proxy, stranger):
    with reverts():
        proxy.changeProxyAdmin(stranger, {"from": stranger})
