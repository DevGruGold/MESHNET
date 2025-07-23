// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title Treasury
 * @dev Multi-signature treasury management for MESHNET DAO
 */
contract Treasury is AccessControl, ReentrancyGuard {
    bytes32 public constant TREASURER_ROLE = keccak256("TREASURER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 confirmations;
        mapping(address => bool) isConfirmed;
    }

    mapping(uint256 => Transaction) public transactions;
    uint256 public transactionCount;
    uint256 public requiredConfirmations;
    address[] public treasurers;

    event TransactionSubmitted(uint256 indexed txId, address indexed to, uint256 value);
    event TransactionConfirmed(uint256 indexed txId, address indexed treasurer);
    event TransactionExecuted(uint256 indexed txId);
    event TreasurerAdded(address indexed treasurer);
    event TreasurerRemoved(address indexed treasurer);

    constructor(address[] memory _treasurers, uint256 _requiredConfirmations) {
        require(_treasurers.length > 0, "Treasurers required");
        require(_requiredConfirmations > 0 && _requiredConfirmations <= _treasurers.length, "Invalid confirmation count");

        for (uint256 i = 0; i < _treasurers.length; i++) {
            treasurers.push(_treasurers[i]);
            _grantRole(TREASURER_ROLE, _treasurers[i]);
        }

        requiredConfirmations = _requiredConfirmations;
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    receive() external payable {}

    function submitTransaction(address to, uint256 value, bytes memory data) 
        external 
        onlyRole(TREASURER_ROLE) 
        returns (uint256) 
    {
        uint256 txId = transactionCount++;
        Transaction storage transaction = transactions[txId];

        transaction.to = to;
        transaction.value = value;
        transaction.data = data;
        transaction.executed = false;
        transaction.confirmations = 0;

        emit TransactionSubmitted(txId, to, value);
        return txId;
    }

    function confirmTransaction(uint256 txId) external onlyRole(TREASURER_ROLE) {
        require(txId < transactionCount, "Transaction does not exist");
        require(!transactions[txId].executed, "Transaction already executed");
        require(!transactions[txId].isConfirmed[msg.sender], "Transaction already confirmed");

        transactions[txId].isConfirmed[msg.sender] = true;
        transactions[txId].confirmations++;

        emit TransactionConfirmed(txId, msg.sender);

        if (transactions[txId].confirmations >= requiredConfirmations) {
            executeTransaction(txId);
        }
    }

    function executeTransaction(uint256 txId) public nonReentrant {
        require(txId < transactionCount, "Transaction does not exist");
        require(!transactions[txId].executed, "Transaction already executed");
        require(transactions[txId].confirmations >= requiredConfirmations, "Insufficient confirmations");

        Transaction storage transaction = transactions[txId];
        transaction.executed = true;

        (bool success, ) = transaction.to.call{value: transaction.value}(transaction.data);
        require(success, "Transaction execution failed");

        emit TransactionExecuted(txId);
    }
}