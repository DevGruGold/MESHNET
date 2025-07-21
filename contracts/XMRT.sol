// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

contract XMRT is ERC20, AccessControl, Initializable {
    bytes32 public constant CEO_AI_ROLE = keccak256("CEO_AI_ROLE");
    bytes32 public constant AUDIT_AI_ROLE = keccak256("AUDIT_AI_ROLE");
    bytes32 public constant MESH_VALIDATOR_ROLE = keccak256("MESH_VALIDATOR_ROLE");

    // Placeholder for rigId to wallet mapping
    mapping(bytes32 => address) public rigIdToWallet;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address defaultAdmin, uint256 initialSupply) public initializer {
        __ERC20_init("XMRT Token", "XMRT");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _mint(defaultAdmin, initialSupply * (10 ** decimals()));
    }

    modifier onlyElizaOrLangflow() {
        require(hasRole(CEO_AI_ROLE, _msgSender()) || hasRole(AUDIT_AI_ROLE, _msgSender()), "Caller is not Eliza or Langflow");
        _;
    }

    function rewardFromMesh(address to, uint256 amount) public onlyRole(MESH_VALIDATOR_ROLE) {
        _mint(to, amount);
    }

    function setRigIdToWallet(bytes32 rigId, address wallet) public onlyElizaOrLangflow {
        rigIdToWallet[rigId] = wallet;
    }

    // Placeholder for DAO governance contract interaction
    interface IDAO {
        function propose(address target, uint256 value, bytes memory data, string memory description) external returns (uint256 proposalId);
        function vote(uint256 proposalId, uint8 support) external;
        function execute(uint256 proposalId) external;
    }

    IDAO public daoContract;

    function setDAOContract(address _daoAddress) public onlyRole(DEFAULT_ADMIN_ROLE) {
        daoContract = IDAO(_daoAddress);
    }

    function createProposal(bytes32 proposalId, address target, uint256 value, bytes memory data, string memory description) public onlyElizaOrLangflow {
        // In a real scenario, this would interact with a DAO governance contract
        // For now, we'll just emit an event to log the proposal creation.
        require(address(daoContract) != address(0), "DAO contract not set");
        daoContract.propose(target, value, data, description);
        emit ProposalCreated(proposalId, target, value, data);
    }

    event ProposalCreated(bytes32 indexed proposalId, address indexed target, uint256 value, bytes data);
}


