// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./XMRT.sol";
import "./DAO.sol";
import "./MeshMiner.sol";
import "./Oracle.sol";
import "./Treasury.sol";
import "./Governance.sol";
import "./ReputationSystem.sol";
import "./ProofVerifier.sol";

/**
 * @title MeshNetDeployer
 * @dev Deployment script for all MESHNET contracts
 */
contract MeshNetDeployer {
    XMRT public xmrtToken;
    DAO public dao;
    MeshMiner public meshMiner;
    Oracle public oracle;
    Treasury public treasury;
    Governance public governance;
    ReputationSystem public reputationSystem;
    ProofVerifier public proofVerifier;

    event ContractsDeployed(
        address xmrt,
        address dao,
        address meshMiner,
        address oracle,
        address treasury,
        address governance,
        address reputation,
        address proofVerifier
    );

    function deployAll(
        address[] memory treasurers,
        uint256 requiredConfirmations
    ) external {
        // Deploy XMRT token
        xmrtToken = new XMRT();

        // Deploy DAO
        dao = new DAO();

        // Deploy Oracle
        oracle = new Oracle();

        // Deploy ProofVerifier
        proofVerifier = new ProofVerifier();

        // Deploy ReputationSystem
        reputationSystem = new ReputationSystem();

        // Deploy MeshMiner with XMRT reference
        meshMiner = new MeshMiner(address(xmrtToken));

        // Deploy Treasury
        treasury = new Treasury(treasurers, requiredConfirmations);

        // Deploy Governance with XMRT reference
        governance = new Governance(address(xmrtToken));

        // Initialize contracts with proper roles
        _setupRoles();

        emit ContractsDeployed(
            address(xmrtToken),
            address(dao),
            address(meshMiner),
            address(oracle),
            address(treasury),
            address(governance),
            address(reputationSystem),
            address(proofVerifier)
        );
    }

    function _setupRoles() internal {
        // Grant MeshMiner permission to mint XMRT tokens
        xmrtToken.grantRole(xmrtToken.MESH_VALIDATOR_ROLE(), address(meshMiner));

        // Grant Oracle permission to submit proofs
        meshMiner.grantRole(meshMiner.VALIDATOR_ROLE(), address(oracle));

        // Setup reputation system roles
        reputationSystem.grantRole(reputationSystem.VALIDATOR_ROLE(), address(meshMiner));

        // Setup proof verifier roles
        proofVerifier.grantRole(proofVerifier.VALIDATOR_ROLE(), address(oracle));

        // Grant governance permission to create proposals in XMRT
        xmrtToken.grantRole(xmrtToken.CEO_AI_ROLE(), address(governance));
    }

    function getDeployedAddresses() external view returns (
        address _xmrt,
        address _dao,
        address _meshMiner,
        address _oracle,
        address _treasury,
        address _governance,
        address _reputation,
        address _proofVerifier
    ) {
        return (
            address(xmrtToken),
            address(dao),
            address(meshMiner),
            address(oracle),
            address(treasury),
            address(governance),
            address(reputationSystem),
            address(proofVerifier)
        );
    }
}