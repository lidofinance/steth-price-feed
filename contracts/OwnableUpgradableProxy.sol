pragma solidity 0.8.4;

import "OpenZeppelin/openzeppelin-contracts@4.0.0/contracts/proxy/Proxy.sol";
import "OpenZeppelin/openzeppelin-contracts@4.0.0/contracts/utils/Address.sol";

contract OwnableUpgradableProxy is Proxy {
    bytes32 internal constant _IMPLEMENTATION_SLOT =
        0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;
    bytes32 internal constant _OWNER_SLOT =
        0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103;

    event OwnerChanged(address previousOwner, address newOwner);
    event Upgraded(address indexed implementation);

    constructor(address _logic, bytes memory _data) payable {
        getAddressSlot(_OWNER_SLOT).value = msg.sender;
        _upgradeToAndCall(_logic, _data, false);
    }

    function _implementation() internal view override returns (address impl) {
        return getAddressSlot(_IMPLEMENTATION_SLOT).value;
    }

    function implementation() external view returns (address impl) {
        return getAddressSlot(_IMPLEMENTATION_SLOT).value;
    }

    function upgradeTo(address newImplementation) external onlyOwner {
        getAddressSlot(_IMPLEMENTATION_SLOT).value = newImplementation;
        emit Upgraded(newImplementation);
    }

    function _upgradeToAndCall(
        address newImplementation,
        bytes memory data,
        bool forceCall
    ) internal {
        getAddressSlot(_IMPLEMENTATION_SLOT).value = newImplementation;
        emit Upgraded(newImplementation);
        if (data.length > 0 || forceCall) {
            Address.functionDelegateCall(newImplementation, data);
        }
    }

    function getOwner() public view returns (address) {
        return getAddressSlot(_OWNER_SLOT).value;
    }

    function setOwner(address newOwner) public onlyOwner {
        emit OwnerChanged(getOwner(), newOwner);
        getAddressSlot(_OWNER_SLOT).value = newOwner;
    }

    modifier onlyOwner {
        require(
            msg.sender == getOwner(),
            "Only the contract owner may perform this action"
        );
        _;
    }

    struct AddressSlot {
        address value;
    }

    function getAddressSlot(bytes32 slot)
        internal
        pure
        returns (AddressSlot storage r)
    {
        assembly {
            r.slot := slot
        }
    }
}
