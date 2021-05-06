# @version 0.2.12
# @dev This is a test helper contract only, don't use it in production!


interface PriceFeed:
    def fetch_safe_price(max_age: uint256) -> (uint256, uint256): nonpayable


event Test__PriceFetchResult:
    safe_price: uint256
    updated_at: uint256


price_feed: address


@external
def __init__(price_feed: address):
    self.price_feed = price_feed


@external
def fetch_safe_price(max_age: uint256):
    safe_price: uint256 = 0
    updated_at: uint256 = 0
    (safe_price, updated_at) = PriceFeed(self.price_feed).fetch_safe_price(max_age)
    log Test__PriceFetchResult(safe_price, updated_at)
