from brownie import reverts, ZERO_ADDRESS


def test_uninitialized_contract_reverts(deployer, stranger, StEthPriceFeed):
    price_feed = StEthPriceFeed.deploy({'from': deployer})

    with reverts():
        price_feed.safe_price()

    with reverts():
        price_feed.current_price()

    with reverts():
        price_feed.update_safe_price({'from': deployer})

    with reverts():
        price_feed.fetch_safe_price(0, {'from': deployer})

    with reverts():
        price_feed.fetch_safe_price(1000 * 60 * 60 * 24 * 365, {'from': deployer})

    with reverts():
        price_feed.set_admin(stranger, {'from': deployer})

    with reverts():
        price_feed.set_max_safe_price_difference(142, {'from': deployer})

def test_cannot_initialize_with_zero_curve_address(deployer, stable_swap_oracle, StEthPriceFeed):
    price_feed = StEthPriceFeed.deploy({'from': deployer})
    with reverts():
        price_feed.initialize(
            100,
            stable_swap_oracle.address,
            ZERO_ADDRESS,
            deployer,
            {'from': deployer}
        )

def test_cannot_initialize_with_zero_oracle_address(deployer, curve_pool, StEthPriceFeed):
    price_feed = StEthPriceFeed.deploy({'from': deployer})
    with reverts():
        price_feed.initialize(
            100,
            ZERO_ADDRESS,
            curve_pool.address,
            deployer,
            {'from': deployer}
        )

def test_can_initialize_with_zero_admin_address(deployer, stable_swap_oracle, curve_pool, StEthPriceFeed):
    price_feed = StEthPriceFeed.deploy({'from': deployer})
    price_feed.initialize(
        100,
        stable_swap_oracle.address,
        curve_pool.address,
        ZERO_ADDRESS,
        {'from': deployer}
    )
    assert price_feed.admin() == ZERO_ADDRESS

def test_cannot_initialize_with_max_price_diff_above_1000(deployer, stable_swap_oracle, curve_pool, StEthPriceFeed):
    price_feed = StEthPriceFeed.deploy({'from': deployer})
    with reverts():
        price_feed.initialize(
            1001,
            stable_swap_oracle.address,
            curve_pool.address,
            ZERO_ADDRESS,
            {'from': deployer}
        )


def test_cannot_initialize_twice(deployer, stable_swap_oracle, curve_pool, StEthPriceFeed):
    price_feed = StEthPriceFeed.deploy({'from': deployer})

    def initialize(max_safe_price_difference):
        price_feed.initialize(
            max_safe_price_difference,
            stable_swap_oracle.address,
            curve_pool.address,
            deployer,
            {'from': deployer}
        )

    initialize(142)

    with reverts():
        initialize(142)

    with reverts():
        initialize(153)

