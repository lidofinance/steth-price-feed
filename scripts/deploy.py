import sys, os
from brownie import (StEthPriceFeed, UpgradableProxy, Contract)
from brownie.convert import to_bytes
from utils.config import (get_deployer_account, get_is_live, get_env,
                          prompt_bool)


def deploy_stEth_price_feed(max_safe_price_difference,
                            stable_swap_oracle_address, curve_pool_address,
                            admin, tx_params):
    price_feed_contract = StEthPriceFeed.deploy(tx_params,
                                                publish_source=False)
    call_data = price_feed_contract.initialize.encode_input(
        max_safe_price_difference, stable_swap_oracle_address,
        curve_pool_address, admin)
    proxy = UpgradableProxy.deploy(price_feed_contract,
                                         call_data,
                                         tx_params,
                                         publish_source=False)
    return Contract.from_abi('StEthPriceFeed', proxy.address, StEthPriceFeed.abi)


def main():
    deployer = get_deployer_account(get_is_live())
    stable_swap_oracle_address = get_env("STABLE_SWAP_ORACLE_ADDRESS", True)
    curve_pool_address = get_env("CURVE_POOL_ADDRESS", True)
    max_safe_price_difference = get_env("MAX_SAFE_PRICE_DIFFERENCE",
                                        False,
                                        default=500)
    admin = get_env("ADMIN", False, default=deployer)

    print(f'DEPLOYER: {deployer}')
    print(f'Stable swap oracle address: {stable_swap_oracle_address}')
    print(f'Curve pool oracle address: {curve_pool_address}')
    print(
        f'Max safe price difference: {max_safe_price_difference} ({max_safe_price_difference/100} %)'
    )
    print(f'Admin: {admin}')
    print('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    deploy_stEth_price_feed(max_safe_price_difference,
                            stable_swap_oracle_address,
                            curve_pool_address,
                            admin,
                            tx_params={"from": deployer})
