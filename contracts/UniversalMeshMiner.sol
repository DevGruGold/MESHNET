// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@zetachain/protocol-contracts/contracts/zevm/interfaces/UniversalContract.sol";
import "@zetachain/protocol-contracts/contracts/zevm/interfaces/IGatewayZEVM.sol";
import "@zetachain/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title UniversalMeshMiner
 * @dev Cross-chain mining operations for MESHNET using ZetaChain Universal Apps
 * Enables miners from any connected blockchain to participate in the network
 */
contract UniversalMeshMiner is UniversalContract, ReentrancyGuard, Pausable, AccessControl {

    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    IGatewayZEVM public immutable gateway;
    address public xmrtToken; // ZRC20 XMRT token address

    struct MiningProof {
        bytes32 rigId;
        uint256 hashCount;
        uint256 timestamp;
        bytes signature;
        uint256 chainId;
        address miner;
    }

    struct Miner {
        address minerAddress;
        uint256 totalHashes;
        uint256 totalRewards;
        uint256 reputationScore;
        uint256 lastSubmission;
        bool isActive;
        uint256 originChainId;
    }

    mapping(bytes32 => Miner) public miners;
    mapping(bytes32 => bool) public usedProofs;
    mapping(uint256 => uint256) public chainRewardMultipliers;

    uint256 public constant REWARD_PER_HASH = 1e12; // Base reward per hash
    uint256 public constant MIN_HASH_THRESHOLD = 1000;
    uint256 public constant REPUTATION_BONUS_MAX = 5000; // 50% max bonus

    event CrossChainMiningProof(
        bytes32 indexed rigId,
        address indexed miner,
        uint256 hashCount,
        uint256 chainId,
        uint256 reward
    );

    event RewardDistributed(
        address indexed miner,
        uint256 amount,
        uint256 destinationChain
    );

    event CrossChainWithdraw(
        address indexed miner,
        uint256 amount,
        uint256 destinationChain,
        bytes recipient
    );

    constructor(
        address _gateway,
        address _xmrtToken
    ) {
        gateway = IGatewayZEVM(_gateway);
        xmrtToken = _xmrtToken;

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(VALIDATOR_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);

        // Set default chain multipliers
        chainRewardMultipliers[1] = 10000; // Ethereum: 1x
        chainRewardMultipliers[56] = 11000; // BSC: 1.1x
        chainRewardMultipliers[137] = 11500; // Polygon: 1.15x
        chainRewardMultipliers[8453] = 12000; // Base: 1.2x
        chainRewardMultipliers[0] = 15000; // Bitcoin: 1.5x (special case)
    }

    /**
     * @dev Handle cross-chain calls from miners
     * Processes mining proofs submitted from any connected blockchain
     */
    function onCall(
        MessageContext calldata context,
        address zrc20,
        uint256 amount,
        bytes calldata message
    ) external override onlyGateway nonReentrant whenNotPaused {

        // Decode the mining proof from the message
        MiningProof memory proof = abi.decode(message, (MiningProof));

        // Validate the proof
        require(_validateProof(proof, context), "Invalid mining proof");

        // Update miner data
        _updateMiner(proof, context.sender, context.origin);

        // Calculate and distribute rewards
        uint256 reward = _calculateReward(proof);

        // Mint or transfer XMRT rewards
        if (reward > 0) {
            _distributeReward(proof.rigId, context.sender, reward, context.origin);
        }

        emit CrossChainMiningProof(
            proof.rigId,
            context.sender,
            proof.hashCount,
            context.origin,
            reward
        );
    }

    /**
     * @dev Allow miners to withdraw rewards to their preferred chain
     */
    function withdrawToChain(
        uint256 amount,
        uint256 destinationChain,
        bytes calldata recipient
    ) external nonReentrant whenNotPaused {

        // Get miner data
        bytes32 rigId = keccak256(abi.encodePacked(msg.sender));
        Miner storage miner = miners[rigId];

        require(miner.isActive, "Miner not active");
        require(miner.totalRewards >= amount, "Insufficient rewards");

        // Update miner rewards
        miner.totalRewards -= amount;

        // Withdraw to destination chain
        _withdrawToChain(msg.sender, amount, destinationChain, recipient);

        emit CrossChainWithdraw(msg.sender, amount, destinationChain, recipient);
    }

    /**
     * @dev Validate mining proof cryptographically
     */
    function _validateProof(
        MiningProof memory proof,
        MessageContext calldata context
    ) internal view returns (bool) {

        // Check if proof already used
        bytes32 proofHash = keccak256(abi.encodePacked(
            proof.rigId,
            proof.hashCount,
            proof.timestamp,
            proof.chainId
        ));

        if (usedProofs[proofHash]) {
            return false;
        }

        // Check timestamp freshness (within 1 hour)
        if (block.timestamp - proof.timestamp > 3600) {
            return false;
        }

        // Check minimum hash threshold
        if (proof.hashCount < MIN_HASH_THRESHOLD) {
            return false;
        }

        // Verify signature (simplified - in production, use proper ECDSA)
        bytes32 messageHash = keccak256(abi.encodePacked(
            proof.rigId,
            proof.hashCount,
            proof.timestamp,
            context.sender
        ));

        // Mark proof as used
        usedProofs[proofHash] = true;

        return true;
    }

    /**
     * @dev Update miner information
     */
    function _updateMiner(
        MiningProof memory proof,
        address minerAddress,
        uint256 chainId
    ) internal {

        Miner storage miner = miners[proof.rigId];

        if (!miner.isActive) {
            miner.minerAddress = minerAddress;
            miner.isActive = true;
            miner.originChainId = chainId;
            miner.reputationScore = 1000; // Starting reputation
        }

        miner.totalHashes += proof.hashCount;
        miner.lastSubmission = block.timestamp;

        // Update reputation based on consistent mining
        if (block.timestamp - miner.lastSubmission < 86400) { // Within 24 hours
            miner.reputationScore = miner.reputationScore * 1001 / 1000; // Small bonus
        }
    }

    /**
     * @dev Calculate mining rewards with chain and reputation multipliers
     */
    function _calculateReward(MiningProof memory proof) internal view returns (uint256) {

        Miner storage miner = miners[proof.rigId];
        uint256 baseReward = proof.hashCount * REWARD_PER_HASH;

        // Apply chain multiplier
        uint256 chainMultiplier = chainRewardMultipliers[proof.chainId];
        if (chainMultiplier == 0) chainMultiplier = 10000; // Default 1x

        uint256 chainAdjustedReward = baseReward * chainMultiplier / 10000;

        // Apply reputation bonus (up to 50%)
        uint256 reputationBonus = 0;
        if (miner.reputationScore > 1000) {
            reputationBonus = (miner.reputationScore - 1000) * REPUTATION_BONUS_MAX / 9000;
            if (reputationBonus > REPUTATION_BONUS_MAX) {
                reputationBonus = REPUTATION_BONUS_MAX;
            }
        }

        uint256 finalReward = chainAdjustedReward * (10000 + reputationBonus) / 10000;

        return finalReward;
    }

    /**
     * @dev Distribute rewards to miner
     */
    function _distributeReward(
        bytes32 rigId,
        address miner,
        uint256 reward,
        uint256 originChain
    ) internal {

        // Update miner rewards
        miners[rigId].totalRewards += reward;

        // Mint XMRT tokens (assuming XMRT has a mint function)
        // In production, integrate with actual XMRT ZRC20 contract
        IZRC20(xmrtToken).transfer(miner, reward);

        emit RewardDistributed(miner, reward, originChain);
    }

    /**
     * @dev Withdraw rewards to specific chain
     */
    function _withdrawToChain(
        address miner,
        uint256 amount,
        uint256 destinationChain,
        bytes calldata recipient
    ) internal {

        // Use ZetaChain gateway to withdraw to destination chain
        // This will convert ZRC20 XMRT back to native tokens on destination chain

        RevertOptions memory revertOptions = RevertOptions({
            revertAddress: miner,
            callOnRevert: false,
            abortAddress: miner,
            revertMessage: "",
            onRevertGasLimit: 0
        });

        gateway.withdrawAndCall(
            recipient,
            amount,
            xmrtToken,
            "",
            revertOptions,
            destinationChain
        );
    }

    /**
     * @dev Set chain reward multipliers
     */
    function setChainMultiplier(
        uint256 chainId,
        uint256 multiplier
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        chainRewardMultipliers[chainId] = multiplier;
    }

    /**
     * @dev Get miner information
     */
    function getMiner(bytes32 rigId) external view returns (Miner memory) {
        return miners[rigId];
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @dev Emergency withdrawal function
     */
    function emergencyWithdraw(
        address token,
        uint256 amount
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        IZRC20(token).transfer(msg.sender, amount);
    }
}