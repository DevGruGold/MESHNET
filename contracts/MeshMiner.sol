// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./XMRT.sol";

/**
 * @title MeshMiner
 * @dev Core mining operations contract for MESHNET
 */
contract MeshMiner is AccessControl, ReentrancyGuard, Pausable {
    using ECDSA for bytes32;

    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    XMRT public xmrtToken;

    struct Rig {
        bytes32 rigId;
        address owner;
        uint256 totalHashes;
        uint256 lastSubmission;
        bool isActive;
        uint256 reputationScore;
    }

    struct ProofSubmission {
        bytes32 rigId;
        uint256 hashCount;
        uint256 timestamp;
        bytes32 blockHash;
        bytes signature;
        bool verified;
    }

    mapping(bytes32 => Rig) public rigs;
    mapping(bytes32 => ProofSubmission[]) public rigProofs;
    mapping(address => bytes32[]) public ownerRigs;

    uint256 public constant MIN_HASH_THRESHOLD = 1000;
    uint256 public constant PROOF_VALIDITY_PERIOD = 1 hours;
    uint256 public constant BASE_REWARD_RATE = 100; // Base tokens per 1000 hashes

    event RigRegistered(bytes32 indexed rigId, address indexed owner);
    event ProofSubmitted(bytes32 indexed rigId, uint256 hashCount, uint256 timestamp);
    event RewardDistributed(address indexed miner, uint256 amount);
    event RigSlashed(bytes32 indexed rigId, uint256 penalty);

    constructor(address _xmrtToken) {
        xmrtToken = XMRT(_xmrtToken);
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Register a new mining rig
     */
    function registerRig(bytes32 rigId, address owner) 
        external 
        onlyRole(VALIDATOR_ROLE) 
        whenNotPaused 
    {
        require(rigs[rigId].owner == address(0), "Rig already registered");
        require(owner != address(0), "Invalid owner address");

        rigs[rigId] = Rig({
            rigId: rigId,
            owner: owner,
            totalHashes: 0,
            lastSubmission: 0,
            isActive: true,
            reputationScore: 100 // Start with base reputation
        });

        ownerRigs[owner].push(rigId);
        emit RigRegistered(rigId, owner);
    }

    /**
     * @dev Submit mining proof with cryptographic validation
     */
    function submitProof(
        bytes32 rigId,
        uint256 hashCount,
        bytes32 blockHash,
        bytes memory signature
    ) external onlyRole(VALIDATOR_ROLE) nonReentrant whenNotPaused {
        require(rigs[rigId].isActive, "Rig not active");
        require(hashCount >= MIN_HASH_THRESHOLD, "Hash count below threshold");
        require(
            block.timestamp - rigs[rigId].lastSubmission >= PROOF_VALIDITY_PERIOD,
            "Proof submitted too soon"
        );

        // Verify proof signature
        bytes32 proofHash = keccak256(abi.encodePacked(rigId, hashCount, blockHash, block.timestamp));
        require(_verifySignature(proofHash, signature, rigs[rigId].owner), "Invalid proof signature");

        // Store proof
        rigProofs[rigId].push(ProofSubmission({
            rigId: rigId,
            hashCount: hashCount,
            timestamp: block.timestamp,
            blockHash: blockHash,
            signature: signature,
            verified: true
        }));

        // Update rig stats
        rigs[rigId].totalHashes += hashCount;
        rigs[rigId].lastSubmission = block.timestamp;

        // Calculate and distribute rewards
        uint256 rewardAmount = calculateReward(hashCount, rigs[rigId].reputationScore);
        xmrtToken.rewardFromMesh(rigs[rigId].owner, rewardAmount);

        emit ProofSubmitted(rigId, hashCount, block.timestamp);
        emit RewardDistributed(rigs[rigId].owner, rewardAmount);
    }

    /**
     * @dev Calculate reward based on hash count and reputation
     */
    function calculateReward(uint256 hashCount, uint256 reputationScore) 
        public 
        pure 
        returns (uint256) 
    {
        uint256 baseReward = (hashCount * BASE_REWARD_RATE) / 1000;
        uint256 reputationMultiplier = (reputationScore * 100) / 100; // Normalize to percentage
        return (baseReward * reputationMultiplier) / 100;
    }

    /**
     * @dev Slash a rig for malicious behavior
     */
    function slashRig(bytes32 rigId, uint256 penalty) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        require(rigs[rigId].owner != address(0), "Rig not found");
        require(penalty <= rigs[rigId].reputationScore, "Penalty exceeds reputation");

        rigs[rigId].reputationScore -= penalty;

        if (rigs[rigId].reputationScore < 50) {
            rigs[rigId].isActive = false;
        }

        emit RigSlashed(rigId, penalty);
    }

    /**
     * @dev Get rig information
     */
    function getRigInfo(bytes32 rigId) 
        external 
        view 
        returns (
            address owner,
            uint256 totalHashes,
            uint256 lastSubmission,
            bool isActive,
            uint256 reputationScore
        ) 
    {
        Rig memory rig = rigs[rigId];
        return (
            rig.owner,
            rig.totalHashes,
            rig.lastSubmission,
            rig.isActive,
            rig.reputationScore
        );
    }

    /**
     * @dev Get proof count for a rig
     */
    function getProofCount(bytes32 rigId) external view returns (uint256) {
        return rigProofs[rigId].length;
    }

    /**
     * @dev Get rigs owned by an address
     */
    function getOwnerRigs(address owner) external view returns (bytes32[] memory) {
        return ownerRigs[owner];
    }

    /**
     * @dev Verify cryptographic signature
     */
    function _verifySignature(
        bytes32 hash,
        bytes memory signature,
        address expectedSigner
    ) internal pure returns (bool) {
        return hash.toEthSignedMessageHash().recover(signature) == expectedSigner;
    }

    /**
     * @dev Emergency pause
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
}