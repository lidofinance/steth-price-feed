import pytest
from brownie import chain, reverts


ERR_PRICE_NOT_SAFE = 'price is not safe'


@pytest.fixture(scope='function')
def price_feed(deploy_price_feed):
    # 5% max safe price difference
    return deploy_price_feed(max_safe_price_difference=500)


def test_max_safe_price_difference(price_feed):
    difference = price_feed.max_safe_price_difference()
    assert difference == 500


def test_safe_price_should_revert_before_any_price_set(price_feed):
    with reverts():
        price_feed.safe_price()


def test_current_price_safe(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)

    curve_pool.set_price(0.98 * 1e18)
    assert price_feed.current_price() == (0.98 * 1e18, True)

    curve_pool.set_price(0.95 * 1e18)
    assert price_feed.current_price() == (0.95 * 1e18, True)

def test_full_price_info_safe(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)

    curve_pool.set_price(0.98 * 1e18)
    assert price_feed.full_price_info() == (0.98 * 1e18, True, 1e18)

    curve_pool.set_price(0.95 * 1e18)
    assert price_feed.full_price_info() == (0.95 * 1e18, True, 1e18)


def test_current_price_safe_equals_1(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(0.99 * 1e18)
    curve_pool.set_price(1e18)
    assert price_feed.current_price() == (1e18, True)

def test_full_price_info_safe_equals_1(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(0.99 * 1e18)
    curve_pool.set_price(1e18)
    assert price_feed.full_price_info() == (1e18, True, 0.99 * 1e18)


def test_current_price_unsafe_gt_1(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(1.02 * 1e18)
    assert price_feed.current_price() == (1.02 * 1e18, False)

def test_full_price_info_unsafe_gt_1(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(1.02 * 1e18)
    assert price_feed.full_price_info() == (1.02 * 1e18, False, 1e18)


def test_current_price_unsafe_diff(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(0.949 * 1e18)
    assert price_feed.current_price() == (0.949 * 1e18, False)

    stable_swap_oracle.set_price(0.949 * 1e18)
    curve_pool.set_price(1e18)
    assert price_feed.current_price() == (1e18, False)

def test_full_price_info_unsafe_diff(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(0.949 * 1e18)
    assert price_feed.full_price_info() == (0.949 * 1e18, False, 1e18)

    stable_swap_oracle.set_price(0.949 * 1e18)
    curve_pool.set_price(1e18)
    assert price_feed.full_price_info() == (1e18, False, 0.949 * 1e18)

def test_update_safe_price(stable_swap_oracle, curve_pool, price_feed, stranger, helpers):
    prev_pool_price = 0
    pool_price = 0.98 * 1e18
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(pool_price)

    tx = price_feed.update_safe_price({'from': stranger})
    assert price_feed.safe_price() == (pool_price, chain[-1].timestamp)

    helpers.assert_single_event_named('SafePriceUpdated', tx, {
      'from_price': prev_pool_price,
      'to_price': pool_price
    })

    prev_pool_price = pool_price
    pool_price = 0.97 * 1e18
    curve_pool.set_price(pool_price)

    tx = price_feed.update_safe_price({'from': stranger})
    assert price_feed.safe_price() == (pool_price, chain[-1].timestamp)

    helpers.assert_single_event_named('SafePriceUpdated', tx, {
      'from_price': prev_pool_price,
      'to_price': pool_price
    })

    prev_pool_price = pool_price
    pool_price = 0.9 * 1e18
    curve_pool.set_price(pool_price)
    stable_swap_oracle.set_price(pool_price * 1.01)

    tx = price_feed.update_safe_price({'from': stranger})
    assert price_feed.safe_price() == (pool_price, chain[-1].timestamp)

    helpers.assert_single_event_named('SafePriceUpdated', tx, {
      'from_price': prev_pool_price,
      'to_price': pool_price
    })


def test_update_safe_price_fails_on_unsafe(stable_swap_oracle, curve_pool, price_feed, stranger):
    def assert_update_fails():
        with reverts(ERR_PRICE_NOT_SAFE):
            price_feed.update_safe_price({'from': stranger})
        with reverts(ERR_PRICE_NOT_SAFE):
            price_feed.fetch_safe_price(0, {'from': stranger})

    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(0.949 * 1e18)
    assert_update_fails()

    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(1.051 * 1e18)
    assert_update_fails()

    stable_swap_oracle.set_price(0.9 * 1e18)
    curve_pool.set_price(0.8541 * 1e18) # 0.949 * 0.9 * 1e18
    assert_update_fails()

    stable_swap_oracle.set_price(0.9 * 1e18)
    curve_pool.set_price(0.9459 * 1e18) # 1.051 * 0.9 * 1e18
    assert_update_fails()

    stable_swap_oracle.set_price(1.05 * 1e18)
    curve_pool.set_price(0.99645 * 1e18) # 0.949 * 1.05 * 1e18
    assert_update_fails()

    stable_swap_oracle.set_price(1.05 * 1e18)
    curve_pool.set_price(1.10355 * 1e18) # 1.051 * 1.05
    assert_update_fails()


def test_update_safe_price_gt_1(stable_swap_oracle, curve_pool, price_feed, stranger, helpers):
    curve_pool.set_price(1.02 * 1e18)
    stable_swap_oracle.set_price(0.98 * 1e18)
    tx = price_feed.update_safe_price({'from': stranger})

    assert price_feed.safe_price() == (1e18, chain[-1].timestamp)

    helpers.assert_single_event_named('SafePriceUpdated', tx, {
      'from_price': 0,
      'to_price': 1e18
    })

    curve_pool.set_price(1.03 * 1e18)
    stable_swap_oracle.set_price(1.01 * 1e18)
    tx = price_feed.update_safe_price({'from': stranger})

    assert price_feed.safe_price() == (1e18, chain[-1].timestamp)

    helpers.assert_single_event_named('SafePriceUpdated', tx, {
      'from_price': 1e18,
      'to_price': 1e18
    })


def test_fetch_safe_price_always_fetches_after_deploy(stable_swap_oracle, curve_pool, price_feed, stranger, helpers):
    pool_price = 0.97 * 1e18
    curve_pool.set_price(pool_price)
    stable_swap_oracle.set_price(1e18)

    max_age = 2**256 - 1 # max uint256 value
    tx = price_feed.fetch_safe_price(max_age, {'from': stranger})

    helpers.assert_single_event_named('SafePriceUpdated', tx, {
      'from_price': 0,
      'to_price': pool_price
    })


def test_fetch_safe_price_doesnt_fetch_until_expired(
    stable_swap_oracle,
    curve_pool,
    price_feed,
    stranger,
    helpers,
    PriceFetchResultHelper
):
    # calls `price_feed.fetch_safe_price` and logs the result to the `Test__PriceFetchResult` event
    helper = PriceFetchResultHelper.deploy(price_feed, {'from': stranger})

    curve_pool.set_price(1e18)
    stable_swap_oracle.set_price(1e18)

    price_feed.update_safe_price({'from': stranger})
    prev_updated_at = chain[-1].timestamp

    # set an unsafe price
    curve_pool.set_price(0.90 * 1e18)

    one_hour = 60 * 60
    tx = helper.fetch_safe_price(one_hour, {'from': stranger})

    helpers.assert_no_events_named('SafePriceUpdated', tx)
    helpers.assert_single_event_named('Test__PriceFetchResult', tx, {
      'safe_price': 1e18,
      'updated_at': prev_updated_at
    })

    assert price_feed.safe_price() == (1e18, prev_updated_at)

    chain.mine(timedelta = one_hour // 2)

    tx = helper.fetch_safe_price(one_hour, {'from': stranger})

    helpers.assert_no_events_named('SafePriceUpdated', tx)
    helpers.assert_single_event_named('Test__PriceFetchResult', tx, {
      'safe_price': 1e18,
      'updated_at': prev_updated_at
    })

    assert price_feed.safe_price() == (1e18, prev_updated_at)

    chain.mine(timedelta = one_hour // 2 + 1)

    with reverts(ERR_PRICE_NOT_SAFE):
        price_feed.fetch_safe_price(one_hour, {'from': stranger})

    pool_price = 0.96 * 1e18
    curve_pool.set_price(pool_price)

    tx = helper.fetch_safe_price(one_hour, {'from': stranger})

    helpers.assert_single_event_named('SafePriceUpdated', tx, source=price_feed, evt_keys_dict={
      'from_price': 1e18,
      'to_price': pool_price
    })

    helpers.assert_single_event_named('Test__PriceFetchResult', tx, {
      'safe_price': pool_price,
      'updated_at': chain[-1].timestamp
    })


def test_set_max_safe_price_difference_acl(price_feed, stranger):
    with reverts():
        price_feed.set_max_safe_price_difference(1000, {'from': stranger})


def test_set_max_safe_price_difference_max_check(price_feed):
    admin = price_feed.admin()
    with reverts():
        price_feed.set_max_safe_price_difference(1001, {'from': admin})


def test_set_max_safe_price_difference(price_feed, stable_swap_oracle, curve_pool, stranger, helpers):
    oracle_price = 1e18

    stable_swap_oracle.set_price(oracle_price)
    curve_pool.set_price(0.93 * 1e18)

    with reverts(ERR_PRICE_NOT_SAFE):
        price_feed.update_safe_price({'from': stranger})

    admin = price_feed.admin()
    tx = price_feed.set_max_safe_price_difference(1000, {'from': admin})

    helpers.assert_single_event_named('MaxSafePriceDifferenceChanged', tx, {
      'max_safe_price_difference': 1000
    })

    assert price_feed.max_safe_price_difference() == 1000 # 10%

    price_feed.update_safe_price({'from': stranger})


def test_set_admin(price_feed, accounts, stranger, helpers):
    with reverts():
        price_feed.set_admin(stranger, {'from': stranger})

    old_admin = price_feed.admin()
    new_admin = accounts[2]

    tx = price_feed.set_admin(new_admin, {'from': old_admin})
    assert price_feed.admin() == new_admin

    helpers.assert_single_event_named('AdminChanged', tx, {
      'admin': new_admin,
    })

    with reverts():
        price_feed.set_admin(old_admin, {'from': old_admin})

    tx = price_feed.set_admin(old_admin, {'from': new_admin})
    assert price_feed.admin() == old_admin

    helpers.assert_single_event_named('AdminChanged', tx, {
      'admin': old_admin,
    })
