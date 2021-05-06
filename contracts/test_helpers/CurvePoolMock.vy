# @version 0.2.12
# @dev This is a test helper contract only, don't use it in production!


price: public(uint256)


@external
def __init__(_price: uint256):
    self.price = _price


@view
@external
def get_dy(x: int128, y: int128, dx: uint256) -> uint256:
    return self.price


@external
def set_price(_price: uint256):
    self.price = _price
