// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @title ProofVerifier
 * @dev Cryptographic proof validation for MESHNET mining
 */
contract ProofVerifier is AccessControl {
    using ECDSA for bytes32;

    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    struct ProofData {
        bytes32 rigId;
        uint256 hashCount;
        bytes32 blockHash;
        uint256 timestamp;
        uint256 nonce;
        bytes signature;
    }

    mapping(bytes32 => bool) public usedProofHashes;
    mapping(bytes32 => uint256) public rigLastProofTime;

    uint256 public constant PROOF_COOLDOWN = 1 hours;
    uint256 public constant PROOF_VALIDITY_WINDOW = 10 minutes;

    event ProofVerified(bytes32 indexed rigId, bytes32 indexed proofHash, bool isValid);
    event ProofRejected(bytes32 indexed rigId, bytes32 indexed proofHash, string reason);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    function verifyMiningProof(
        bytes32 rigId,
        uint256 hashCount,
        bytes32 blockHash,
        uint256 timestamp,
        uint256 nonce,
        bytes memory signature,
        address expectedSigner
    ) external onlyRole(VALIDATOR_ROLE) returns (bool) {

        // Check cooldown period
        require(
            block.timestamp >= rigLastProofTime[rigId] + PROOF_COOLDOWN,
            "Proof submitted too soon"
        );

        // Check proof is not too old or too new
        require(
            block.timestamp >= timestamp && 
            block.timestamp <= timestamp + PROOF_VALIDITY_WINDOW,
            "Proof timestamp invalid"
        );

        // Generate proof hash
        bytes32 proofHash = keccak256(abi.encodePacked(
            rigId, hashCount, blockHash, timestamp, nonce
        ));

        // Check for replay attacks
        require(!usedProofHashes[proofHash], "Proof already used");

        // Verify cryptographic signature
        bool isValidSignature = _verifySignature(proofHash, signature, expectedSigner);
        if (!isValidSignature) {
            emit ProofRejected(rigId, proofHash, "Invalid signature");
            return false;
        }

        // Verify proof of work (simplified example)
        bool isValidPow = _verifyProofOfWork(proofHash, hashCount);
        if (!isValidPow) {
            emit ProofRejected(rigId, proofHash, "Invalid proof of work");
            return false;
        }

        // Mark proof as used and update timestamp
        usedProofHashes[proofHash] = true;
        rigLastProofTime[rigId] = block.timestamp;

        emit ProofVerified(rigId, proofHash, true);
        return true;
    }

    function _verifySignature(
        bytes32 hash,
        bytes memory signature,
        address expectedSigner
    ) internal pure returns (bool) {
        return hash.toEthSignedMessageHash().recover(signature) == expectedSigner;
    }

    function _verifyProofOfWork(
        bytes32 proofHash,
        uint256 claimedHashCount
    ) internal pure returns (bool) {
        // Simplified PoW verification
        // In production, this would involve more complex validation
        uint256 difficulty = uint256(proofHash) % 1000000;
        uint256 requiredDifficulty = claimedHashCount / 1000;

        return difficulty >= requiredDifficulty;
    }

    function isProofUsed(bytes32 proofHash) external view returns (bool) {
        return usedProofHashes[proofHash];
    }

    function getLastProofTime(bytes32 rigId) external view returns (uint256) {
        return rigLastProofTime[rigId];
    }
}