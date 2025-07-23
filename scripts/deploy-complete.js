const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
    console.log("🚀 DEPLOYING COMPLETE MESHNET ECOSYSTEM");
    console.log("=" * 50);

    const [deployer] = await ethers.getSigners();
    console.log("Deploying with account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy contracts in dependency order
    console.log("\n📦 Deploying core contracts...");

    // 1. Deploy XMRT Token
    const XMRT = await ethers.getContractFactory("XMRT");
    const xmrt = await XMRT.deploy();
    await xmrt.deployed();
    console.log("✅ XMRT deployed to:", xmrt.address);

    // 2. Deploy DAO
    const DAO = await ethers.getContractFactory("DAO");
    const dao = await DAO.deploy();
    await dao.deployed();
    console.log("✅ DAO deployed to:", dao.address);

    // 3. Deploy Oracle
    const Oracle = await ethers.getContractFactory("Oracle");
    const oracle = await Oracle.deploy();
    await oracle.deployed();
    console.log("✅ Oracle deployed to:", oracle.address);

    // 4. Deploy ProofVerifier
    const ProofVerifier = await ethers.getContractFactory("ProofVerifier");
    const proofVerifier = await ProofVerifier.deploy();
    await proofVerifier.deployed();
    console.log("✅ ProofVerifier deployed to:", proofVerifier.address);

    // 5. Deploy ReputationSystem
    const ReputationSystem = await ethers.getContractFactory("ReputationSystem");
    const reputationSystem = await ReputationSystem.deploy();
    await reputationSystem.deployed();
    console.log("✅ ReputationSystem deployed to:", reputationSystem.address);

    // 6. Deploy MeshMiner
    const MeshMiner = await ethers.getContractFactory("MeshMiner");
    const meshMiner = await MeshMiner.deploy(xmrt.address);
    await meshMiner.deployed();
    console.log("✅ MeshMiner deployed to:", meshMiner.address);

    // 7. Deploy Treasury
    const treasurers = [deployer.address]; // Add more treasurers as needed
    const requiredConfirmations = 1;
    const Treasury = await ethers.getContractFactory("Treasury");
    const treasury = await Treasury.deploy(treasurers, requiredConfirmations);
    await treasury.deployed();
    console.log("✅ Treasury deployed to:", treasury.address);

    // 8. Deploy Governance
    const Governance = await ethers.getContractFactory("Governance");
    const governance = await Governance.deploy(xmrt.address);
    await governance.deployed();
    console.log("✅ Governance deployed to:", governance.address);

    console.log("\n🔗 Setting up contract permissions...");

    // Initialize XMRT
    await xmrt.initialize();
    console.log("✅ XMRT initialized");

    // Initialize DAO
    await dao.initialize();
    console.log("✅ DAO initialized");

    // Grant roles
    const MESH_VALIDATOR_ROLE = await xmrt.MESH_VALIDATOR_ROLE();
    const VALIDATOR_ROLE = await meshMiner.VALIDATOR_ROLE();
    const CEO_AI_ROLE = await xmrt.CEO_AI_ROLE();

    await xmrt.grantRole(MESH_VALIDATOR_ROLE, meshMiner.address);
    await meshMiner.grantRole(VALIDATOR_ROLE, oracle.address);
    await reputationSystem.grantRole(await reputationSystem.VALIDATOR_ROLE(), meshMiner.address);
    await proofVerifier.grantRole(await proofVerifier.VALIDATOR_ROLE(), oracle.address);
    await xmrt.grantRole(CEO_AI_ROLE, governance.address);

    console.log("✅ All roles granted successfully");

    // Save deployment info
    const deploymentInfo = {
        network: hre.network.name,
        deployer: deployer.address,
        timestamp: new Date().toISOString(),
        contracts: {
            XMRT: xmrt.address,
            DAO: dao.address,
            Oracle: oracle.address,
            ProofVerifier: proofVerifier.address,
            ReputationSystem: reputationSystem.address,
            MeshMiner: meshMiner.address,
            Treasury: treasury.address,
            Governance: governance.address
        },
        gasUsed: {
            // Gas usage will be calculated during deployment
        }
    };

    fs.writeFileSync(
        "deployment-info.json",
        JSON.stringify(deploymentInfo, null, 2)
    );

    console.log("\n🎉 MESHNET ECOSYSTEM DEPLOYED SUCCESSFULLY!");
    console.log("📄 Deployment info saved to deployment-info.json");

    console.log("\n📋 CONTRACT ADDRESSES:");
    console.log("XMRT Token:", xmrt.address);
    console.log("DAO:", dao.address);
    console.log("Oracle:", oracle.address);
    console.log("ProofVerifier:", proofVerifier.address);
    console.log("ReputationSystem:", reputationSystem.address);
    console.log("MeshMiner:", meshMiner.address);
    console.log("Treasury:", treasury.address);
    console.log("Governance:", governance.address);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });