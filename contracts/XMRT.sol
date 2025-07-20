// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract XMRT is ERC20, AccessControl {
    bytes32 public constant CEO_AI_ROLE = keccak256("CEO_AI_ROLE");
    bytes32 public constant AUDIT_AI_ROLE = keccak256("AUDIT_AI_ROLE");
    bytes32 public constant MESH_VALIDATOR_ROLE = keccak256("MESH_VALIDATOR_ROLE");

    constructor() ERC20("XMRT Token", "XMRT") {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _mint(msg.sender, 1000000 * 10 ** decimals()); // Mint initial supply to deployer
    }

    modifier onlyElizaOrLangflow() {
        require(hasRole(CEO_AI_ROLE, _msgSender()) || hasRole(AUDIT_AI_ROLE, _msgSender()), "Caller is not Eliza or Langflow");
        _;
    }

    function rewardFromMesh(address to, uint256 amount) public onlyRole(MESH_VALIDATOR_ROLE) {
        _mint(to, amount);
    }

    // Placeholder for rigId to wallet mapping
    mapping(bytes32 => address) public rigIdToWallet;

    function setRigIdToWallet(bytes32 rigId, address wallet) public onlyElizaOrLangflow {
        rigIdToWallet[rigId] = wallet;
    }

    function createProposal(bytes32 proposalId, address target, uint256 value, bytes memory data) public onlyElizaOrLangflow {
        // Placeholder for DAO proposal creation logic
        // In a real scenario, this would interact with a DAO governance contract
    }
}


