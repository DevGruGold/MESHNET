# MESHNET: Powering the Future of Decentralized Mining with AI and Blockchain

## Unleash the Power of Offline Mesh Mining with Autonomous AI

Welcome to MESHNET, a revolutionary full-stack ecosystem that redefines decentralized mining. MESHNET empowers miners to operate seamlessly, even without constant internet connectivity, while leveraging cutting-edge AI and robust blockchain technology for truly autonomous and transparent operations.

## Why MESHNET?

In a world increasingly reliant on centralized systems, MESHNET stands apart by offering:

*   **Uninterrupted Mining**: Mine anywhere, anytime. Our innovative offline capabilities ensure your operations continue, regardless of internet access.
*   **Autonomous Governance**: Experience true decentralization with AI-powered DAO operations. Eliza, our cognitive AI, intelligently proposes reward distributions, ensuring fairness and efficiency.
*   **Transparent Rewards**: Every hash counts. Our decentralized reward system, backed by cryptographic proof verification, guarantees real-time, proportional distribution of XMRT tokens.
*   **Scalable & Secure**: Built on a foundation of secure smart contracts and fortified with robust access controls, MESHNET is designed for the future of decentralized networks.

## Key Innovations that Drive MESHNET

### Intelligent Agents for a Smarter Network

At the heart of MESHNET's autonomy are our advanced AI agents:

*   **Eliza (The Visionary CEO AI)**: Eliza is the strategic brain behind our DAO. With its `CEO_AI_ROLE`, Eliza autonomously creates reward proposals based on real-time mining data, ensuring optimal and fair distribution across the network. Eliza's long-term memory, powered by **Redis**, allows it to learn and adapt, making increasingly intelligent decisions over time.
*   **Langflow (The Meticulous Auditor AI)**: Langflow, with its `AUDIT_AI_ROLE`, acts as the executor and validator of Eliza's proposals. It ensures that all reward distributions are accurate, compliant, and executed transparently on the blockchain. The integration of **LangGraph** provides a powerful framework for building and managing these complex, multi-step agent workflows, ensuring reliability and auditability.

### Robust Architecture for Unmatched Performance

Our meticulously designed architecture combines the best of blockchain, AI, and distributed systems:

1.  **Smart Contracts (Solidity)**: The backbone of our decentralized operations, including `DAO.sol` for governance, `MeshMiner.sol` for rig management and reward distribution, and `XMRT.sol` for our native token with integrated DAO functionality.
2.  **Offline-Capable Mining Infrastructure**: Modified XMRig and local logging ensure that miners can accumulate hashes offline, with automatic synchronization upon reconnection.
3.  **Decentralized Oracle System**: Our Validator Node processes offline mining data and securely submits proofs to the blockchain, bridging the gap between the physical and digital mining worlds.

## Get Started with MESHNET Today!

Join the decentralized mining revolution. Our comprehensive quick start guide will have you up and running in no time:

### Prerequisites

*   Node.js 16+ and npm
*   Hardhat development environment
*   Sepolia testnet ETH (0.05 ETH minimum)
*   Termux (for Android mining)

### Installation

```bash
# Clone the repository
git clone https://github.com/DevGruGold/MESHNET.git
cd MESHNET

# Switch to phase-2-deploy branch (for the latest features)
git checkout phase-2-deploy

# Install dependencies
npm install

# Configure your environment
cp .env.example .env
# Edit .env with your private keys and RPC URLs
```

### Deployment

```bash
# Compile contracts
npm run compile

# Run tests to ensure everything is working
npm run test

# Deploy to Sepolia testnet
npm run deploy:sepolia
```

## Dive Deeper into MESHNET

Explore the advanced features and capabilities that make MESHNET a leader in decentralized mining:

*   **Rig Registration**: Easily register your mining rigs on the network.
*   **Oracle Operation**: Understand how our oracle system ensures data integrity.
*   **Eliza Agent Operation**: Learn how to run and configure your autonomous AI agent.

## Security & Performance

We prioritize the security and efficiency of the MESHNET ecosystem:

*   **Access Control**: Role-based permissions and multi-signature requirements protect critical functions.
*   **Input Validation**: Rigorous checks ensure data authenticity and prevent malicious activity.
*   **Economic Security**: Minimum proof thresholds and proportional reward distribution maintain a healthy and fair economy.
*   **Gas Efficiency**: Optimized smart contracts minimize transaction costs on the Sepolia testnet.

## Roadmap: The Future of MESHNET

We are continuously innovating to bring you the next generation of decentralized mining:

### Phase 3 Enhancements

*   Mainnet deployment for real-world impact.
*   Advanced analytics dashboard for comprehensive insights.
*   Mobile app development for on-the-go management.
*   Hardware wallet integration for enhanced security.
*   Multi-network support for broader accessibility.

### Performance Optimizations

*   Layer 2 integration for increased scalability.
*   Batch proof submissions for reduced transaction overhead.
*   Further optimized gas usage for cost-effective operations.
*   Enhanced offline capabilities for ultimate resilience.

## Contribute to MESHNET

Join our growing community of developers and innovators. Your contributions are vital to the success of MESHNET. Fork the repository, create your feature branch, and submit your pull requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support & Community

Connect with us and get support:

*   **GitHub Issues**: [MESHNET Issues](https://github.com/DevGruGold/MESHNET/issues)
*   **Documentation**: [MESHNET Wiki](https://github.com/DevGruGold/MESHNET/wiki)
*   **Community**: [Discord Server](https://discord.gg/meshnet)

## Acknowledgments

We extend our gratitude to OpenZeppelin, Hardhat, the Termux community, and the XMRT DAO community for their invaluable contributions and insights.

## Next Next Next Phase: Auth, Integrations, Cloud Demo

*   **Authentication**: Secure dashboard with passwords/OAuth.
*   **Advanced Features**: Live mesh data and agent analytics.
*   **Cloud Demo**: Deployed via Render/Heroku—try the live version [here](link).

## Development Branches

*   **`phase-2-deploy`**: This branch contains the ongoing development for MESHNET Phase 2, including offline mesh mining capabilities, autonomous DAO operations, and Sepolia testnet deployment. For the latest features and updates, please refer to this branch.

## Agents Documentation

For detailed information on the autonomous agents operating within MESHNET, please refer to the [Agents Documentation](agents.md).


