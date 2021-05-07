from brownie import Contract
from utils.config import get_deployer_account, get_is_live, get_env, prompt_bool

try:
    from brownie import StEthPriceFeed, PriceFeedProxy
except ImportError:
    print("You're probably running inside Brownie console. Please call:")
    print("set_console_globals(StEthPriceFeed=StEthPriceFeed, PriceFeedProxy=PriceFeedProxy)")


def set_console_globals(**kwargs):
    global StEthPriceFeed
    global PriceFeedProxy
    StEthPriceFeed = kwargs['StEthPriceFeed']
    PriceFeedProxy = kwargs['PriceFeedProxy']


def deploy_price_feed(
    max_safe_price_difference,
    stable_swap_oracle_address,
    curve_pool_address,
    admin,
    tx_params
):
    price_feed_contract = StEthPriceFeed.deploy(tx_params, publish_source=False)
    proxy = PriceFeedProxy.deploy(
        price_feed_contract,
        max_safe_price_difference,
        stable_swap_oracle_address,
        curve_pool_address,
        admin,
        tx_params
    )
    return Contract.from_abi('StEthPriceFeed', proxy.address, StEthPriceFeed.abi)


def main():
    deployer = get_deployer_account(get_is_live())
    stable_swap_oracle_address = get_env('STABLE_SWAP_ORACLE_ADDRESS', True)
    curve_pool_address = get_env('CURVE_POOL_ADDRESS', True)
    max_safe_price_difference = get_env('MAX_SAFE_PRICE_DIFFERENCE', False, default=500)
    admin = get_env('ADMIN', False, default=deployer)

    print(f'Deployer: {deployer}')
    print(f'Stable swap oracle address: {stable_swap_oracle_address}')
    print(f'Curve pool oracle address: {curve_pool_address}')
    print(
        f'Max safe price difference: {max_safe_price_difference} '
        f'({max_safe_price_difference / 100}%)'
    )
    print(f'Admin: {admin}')
    print('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    deploy_price_feed(
        max_safe_price_difference,
        stable_swap_oracle_address,
        curve_pool_address,
        admin,
        tx_params={'from': deployer}
    )
