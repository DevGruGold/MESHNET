# MESHNET Phase 2 - Offline Mesh Mining with Autonomous DAO Operations

## Overview

MESHNET Phase 2 introduces offline-capable mesh mining with autonomous DAO operations powered by Eliza AI. This implementation enables miners to operate in offline environments while maintaining decentralized reward distribution through smart contracts deployed on Sepolia testnet.

## Architecture

### Core Components

1. **Smart Contracts**
   - `DAO.sol`: Manages decentralized autonomous organization proposals and voting.
   - `Governance.sol`: Handles governance-related functions and roles.
   - `MeshMiner.sol`: Manages rig registration, proof submission, and reward distribution.
   - `MeshNetDeployer.sol`: Utility contract for deploying other MeshNet contracts.
   - `Oracle.sol`: Provides external data feeds to smart contracts.
   - `ProofVerifier.sol`: Verifies cryptographic proofs submitted by miners.
   - `ReputationSystem.sol`: Manages and tracks reputation scores within the network.
   - `Treasury.sol`: Securely holds and manages project funds.
   - `XMRT.sol`: Extended ERC20 token with DAO functionality and mesh reward integration.

2. **Autonomous Agents**
   - **Eliza**: Cognitive creator with CEO_AI_ROLE for autonomous proposal creation
   - **Langflow**: Executor with AUDIT_AI_ROLE for proposal validation and execution

3. **Oracle System**
   - **Validator Node**: Processes offline mining data and submits proofs to blockchain
   - **Scoreboard Ingestion**: Parses and validates mining session data

4. **Mining Infrastructure**
   - **Termux Integration**: Modified XMRig for offline-capable mining
   - **Offline Logging**: Local storage of mining sessions for later synchronization

## Features

### Offline Mining Capability
- Miners can operate without internet connectivity
- Local hash count logging to `/sdcard/MESHNET/scoreboard.json`
- Automatic synchronization upon reconnection
- Rig ID-based identity management

### Autonomous DAO Operations
- Eliza AI creates reward proposals based on hash-weighted distribution
- Configurable proposal intervals and minimum proof thresholds
- Langflow validation and execution of approved proposals
- Transparent on-chain governance

### Decentralized Reward System
- Hash-based proportional reward calculation
- Cryptographic proof verification
- Real-time reward tracking and distribution
- Claimable reward interface

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- Hardhat development environment
- Sepolia testnet ETH (0.05 ETH minimum)
- Termux (for Android mining)

### Installation

```bash
# Clone the repository
git clone https://github.com/DevGruGold/MESHNET.git
cd MESHNET

# Switch to phase-2-deploy branch
git checkout phase-2-deploy

# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env
# Edit .env with your configuration
```

### Deployment

```bash
# Compile contracts
npm run compile

# Run tests
npm run test

# Deploy to Sepolia testnet
npm run deploy:sepolia
```

### Configuration

1. **Update .env file** with your private keys and RPC URLs
2. **Configure contract addresses** in deployment-info.json after deployment
3. **Set up Oracle** with validator private key
4. **Initialize Eliza agent** with contract addresses

## Usage

### Rig Registration

```javascript
// Register a new mining rig
await meshMiner.registerRig(rigId, walletAddress);
```

### Mining Setup (Termux)

```bash
# Make script executable
chmod +x scripts/termux/miner_meshnet.sh

# Start mining
./scripts/termux/miner_meshnet.sh
```

### Oracle Operation

```bash
# Run oracle submitter
cd oracle/scoreboard
python3 submitter.py
```

### Eliza Agent

```bash
# Start autonomous agent
cd agents/eliza
python3 agent_loop.py
```

## Smart Contract Interface

### MeshMiner.sol

```solidity
// Register a mining rig
function registerRig(bytes32 rigId, address owner) public

// Submit mining proof (validator only)
function submitProof(bytes32 rigId, uint256 hashes, bytes memory signature) public

// Distribute rewards (validator only)
function distributeReward(address miner, uint256 rewardAmount) public
```

### XMRT.sol

```solidity
// Mint rewards from mesh mining (validator only)
function rewardFromMesh(address to, uint256 amount) public

// Create DAO proposal (Eliza/Langflow only)
function createProposal(bytes32 proposalId, address target, uint256 value, bytes memory data) public
```

## Testing

### Unit Tests

```bash
# Run all tests
npm run test

# Run specific test file
npx hardhat test test/deployment_test.js
```

### Integration Testing

The test suite includes:
- Contract deployment verification
- Rig registration and validation
- Proof submission workflows
- Reward distribution mechanisms
- Offline mining simulation
- Gas usage analysis

### Test Scenarios

1. **3 Miners Offline → Reconnect + Submit**
   - Miners accumulate hashes offline
   - Reconnect and submit proofs via Oracle
   - Eliza creates reward proposal
   - Langflow executes distribution

