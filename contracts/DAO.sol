// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

contract DAO is AccessControl, Initializable {
    bytes32 public constant PROPOSER_ROLE = keccak256("PROPOSER_ROLE");
    bytes32 public constant VOTER_ROLE = keccak256("VOTER_ROLE");

    struct Proposal {
        uint256 id;
        address target;
        uint256 value;
        bytes data;
        string description;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool executed;
        uint256 deadline;
        address proposer;
    }

    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    uint256 public proposalCount;
    uint256 public votingPeriod = 7 days;

    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, address target, uint256 value, string description);
    event VoteCast(uint256 indexed proposalId, address indexed voter, uint8 support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address defaultAdmin) public initializer {
        __AccessControl_init();
        _setupRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _setupRole(PROPOSER_ROLE, defaultAdmin);
        _setupRole(VOTER_ROLE, defaultAdmin);
    }

    function propose(address target, uint256 value, bytes memory data, string memory description) external onlyRole(PROPOSER_ROLE) returns (uint256 proposalId) {
        proposalId = ++proposalCount;
        proposals[proposalId] = Proposal({
            id: proposalId,
            target: target,
            value: value,
            data: data,
            description: description,
            forVotes: 0,
            againstVotes: 0,
            abstainVotes: 0,
            executed: false,
            deadline: block.timestamp + votingPeriod,
            proposer: msg.sender
        });

        emit ProposalCreated(proposalId, msg.sender, target, value, description);
    }

    function vote(uint256 proposalId, uint8 support) external onlyRole(VOTER_ROLE) {
        require(proposalId <= proposalCount && proposalId > 0, "Invalid proposal ID");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        require(block.timestamp <= proposals[proposalId].deadline, "Voting period ended");

        hasVoted[proposalId][msg.sender] = true;

        if (support == 0) {
            proposals[proposalId].againstVotes += 1;
        } else if (support == 1) {
            proposals[proposalId].forVotes += 1;
        } else if (support == 2) {
            proposals[proposalId].abstainVotes += 1;
        }

        emit VoteCast(proposalId, msg.sender, support, 1);
    }

    function execute(uint256 proposalId) external {
        require(proposalId <= proposalCount && proposalId > 0, "Invalid proposal ID");
        require(!proposals[proposalId].executed, "Proposal already executed");
        require(block.timestamp > proposals[proposalId].deadline, "Voting period not ended");
        require(proposals[proposalId].forVotes > proposals[proposalId].againstVotes, "Proposal not passed");

        proposals[proposalId].executed = true;

        (bool success, ) = proposals[proposalId].target.call{value: proposals[proposalId].value}(proposals[proposalId].data);
        require(success, "Proposal execution failed");

        emit ProposalExecuted(proposalId);
    }

    function setVotingPeriod(uint256 _votingPeriod) external onlyRole(DEFAULT_ADMIN_ROLE) {
        votingPeriod = _votingPeriod;
    }
}

