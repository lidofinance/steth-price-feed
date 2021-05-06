# @version 0.2.12


admin: public(address)
max_safe_price_difference: public(uint256)
safe_price_value: public(uint256)
safe_price_timestamp: public(uint256)
curve_pool_address: public(address)
stable_swap_oracle_address: public(address)

const_price: public(uint256)


@external
def perform_upgrade(const_price: uint256):
    self.const_price = const_price


@external
def safe_price() -> (uint256, uint256):
    return (self.const_price, 42)


@external
def current_price() -> (uint256, bool):
    return (self.const_price, True)


@external
def update_safe_price() -> uint256:
    return self.const_price


@external
def fetch_safe_price(max_age: uint256) -> (uint256, uint256):
    return (self.const_price, 42)