2. **Autonomous Proposal Creation**
   - Eliza monitors scoreboard data
   - Creates hash-weighted reward proposals
   - Respects minimum proof thresholds
   - Maintains proposal intervals

## Security Considerations

### Access Control
- Role-based permissions for all critical functions
- Multi-signature requirements for high-value operations
- Signature verification for mining proofs

### Input Validation
- Rig ID uniqueness enforcement
- Hash count validation
- Signature authenticity checks

### Economic Security
- Minimum proof thresholds prevent spam
- Proportional reward distribution
- Gas-efficient operations

## Gas Usage

Typical gas costs on Sepolia:
- Rig registration: ~150,000 gas
- Proof submission: ~120,000 gas
- Reward distribution: ~180,000 gas

## Frontend Integration

### Dashboard Components
- Real-time mining statistics
- Rig status monitoring
- Reward tracking interface
- Network topology visualization

### API Endpoints
```
GET /api/mesh/rigs - List registered rigs
GET /api/mesh/rewards/{address} - Get claimable rewards
POST /api/mesh/register - Register new rig
POST /api/mesh/claim-rewards - Claim pending rewards
```

## Troubleshooting

### Common Issues

1. **Rig Registration Fails**
   - Ensure rig ID is unique
   - Check wallet connection
   - Verify sufficient gas

2. **Proof Submission Rejected**
   - Validate Oracle permissions
   - Check signature format
   - Ensure minimum hash threshold

3. **Rewards Not Distributed**
   - Verify Eliza agent is running
   - Check proposal interval settings
   - Ensure Langflow validation

### Debug Commands

```bash
# Check contract deployment
npx hardhat verify --network sepolia <contract_address>

# Monitor events
npx hardhat console --network sepolia

# Test Oracle connection
python3 oracle/scoreboard/submitter.py --test
```

## Roadmap

### Phase 3 Enhancements
- Mainnet deployment
- Advanced analytics dashboard
- Mobile app development
- Hardware wallet integration
- Multi-network support

### Performance Optimizations
- Layer 2 integration
- Batch proof submissions
- Optimized gas usage
- Enhanced offline capabilities

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support and questions:
- GitHub Issues: [MESHNET Issues](https://github.com/DevGruGold/MESHNET/issues)
- Documentation: [MESHNET Wiki](https://github.com/DevGruGold/MESHNET/wiki)
- Community: [Discord Server](https://discord.gg/meshnet)

## Acknowledgments

- OpenZeppelin for secure smart contract libraries
- Hardhat for development framework
- Termux community for mobile mining support
- XMRT DAO community for governance insights



## Instructions for Future Agents

This project is designed to facilitate offline mesh mining with autonomous DAO operations. Here are some areas for future improvement and considerations for the next agent:

1.  **Comprehensive Testing**: While unit and integration tests are present, consider expanding test coverage, especially for edge cases and security vulnerabilities in smart contracts. Fuzz testing and formal verification could be valuable additions.
2.  **Gas Optimization**: Review smart contract functions for further gas optimization. Even small reductions can lead to significant savings over time, especially on mainnet deployment.
3.  **Frontend Enhancements**: The current frontend integration is outlined. Develop a fully functional and user-friendly dashboard that visualizes all aspects of the MESHNET ecosystem, including real-time mining statistics, DAO proposals, and reward distribution.
4.  **Oracle Robustness**: Enhance the Oracle system's robustness and fault tolerance. Consider implementing decentralized oracle solutions to reduce single points of failure.
5.  **Agent Intelligence**: Improve the intelligence and autonomy of Eliza and Langflow agents. Explore advanced AI/ML techniques for more sophisticated proposal creation and execution, and consider integrating with more diverse data sources.
6.  **Security Audits**: Before mainnet deployment, a thorough security audit of all smart contracts and the overall system architecture is highly recommended.
7.  **Documentation**: Continuously update and expand documentation for all components, including detailed API specifications, smart contract function explanations, and deployment guides.
8.  **Scalability**: As the network grows, evaluate and implement solutions for scalability, such as Layer 2 integrations or sharding, to handle increased transaction volume.
9.  **User Experience**: Focus on improving the overall user experience for miners, DAO participants, and developers. Simplify setup processes and provide clear feedback mechanisms.

By focusing on these areas, the MESHNET project can be significantly improved and prepared for wider adoption and mainnet deployment.

## Next Next Next Phase: Auth, Integrations, Cloud Demo
- **Authentication:** Secure dashboard with passwords/OAuth.
- **Advanced Features:** Live mesh data and agent analytics.
- **Cloud Demo:** Deployed via Render/Heroku—try the live version [here](link).



## Development Branches

- **`phase-2-deploy`**: This branch contains the ongoing development for MESHNET Phase 2, including offline mesh mining capabilities, autonomous DAO operations, and Sepolia testnet deployment. For the latest features and updates, please refer to this branch.




## Agents Documentation

For detailed information on the autonomous agents operating within MESHNET, please refer to the [Agents Documentation](agents.md).


