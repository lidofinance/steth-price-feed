# @version 0.2.12

admin: public(address)
max_safe_price_difference: public(uint256)
safe_price_value: public(uint256)
safe_price_timestamp: public(uint256)
curve_pool_address: public(address)
stable_swap_oracle_address: public(address)


interface StableSwap:
    def get_dy(i: int128, j: int128, x: uint256) -> uint256: view


interface StableSwapStateOracle:
    def stethPrice() -> uint256: view


@external
def __init__(
    max_safe_price_difference: uint256,
    stable_swap_oracle_address: address,
    curve_pool_address: address,
    admin: address
):
    """
    @notice Contract constructor
    @param max_safe_price_difference maximum allowed safe price change. 10000 equals to 100%
    @param admin Contract admin address, that's allowed to change the maximum allowed price change
    @param curve_pool_address Curve stEth/Eth pool address
    @param stable_swap_oracle_address Stable swap oracle address
    """
    self.max_safe_price_difference = max_safe_price_difference
    self.admin = admin
    self.stable_swap_oracle_address = stable_swap_oracle_address
    self.curve_pool_address = curve_pool_address


@view
@internal
def _percentage_diff(new: uint256, old: uint256) -> uint256:
    if new > old :
        return (new - old) * 10000 / old
    else:
        return (old - new) * 10000 / old


@view
@external
def safe_price() -> (uint256, uint256):
    safe_price_timestamp: uint256 = self.safe_price_timestamp
    assert safe_price_timestamp != 0
    return (self.safe_price_value, safe_price_timestamp)


@view
@internal
def _current_price() -> (uint256, bool):
    pool_price: uint256 = StableSwap(self.curve_pool_address).get_dy(1, 0, 10**18)
    shifted_price: uint256 = StableSwapStateOracle(self.stable_swap_oracle_address).stethPrice()
    is_changed_unsafely: bool = self._percentage_diff(pool_price, shifted_price) > self.max_safe_price_difference
    return (pool_price, is_changed_unsafely)


@view
@external
def current_price() -> (uint256, bool):
    price: uint256 = 0
    is_changed_unsafely: bool = True
    price, is_changed_unsafely = self._current_price()
    is_safe: bool = price <= 10**18 and not is_changed_unsafely
    return (price, is_safe)


@internal
def _update_safe_price() -> uint256:
    price: uint256 = 0
    is_changed_unsafely: bool = True
    price, is_changed_unsafely = self._current_price()
    assert not is_changed_unsafely, "price is not safe"
    self.safe_price_value = min(10**18, price)
    self.safe_price_timestamp = block.timestamp
    return price


@external
def update_safe_price() -> uint256:
    return self._update_safe_price()


@external
def fetch_safe_price(max_age: uint256) -> (uint256, uint256):
    safe_price_timestamp: uint256 = self.safe_price_timestamp
    if block.timestamp - safe_price_timestamp > max_age:
        price: uint256 = self._update_safe_price()
        return (price, block.timestamp)
    else:
        return (self.safe_price_value, safe_price_timestamp)


@external
def set_admin(admin: address):
    assert msg.sender == self.admin
    self.admin = admin


@external
def set_max_safe_price_difference(max_safe_price_difference: uint256):
    assert msg.sender == self.admin
    self.max_safe_price_difference = max_safe_price_difference
