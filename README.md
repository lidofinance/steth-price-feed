# Price feed for stETH/ETH pair

The feed is used to fetch stETH/ETH pair price in a safe manner, which means that the price
should be expensive to manipulate in any direction.

The price is defined as the amount of ETH wei needed to buy 1 stETH. For example, a price equal
to `10**18` would mean that stETH is pegged 1:1 to ETH.

See the detailed specification in [specification.md](./specification.md).


## Price feed interface

* `safe_price() -> (price: uint256, timestamp: uint256)` returns the cached safe price
  and its timestamp.

* `current_price() -> (price: uint256, is_safe: bool)` returns the current pool price and whether
  the price is safe.

* `update_safe_price() -> uint256` sets the cached safe price to the max(current pool price, 1)
  given that the latter is safe.

* `fetch_safe_price(max_age: uint256) -> (price: uint256, timestamp: uint256)` returns the cached
  safe price and its timestamp. Calls `update_safe_price()` prior to that if the cached safe
  price is older than `max_age` seconds.
