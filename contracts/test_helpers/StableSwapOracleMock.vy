# @version 0.2.12


price: public(uint256)


@external
def __init__(_price: uint256):
    self.price = _price


@view
@external
def stethPrice() -> uint256:
    return self.price


@external
def set_price(_price: uint256):
    self.price = _price
