import pytest
import scripts.deploy


@pytest.fixture(scope='function', autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]


@pytest.fixture(scope='function')
def deploy_price_feed(deployer, stable_swap_oracle, curve_pool):
    def deploy(max_safe_price_difference, deployer = deployer, admin = deployer):
        return scripts.deploy.deploy_price_feed(
            max_safe_price_difference=max_safe_price_difference,
            stable_swap_oracle_address=stable_swap_oracle,
            curve_pool_address=curve_pool,
            admin=admin,
            tx_params={'from': deployer}
        )
    return deploy


@pytest.fixture(scope='function')
def stable_swap_oracle(deployer, StableSwapOracleMock):
    return StableSwapOracleMock.deploy(1e18, {'from': deployer})


@pytest.fixture(scope='function')
def curve_pool(deployer, CurvePoolMock):
    return CurvePoolMock.deploy(1e18, {'from': deployer})


@pytest.fixture(scope='module')
def stranger(accounts):
    return accounts[9]


class Helpers:
    @staticmethod
    def filter_events_from(addr, events):
        return list(filter(lambda evt: evt.address == addr, events))

    @staticmethod
    def assert_single_event_named(evt_name, tx, evt_keys_dict = None, source = None):
        if source is None:
            source = tx.receiver
        receiver_events = Helpers.filter_events_from(source, tx.events[evt_name])
        assert len(receiver_events) == 1
        if evt_keys_dict is not None:
            assert dict(receiver_events[0]) == evt_keys_dict
        return receiver_events[0]

    @staticmethod
    def assert_no_events_named(evt_name, tx):
        assert evt_name not in tx.events



@pytest.fixture(scope='module')
def helpers():
    return Helpers
