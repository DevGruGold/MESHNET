// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@zetachain/protocol-contracts/contracts/evm/interfaces/IGatewayEVM.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title MeshNetGateway  
 * @dev Gateway contract for MESHNET cross-chain operations
 * Deployed on connected chains to enable mining proof submissions
 */
contract MeshNetGateway is ReentrancyGuard, AccessControl, Pausable {

    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    IGatewayEVM public immutable gateway;
    address public universalMeshMiner; // Address on ZetaChain
    uint256 public immutable chainId;

    struct MiningSubmission {
        bytes32 rigId;
        uint256 hashCount;
        uint256 timestamp;
        bytes signature;
        address miner;
    }

    mapping(bytes32 => bool) public submittedProofs;
    mapping(address => uint256) public minerSubmissions;

    event MiningProofSubmitted(
        bytes32 indexed rigId,
        address indexed miner,
        uint256 hashCount,
        bytes32 proofHash
    );

    event CrossChainCallInitiated(
        address indexed miner,
        bytes32 indexed rigId,
        uint256 amount
    );

    constructor(
        address _gateway,
        address _universalMeshMiner,
        uint256 _chainId
    ) {
        gateway = IGatewayEVM(_gateway);
        universalMeshMiner = _universalMeshMiner;
        chainId = _chainId;

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
    }

    /**
     * @dev Submit mining proof to ZetaChain Universal Contract
     */
    function submitMiningProof(
        bytes32 rigId,
        uint256 hashCount,
        bytes calldata signature
    ) external payable nonReentrant whenNotPaused {

        require(hashCount > 0, "Hash count must be positive");
        require(signature.length > 0, "Signature required");

        // Create proof hash to prevent duplicates
        bytes32 proofHash = keccak256(abi.encodePacked(
            rigId,
            hashCount,
            block.timestamp,
            msg.sender,
            chainId
        ));

        require(!submittedProofs[proofHash], "Proof already submitted");
        submittedProofs[proofHash] = true;

        // Create mining submission data
        MiningSubmission memory submission = MiningSubmission({
            rigId: rigId,
            hashCount: hashCount,
            timestamp: block.timestamp,
            signature: signature,
            miner: msg.sender
        });

        // Encode submission for cross-chain call
        bytes memory message = abi.encode(submission);

        // Call Universal MeshMiner on ZetaChain
        RevertOptions memory revertOptions = RevertOptions({
            revertAddress: msg.sender,
            callOnRevert: true,
            abortAddress: msg.sender,
            revertMessage: "Mining proof failed",
            onRevertGasLimit: 100000
        });

        gateway.call{value: msg.value}(
            universalMeshMiner,
            message,
            revertOptions
        );

        // Update tracking
        minerSubmissions[msg.sender]++;

        emit MiningProofSubmitted(rigId, msg.sender, hashCount, proofHash);
        emit CrossChainCallInitiated(msg.sender, rigId, msg.value);
    }

    /**
     * @dev Batch submit multiple mining proofs
     */
    function batchSubmitProofs(
        bytes32[] calldata rigIds,
        uint256[] calldata hashCounts,
        bytes[] calldata signatures
    ) external payable nonReentrant whenNotPaused {

        require(rigIds.length == hashCounts.length, "Array length mismatch");
        require(rigIds.length == signatures.length, "Array length mismatch");
        require(rigIds.length <= 10, "Too many proofs");

        uint256 totalValue = msg.value / rigIds.length;

        for (uint i = 0; i < rigIds.length; i++) {
            // Similar logic to single submission but in loop
            bytes32 proofHash = keccak256(abi.encodePacked(
                rigIds[i],
                hashCounts[i],
                block.timestamp,
                msg.sender,
                chainId
            ));

            require(!submittedProofs[proofHash], "Duplicate proof in batch");
            submittedProofs[proofHash] = true;

            MiningSubmission memory submission = MiningSubmission({
                rigId: rigIds[i],
                hashCount: hashCounts[i],
                timestamp: block.timestamp,
                signature: signatures[i],
                miner: msg.sender
            });

            bytes memory message = abi.encode(submission);

            RevertOptions memory revertOptions = RevertOptions({
                revertAddress: msg.sender,
                callOnRevert: true,
                abortAddress: msg.sender,
                revertMessage: "Batch mining proof failed",
                onRevertGasLimit: 100000
            });

            gateway.call{value: totalValue}(
                universalMeshMiner,
                message,
                revertOptions
            );

            emit MiningProofSubmitted(rigIds[i], msg.sender, hashCounts[i], proofHash);
        }

        minerSubmissions[msg.sender] += rigIds.length;
    }

    /**
     * @dev Get miner submission count
     */
    function getMinerSubmissionCount(address miner) external view returns (uint256) {
        return minerSubmissions[miner];
    }

    /**
     * @dev Check if proof was submitted
     */
    function isProofSubmitted(bytes32 proofHash) external view returns (bool) {
        return submittedProofs[proofHash];
    }

    /**
     * @dev Update Universal MeshMiner address
     */
    function setUniversalMeshMiner(
        address _universalMeshMiner
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        universalMeshMiner = _universalMeshMiner;
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
     * @dev Emergency withdrawal
     */
    function emergencyWithdraw() external onlyRole(DEFAULT_ADMIN_ROLE) {
        payable(msg.sender).transfer(address(this).balance);
    }

    /**
     * @dev Receive function for gas payments
     */
    receive() external payable {}
}