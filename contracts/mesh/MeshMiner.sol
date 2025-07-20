// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";

interface IXMRT {
    function rewardFromMesh(address to, uint256 amount) external;
}

contract MeshMiner is AccessControl {
    bytes32 public constant MESH_VALIDATOR_ROLE = keccak256("MESH_VALIDATOR_ROLE");

    mapping(bytes32 => address) public rigIdToOwner;
    mapping(bytes32 => uint256) public rigIdToHashes;

    event RigRegistered(bytes32 indexed rigId, address indexed owner);
    event ProofSubmitted(bytes32 indexed rigId, uint256 hashes, bytes signature);
    event RewardDistributed(address indexed miner, uint256 rewardAmount);

    IXMRT public xmrtContract;

    constructor(address _xmrtAddress) {
        xmrtContract = IXMRT(_xmrtAddress);
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function registerRig(bytes32 rigId, address owner) public {
        require(rigIdToOwner[rigId] == address(0), "Rig already registered");
        rigIdToOwner[rigId] = owner;
        emit RigRegistered(rigId, owner);
    }

    function submitProof(bytes32 rigId, uint256 hashes, bytes memory signature) public onlyRole(MESH_VALIDATOR_ROLE) {
        // In a real scenario, validateMeshSig would be called here or an equivalent on-chain validation
        // For this MVP, we assume the MESH_VALIDATOR_ROLE ensures validity.
        rigIdToHashes[rigId] = hashes;
        emit ProofSubmitted(rigId, hashes, signature);
    }

    function distributeReward(address miner, uint256 rewardAmount) public onlyRole(MESH_VALIDATOR_ROLE) {
        xmrtContract.rewardFromMesh(miner, rewardAmount);
        emit RewardDistributed(miner, rewardAmount);
    }

    // Function to validate mesh signature off-chain (placeholder for Eliza/Oracle)
    function validateMeshSig(bytes32 rigId, bytes memory signature) public pure returns (bool) {
        // This would involve more complex signature verification logic, possibly involving a specific key.
        // For the MVP, this is a placeholder.
        return true;
    }
}


