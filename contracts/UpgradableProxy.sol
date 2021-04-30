// SPDX-License-Identifier: MIT

pragma solidity 0.8.4;

import "OpenZeppelin/openzeppelin-contracts@4.0.0/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import "OpenZeppelin/openzeppelin-contracts@4.0.0/contracts/utils/Address.sol";

/**
 * @dev Copied from https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.1.0/contracts/utils/StorageSlot.sol
 */
library StorageSlot {
    struct AddressSlot {
        address value;
    }

    function getAddressSlot(bytes32 slot) internal pure returns (AddressSlot storage r) {
        assembly {
            r.slot := slot
        }
    }
}

contract UpgradableProxy is ERC1967Proxy {
    /**
     * @dev Storage slot with the admin of the contract.
     * This is the keccak-256 hash of "eip1967.proxy.admin" subtracted by 1, and is
     * validated in the constructor.
     */
    bytes32 internal constant _ADMIN_SLOT = 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103;

    /**
     * @dev Emitted when the admin account has changed.
     */
    event AdminChanged(address previousAdmin, address newAdmin);

    /**
     * @dev Initializes the upgradeable proxy with an initial implementation specified by `logic`.
     *
     * If `data` is nonempty, it's used as data in a delegate call to `logic`. This will typically
     * be an encoded function call, and allows initializating the storage of the proxy like
     * a Solidity constructor.
     */
    constructor(address logic, bytes memory data) payable ERC1967Proxy(logic, data) {
        _setAdmin(msg.sender);
    }

    /**
     * @dev Returns the current implementation address.
     */
    function implementation() external view returns (address) {
        return _implementation();
    }

    /**
     * @dev Upgrades the proxy to a new implementation.
     *
     * Emits an {Upgraded} event.
     */
    function upgradeTo(address newImplementation) external {
        require(msg.sender == _getAdmin(), "ERC1967: unauthorized");
        _upgradeTo(newImplementation);
    }

    /**
     * @dev Returns the current admin.
     */
    function _getAdmin() internal view returns (address) {
        return StorageSlot.getAddressSlot(_ADMIN_SLOT).value;
    }

    /**
     * @dev Stores a new address in the EIP1967 admin slot.
     */
    function _setAdmin(address newAdmin) private {
        StorageSlot.getAddressSlot(_ADMIN_SLOT).value = newAdmin;
    }

    /**
     * @dev Returns the current admin of the proxy.
     */
    function getProxyAdmin() external view returns (address) {
        return _getAdmin();
    }

    /**
     * @dev Changes the admin of the proxy.
     *
     * Emits an {AdminChanged} event.
     */
    function changeProxyAdmin(address newAdmin) external {
        address admin = _getAdmin();
        require(msg.sender == admin, "ERC1967: unauthorized");
        emit AdminChanged(admin, newAdmin);
        _setAdmin(newAdmin);
    }
}
