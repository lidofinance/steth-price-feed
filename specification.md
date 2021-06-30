# stETH Price Oracle

Lido intends to provide secure and reliable price feed for stETH for protocols that intend to integrate it. Unfortunately, Chainlink is not available for stETH, and Uniswap TWAP is not feasible at the moment: we'd want deep liquidity on stETH/ETH pair for this price, but Uni v2 doesn't allow tight curves for similaraly-priced coins.

stETH has deep liquidity in the [Curve pool](https://etherscan.io/address/0xdc24316b9ae028f1497c275eb9192a3ea0f67022) but it doesn't have a TWAP capability, so that's out, too. In the moment Curve price is flashloanable, if not easily. We decided that in a pinch we can provide a "price anchor" that would attest that "stETH/ETH price on Curve used to be around in recent past" (implemented using the Merkle price oracle) and a price feed that could provide a reasonably safe estimation of current stETH/ETH price.

## Vocabulary

* **Current price**—current price of stETH on Curve pool. Flashloanable.
* **Historical price**—the price of stETH on Curve pool that was at least 15 blocks ago. May be older than 15 blocks: in that case, the pool price that was 15 blocks ago differs from the "historical price" by no more than `N`%.
* **Safe price range**—the range from `historical price - N%` to `min(historical price + N%, 1)`.
* **Safe price**—the price that's within the safe price range.

The parameter `N` is configured by the price feed admin; we're planning to initially set it to `5%`.

## stETH price feed specification

The feed is used to fetch stETH/ETH pair price in a safe manner. By "safe" we mean that the price should be expensive to significantly manipulate in any direction, e.g. using flash loans or sandwich attacks.

The feed should initially interface with two contracts:

1. Curve stETH/ETH pool: [source](https://github.com/curvefi/curve-contract/blob/c6df0cf/contracts/pools/steth/StableSwapSTETH.vy), [deployed contract](https://etherscan.io/address/0xdc24316b9ae028f1497c275eb9192a3ea0f67022).
2. Curve stETH/ETH pool Merkle oracle: [source](https://github.com/lidofinance/curve-merkle-oracle).

The pool is used as the main price source, and the oracle provides time-shifted price from the same pool used to establish a safe price range.


### The safe price range

The price is defined as the amount of ETH wei needed to buy 1 stETH. For example, a price equal to `10**18` would mean that stETH is pegged 1:1 to ETH.

The safe price is defined as the one that satisfies all of the following conditions:

* The absolute value of percentage difference between the safe price and the time-shifted price fetched from the Merkle oracle is at most `max_safe_price_difference`.
* The safe price is at most `10**18`, meaning that stETH cannot be more expensive than ETH.


### Future upgrades

The feed contract should be put behind an upgradeable proxy so the implementation can be upgraded when new price sources appear.


### Interface

##### `initialize(max_safe_price_difference: uint256, stable_swap_oracle_address: address, curve_pool_address: address, admin: address)`

Initializes the contract. Reverts if 1) `max_safe_price_difference` is above 10000, 2) `stable_swap_oracle_address` or `curve_pool_address` are zero addresses, 3) contract is already initiated.

* `max_safe_price_difference` maximum allowed safe price change: how much the price fetched from the pool is allowed to deviate from the time-shifted price provided by the Merkle oracle in order to be considered safe; `10**18` corresponds to 100%.
* `stable_swap_oracle_address` the address of the time-shifted price oracle.
* `curve_pool_address` the address of the ETH/stETH curve pool.
* `admin` the address that's allowed to change the maximum allowed price change.


##### `safe_price() -> (price: uint256, timestamp: uint256)`

Returns the cached safe price and its timestamp. Reverts if no cached price was set.

```python
@view
def safe_price():
  assert self.safe_price_timestamp != 0
  return (self.safe_price, self.safe_price_timestamp)
```


##### `current_price() -> (price: uint256, is_safe: bool)`

Returns the current pool price & whether the price is safe.

```python
@view
def _current_price():
  pool_price = StableSwap(CURVE_POOL_ADDR).get_dy(1, 0, 10**18)
  shifted_price = StableSwapStateOracle(ORACLE_ADDR).stethPrice()
  has_changed_unsafely = self.percentage_diff(pool_price, shifted_price) > self.max_safe_price_difference
  return (pool_price, has_changed_unsafely, shifted_price)

@view
def current_price():
    (price, has_changed_unsafely, _) = self._current_price()
    is_safe = price <= 10**18 and not has_changed_unsafely
    return (price, is_safe)
```

##### `full_price_info() -> (price: uint256, is_safe: bool, anchor_price: uint256)`

Returns the current pool price, whether the price is safe, and the current time-shifted price.

```python
@view
def _current_price():
  pool_price = StableSwap(CURVE_POOL_ADDR).get_dy(1, 0, 10**18)
  shifted_price = StableSwapStateOracle(ORACLE_ADDR).stethPrice()
  has_changed_unsafely = self.percentage_diff(pool_price, shifted_price) > self.max_safe_price_difference
  return (pool_price, has_changed_unsafely, shifted_price)

@view
def full_price_info():
    (price, has_changed_unsafely, shifted_price) = self._current_price()
    is_safe = price <= 10**18 and not has_changed_unsafely
    return (price, is_safe, shifted_price)
```


##### `update_safe_price() -> uint256`

Sets the cached safe price to the current pool price.

If the price is higher than `10**18`, sets the cached safe price to `10**18`. If the price is not safe for any other reason, reverts.

```python
def update_safe_price():
  (price, is_changed_unsafely) = self._current_price()
  assert not is_changed_unsafely, "price is not safe"
  self.safe_price = max(price, 10**18)
  self.safe_price_timestamp = block.timestamp
  return price
```


##### `fetch_safe_price(max_age: uint256) -> (price: uint256, timestamp: uint256)`

Returns the cached safe price and its timestamp. Calls `update_safe_price()` prior to that if the cached safe price is older than `max_age` seconds (note: that call reverts, if the price is unsafe).

```python
def fetch_safe_price(max_age):
  if block.timestamp - self.safe_price_timestamp > max_age:
    price = self.update_safe_price()
    return (price, block.timsetamp)
  else:
    return (self.safe_price, self.safe_price_timestamp)
```


##### `set_admin(admin: address)`

Updates the admin address. May only be called by the current admin.


##### `set_max_safe_price_difference(max_safe_price_difference: uint256)`

Updates the maximum difference between the safe price and the time-shifted price. May only be called by the admin. Reverts if the number provided is above 10000.

## Fail conditions

Price feed can give incorrect data in, as far as we can tell, three situations:

- stETH/ETH price moving suddenly and very quickly. There is at least 15 blocks delay between price drop and offchain oracle feed providers submitting a new historical price, and likely more bc tx are not mined instanteously. That should not happen normally: while stETH/ETH is volatile, it's not 5%-in-four-minutes volatile.
- oracle feed going stale because feed providers go offline. This is mitigated by the fact it's operated by several very experienced professionals (all of which, e.g., are Chainlink operators too) - and we only need one operational provider to maintain the feed. The only realistic scenario where this feed goes offline is deprecating the oracle alltogether.
- Multi-block flashloan attack. An block producer who is able to reliably get 2 blocks in a row can treat two blocks as an atomic transaction, leading to what is essentially a multiblock flashloan attack to manipulate price. That can lead to a short period of time (a few blocks) where stETH/ETH price feed is artificially manipulated. This attack is not mitigated, but in our opinion, not very realistic. It's very hard to pull off.


## Further upgrade plans

+ Balancer + Univ3 + Chainlink + ???
