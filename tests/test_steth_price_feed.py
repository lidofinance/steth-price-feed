from brownie import chain, reverts


def test_max_safe_price_difference(price_feed):
    price_feed.max_safe_price_difference()


def test_safe_price_should_reverts_on_price_set(price_feed):
    with reverts():
        price_feed.safe_price()


def test_safe_current_price(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    assert price_feed.current_price() == (9.8 * 1e17, True)


def test_unsafe_current_price_gte_1(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(1.02 * 1e18)
    assert price_feed.current_price() == (1.02 * 1e18, False)


def test_unsafe_current_price_diff_gt_max_diff(stable_swap_oracle, curve_pool, price_feed):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.4 * 1e17)
    assert price_feed.current_price() == (9.4 * 1e17, False)


def test_update_safe_price(stable_swap_oracle, curve_pool, price_feed, stranger):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    price_feed.update_safe_price({'from': stranger})
    assert price_feed.safe_price() == (9.8 * 1e17, chain[-1].timestamp)


def test_update_safe_price_fails_on_unsafe(stable_swap_oracle, curve_pool, price_feed, stranger):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    price_feed.update_safe_price({'from': stranger})
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9 * 1e17)
    with reverts('price is not safe'):
        price_feed.update_safe_price({'from': stranger})


def test_update_safe_price_with_gt_1(stable_swap_oracle, curve_pool, price_feed, stranger):
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(9.8 * 1e17)
    price_feed.update_safe_price({'from': stranger})
    stable_swap_oracle.set_price(1e18)
    curve_pool.set_price(1.02 * 1e18)
    price_feed.update_safe_price({'from': stranger})
    assert price_feed.safe_price() == (1e18, chain[-1].timestamp)


def test_set_admin(price_feed, accounts):
    old_admin = price_feed.admin()
    new_admin = accounts[2]
    price_feed.set_admin(new_admin, {'from': old_admin})
    assert price_feed.admin() == new_admin
    price_feed.set_admin(old_admin, {'from': new_admin})


def test_set_admin_acl_fails(price_feed, stranger):
    new_admin = stranger
    with reverts():
        price_feed.set_admin(new_admin, {'from': new_admin})


def test_set_max_safe_price_difference(price_feed):
    admin = price_feed.admin()
    price_feed.set_max_safe_price_difference(5000, {'from': admin})
    assert price_feed.max_safe_price_difference() == 5000


def test_set_max_safe_price_difference_acl_fails(price_feed, stranger):
    with reverts():
        price_feed.set_max_safe_price_difference(5000, {'from': stranger})
