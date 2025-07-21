// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

interface IXMRT {
    function rewardFromMesh(address to, uint256 amount) external;
}

contract MeshMiner is AccessControl, Initializable {
    bytes32 public constant MESH_VALIDATOR_ROLE = keccak256("MESH_VALIDATOR_ROLE");

    mapping(bytes32 => address) public rigIdToOwner;
    mapping(bytes32 => uint256) public rigIdToHashes;

    event RigRegistered(bytes32 indexed rigId, address indexed owner);
    event ProofSubmitted(bytes32 indexed rigId, uint256 hashes, bytes signature);
    event RewardDistributed(address indexed miner, uint256 rewardAmount);

    IXMRT public xmrtContract;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address _xmrtAddress, address defaultAdmin) public initializer {
        xmrtContract = IXMRT(_xmrtAddress);
        __AccessControl_init();
        _setupRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
    }

    function registerRig(bytes32 rigId, address owner) public {
        require(rigIdToOwner[rigId] == address(0), "Rig already registered");
        rigIdToOwner[rigId] = owner;
        emit RigRegistered(rigId, owner);
    }

    function submitProof(bytes32 rigId, uint256 hashes, bytes memory signature) public onlyRole(MESH_VALIDATOR_ROLE) {
        // This function assumes that the MESH_VALIDATOR_ROLE has already verified the proof off-chain.
        // The `validateMeshSig` function is a placeholder for off-chain validation by Eliza/Oracle.
        rigIdToHashes[rigId] = hashes;
        emit ProofSubmitted(rigId, hashes, signature);
    }

    function distributeReward(address miner, uint256 rewardAmount) public onlyRole(MESH_VALIDATOR_ROLE) {
        xmrtContract.rewardFromMesh(miner, rewardAmount);
        emit RewardDistributed(miner, rewardAmount);
    }

    // This function is a placeholder for off-chain signature validation by Eliza/Oracle.
    // It is not intended to be called on-chain for actual validation in this contract.
    function validateMeshSig(bytes32 rigId, bytes memory signature) public pure returns (bool) {
        return true;
    }
}


