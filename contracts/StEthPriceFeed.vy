# @version ^0.2.12

admin: public(address)
max_safe_price_difference: public(uint256)
_safe_price: public(uint256)
safe_price_timestamp: public(uint256)
curve_pool_address: public(address)
stable_swap_oracle_address: public(address)


interface StableSwap:
    def get_dy(i: int128, j: int128, x: uint256) -> uint256: view


interface StableSwapStateOracle:
    def stethPrice() -> uint256: view


@external
def __init__(_max_safe_price_difference: uint256, _stable_swap_oracle_address: address, _curve_pool_address: address, _admin: address):
    """
    @notice Contract constructor
    @param _max_safe_price_difference maximum allowed safe price change. 10000 equals to 100%
    @param _admin Contract admin address, that's allowed to change the maximum allowed price change
    @param _curve_pool_address Curve stEth/Eth pool address
    @param _stable_swap_oracle_address Stable swap oracle address
    """
    self.max_safe_price_difference = _max_safe_price_difference
    self.admin = _admin
    self.stable_swap_oracle_address = _stable_swap_oracle_address
    self.curve_pool_address = _curve_pool_address


@view
@internal
def percentage_diff(new: uint256, old: uint256) -> uint256:
    if new > old :
        return (new - old)*10000/old
    else:
        return (old - new)*10000/old


@view
@external
def safe_price() -> (uint256, uint256):
    assert self.safe_price_timestamp != 0
    return (self._safe_price, self.safe_price_timestamp)


@view
@internal
def _current_price() -> (uint256, bool):
    pool_price: uint256 = StableSwap(self.curve_pool_address).get_dy(1, 0, 10**18)
    shifted_price: uint256 = StableSwapStateOracle(self.stable_swap_oracle_address).stethPrice()
    is_changed_unsafely: bool = self.percentage_diff(pool_price, shifted_price) > self.max_safe_price_difference
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
    self._safe_price = min(10**18, price)
    self.safe_price_timestamp = block.timestamp
    return price


@external
def update_safe_price() -> uint256:
    return self._update_safe_price()


@external
def fetch_safe_price(max_age: uint256) -> (uint256, uint256):
  if block.timestamp - self.safe_price_timestamp > max_age:
    price:uint256 = self._update_safe_price()
    return (price, block.timestamp)
  else:
    return (self._safe_price, self.safe_price_timestamp)


@external
def set_admin(_admin: address):
    assert msg.sender == self.admin
    self.admin = _admin


@external
def set_max_safe_price_difference(max_safe_price_difference: uint256):
    assert msg.sender == self.admin
    self.max_safe_price_difference = max_safe_price_difference
