// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title ReputationSystem
 * @dev Miner reputation and trust scoring for MESHNET
 */
contract ReputationSystem is AccessControl {
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    struct ReputationRecord {
        uint256 score;
        uint256 totalProofs;
        uint256 validProofs;
        uint256 invalidProofs;
        uint256 lastUpdate;
        bool isBlacklisted;
    }

    mapping(bytes32 => ReputationRecord) public reputations;
    mapping(address => bytes32[]) public minerRigs;

    uint256 public constant BASE_SCORE = 100;
    uint256 public constant MAX_SCORE = 1000;
    uint256 public constant MIN_SCORE = 0;
    uint256 public constant VALID_PROOF_BONUS = 5;
    uint256 public constant INVALID_PROOF_PENALTY = 10;

    event ReputationUpdated(bytes32 indexed rigId, uint256 newScore);
    event RigBlacklisted(bytes32 indexed rigId, string reason);
    event RigWhitelisted(bytes32 indexed rigId);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    function initializeReputation(bytes32 rigId, address miner) 
        external 
        onlyRole(VALIDATOR_ROLE) 
    {
        require(reputations[rigId].lastUpdate == 0, "Reputation already initialized");

        reputations[rigId] = ReputationRecord({
            score: BASE_SCORE,
            totalProofs: 0,
            validProofs: 0,
            invalidProofs: 0,
            lastUpdate: block.timestamp,
            isBlacklisted: false
        });

        minerRigs[miner].push(rigId);
        emit ReputationUpdated(rigId, BASE_SCORE);
    }

    function updateReputationOnValidProof(bytes32 rigId) 
        external 
        onlyRole(VALIDATOR_ROLE) 
    {
        require(reputations[rigId].lastUpdate > 0, "Reputation not initialized");
        require(!reputations[rigId].isBlacklisted, "Rig is blacklisted");

        ReputationRecord storage record = reputations[rigId];
        record.totalProofs++;
        record.validProofs++;

        if (record.score < MAX_SCORE) {
            record.score = _min(record.score + VALID_PROOF_BONUS, MAX_SCORE);
        }

        record.lastUpdate = block.timestamp;
        emit ReputationUpdated(rigId, record.score);
    }

    function updateReputationOnInvalidProof(bytes32 rigId, string memory reason) 
        external 
        onlyRole(VALIDATOR_ROLE) 
    {
        require(reputations[rigId].lastUpdate > 0, "Reputation not initialized");

        ReputationRecord storage record = reputations[rigId];
        record.totalProofs++;
        record.invalidProofs++;
        record.score = _max(record.score - INVALID_PROOF_PENALTY, MIN_SCORE);

        // Blacklist if score drops too low or too many invalid proofs
        if (record.score <= 20 || (record.invalidProofs * 100) / record.totalProofs > 50) {
            record.isBlacklisted = true;
            emit RigBlacklisted(rigId, reason);
        }

        record.lastUpdate = block.timestamp;
        emit ReputationUpdated(rigId, record.score);
    }

    function blacklistRig(bytes32 rigId, string memory reason) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        reputations[rigId].isBlacklisted = true;
        emit RigBlacklisted(rigId, reason);
    }

    function whitelistRig(bytes32 rigId) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        reputations[rigId].isBlacklisted = false;
        emit RigWhitelisted(rigId);
    }

    function getReputationScore(bytes32 rigId) 
        external 
        view 
        returns (uint256) 
    {
        return reputations[rigId].score;
    }

    function isRigTrustworthy(bytes32 rigId) 
        external 
        view 
        returns (bool) 
    {
        return reputations[rigId].score >= 50 && !reputations[rigId].isBlacklisted;
    }

    function _min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }

    function _max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }
}