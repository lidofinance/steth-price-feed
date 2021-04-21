from brownie import network, accounts
import os


def get_is_live():
    return network.show_active() != 'development'


def get_env(name, is_required=True, message=None, default=None):
    if name not in os.environ:
        if is_required:
            raise EnvironmentError(message or f'Please set {name} env variable')
        else:
            return default
    return os.environ[name]


def get_deployer_account(is_live):
    if is_live and 'DEPLOYER' not in os.environ:
        raise EnvironmentError(
            'Please set DEPLOYER env variable to the deployer account name')

    return accounts.load(os.environ['DEPLOYER']) if is_live else accounts[0]


def prompt_bool():
    choice = input().lower()
    if choice in {'yes', 'y'}:
        return True
    elif choice in {'no', 'n'}:
        return False
    else:
        print("Please respond with 'yes' or 'no'")
