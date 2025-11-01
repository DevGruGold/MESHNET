// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title Oracle
 * @dev Decentralized oracle for off-chain data validation
 */
contract Oracle is AccessControl, ReentrancyGuard {
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    struct DataFeed {
        uint256 value;
        uint256 timestamp;
        address provider;
        bool isValid;
    }

    mapping(bytes32 => DataFeed) public dataFeeds;
    mapping(bytes32 => address[]) public feedProviders;
    mapping(address => bool) public trustedProviders;

    uint256 public constant CONSENSUS_THRESHOLD = 2; // Minimum providers for consensus
    uint256 public constant MAX_AGE = 300; // 5 minutes max age for data

    event DataUpdated(bytes32 indexed feedId, uint256 value, address provider);
    event ProviderAdded(address indexed provider);
    event ProviderRemoved(address indexed provider);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Add trusted data provider
     */
    function addProvider(address provider) external onlyRole(ADMIN_ROLE) {
        trustedProviders[provider] = true;
        _grantRole(ORACLE_ROLE, provider);
        emit ProviderAdded(provider);
    }

    /**
     * @dev Remove data provider
     */
    function removeProvider(address provider) external onlyRole(ADMIN_ROLE) {
        trustedProviders[provider] = false;
        _revokeRole(ORACLE_ROLE, provider);
        emit ProviderRemoved(provider);
    }

    /**
     * @dev Update data feed
     */
    function updateFeed(bytes32 feedId, uint256 value) 
        external 
        onlyRole(ORACLE_ROLE) 
        nonReentrant 
    {
        require(trustedProviders[msg.sender], "Not a trusted provider");

        dataFeeds[feedId] = DataFeed({
            value: value,
            timestamp: block.timestamp,
            provider: msg.sender,
            isValid: true
        });

        emit DataUpdated(feedId, value, msg.sender);
    }

    /**
     * @dev Get latest data with freshness check
     */
    function getLatestData(bytes32 feedId) 
        external 
        view 
        returns (uint256 value, uint256 timestamp, bool isValid) 
    {
        DataFeed memory feed = dataFeeds[feedId];
        bool isFresh = (block.timestamp - feed.timestamp) <= MAX_AGE;

        return (feed.value, feed.timestamp, feed.isValid && isFresh);
    }
}