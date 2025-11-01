const { ethers } = require("hardhat");
const { getAddress } = require("@zetachain/addresses");

/**
 * Deploy MESHNET ZetaChain Universal Contracts
 * This script deploys the complete cross-chain mining infrastructure
 */
async function main() {
    console.log("🚀 Deploying MESHNET ZetaChain Integration...");

    const [deployer] = await ethers.getSigners();
    console.log("Deploying with account:", deployer.address);
    console.log("Account balance:", ethers.formatEther(await deployer.getBalance()));

    // Get ZetaChain gateway addresses
    const gatewayZEVM = getAddress("gatewayZEVM", "athens"); // Use mainnet for production
    const gatewayEVM = getAddress("gateway", "ethereum_sepolia"); // Adjust chain as needed

    console.log("\n📋 Gateway Addresses:");
    console.log("ZetaChain Gateway ZEVM:", gatewayZEVM);
    console.log("Ethereum Gateway:", gatewayEVM);

    // 1. Deploy XMRT ZRC20 Token
    console.log("\n🪙 Deploying XMRT ZRC20 Token...");
    const XMRT_ZRC20 = await ethers.getContractFactory("XMRT_ZRC20");
    const protocolFee = 100; // 1% protocol fee
    const xmrtZRC20 = await XMRT_ZRC20.deploy(gatewayZEVM, protocolFee);
    await xmrtZRC20.waitForDeployment();
    console.log("✅ XMRT ZRC20 deployed to:", await xmrtZRC20.getAddress());

    // 2. Deploy Universal MeshMiner
    console.log("\n⛏️ Deploying Universal MeshMiner...");
    const UniversalMeshMiner = await ethers.getContractFactory("UniversalMeshMiner");
    const universalMeshMiner = await UniversalMeshMiner.deploy(
        gatewayZEVM,
        await xmrtZRC20.getAddress()
    );
    await universalMeshMiner.waitForDeployment();
    console.log("✅ Universal MeshMiner deployed to:", await universalMeshMiner.getAddress());

    // 3. Deploy Gateway Contract (for connected chains)
    console.log("\n🌐 Deploying MeshNet Gateway...");
    const MeshNetGateway = await ethers.getContractFactory("MeshNetGateway");
    const chainId = 11155111; // Sepolia testnet
    const meshNetGateway = await MeshNetGateway.deploy(
        gatewayEVM,
        await universalMeshMiner.getAddress(),
        chainId
    );
    await meshNetGateway.waitForDeployment();
    console.log("✅ MeshNet Gateway deployed to:", await meshNetGateway.getAddress());

    // 4. Setup roles and permissions
    console.log("\n🔐 Setting up roles and permissions...");

    // Grant minter role to Universal MeshMiner
    const MINTER_ROLE = await xmrtZRC20.MINTER_ROLE();
    await xmrtZRC20.grantRole(MINTER_ROLE, await universalMeshMiner.getAddress());
    console.log("✅ Granted MINTER_ROLE to Universal MeshMiner");

    // Set chain multipliers for different networks
    await universalMeshMiner.setChainMultiplier(1, 10000); // Ethereum: 1.0x
    await universalMeshMiner.setChainMultiplier(56, 11000); // BSC: 1.1x
    await universalMeshMiner.setChainMultiplier(137, 11500); // Polygon: 1.15x
    await universalMeshMiner.setChainMultiplier(8453, 12000); // Base: 1.2x
    await universalMeshMiner.setChainMultiplier(0, 15000); // Bitcoin: 1.5x
    console.log("✅ Set chain reward multipliers");

    // 5. Verify deployments
    console.log("\n🔍 Verifying deployments...");

    try {
        // Test XMRT ZRC20
        const symbol = await xmrtZRC20.symbol();
        console.log("✅ XMRT Symbol:", symbol);

        // Test Universal MeshMiner
        const xmrtToken = await universalMeshMiner.xmrtToken();
        console.log("✅ Universal MeshMiner XMRT Token:", xmrtToken);

        // Test Gateway
        const universalMinerAddr = await meshNetGateway.universalMeshMiner();
        console.log("✅ Gateway Universal Miner:", universalMinerAddr);

    } catch (error) {
        console.log("❌ Verification failed:", error.message);
    }

    // 6. Generate deployment report
    const deploymentInfo = {
        network: "ZetaChain Athens Testnet",
        deployer: deployer.address,
        timestamp: new Date().toISOString(),
        contracts: {
            "XMRT_ZRC20": {
                address: await xmrtZRC20.getAddress(),
                constructorArgs: [gatewayZEVM, protocolFee]
            },
            "UniversalMeshMiner": {
                address: await universalMeshMiner.getAddress(),
                constructorArgs: [gatewayZEVM, await xmrtZRC20.getAddress()]
            },
            "MeshNetGateway": {
                address: await meshNetGateway.getAddress(),
                constructorArgs: [gatewayEVM, await universalMeshMiner.getAddress(), chainId]
            }
        },
        chainMultipliers: {
            ethereum: "10000 (1.0x)",
            bsc: "11000 (1.1x)",
            polygon: "11500 (1.15x)",
            base: "12000 (1.2x)",
            bitcoin: "15000 (1.5x)"
        }
    };

    console.log("\n📄 Deployment Report:");
    console.log(JSON.stringify(deploymentInfo, null, 2));

    // Save deployment info
    const fs = require("fs");
    fs.writeFileSync(
        "deployments/zetachain-deployment.json",
        JSON.stringify(deploymentInfo, null, 2)
    );

    console.log("\n🎉 MESHNET ZetaChain Integration Deployed Successfully!");
    console.log("\n🔗 Next Steps:");
    console.log("1. Deploy MeshNetGateway on each connected chain");
    console.log("2. Update Eliza Daemon with contract addresses");
    console.log("3. Configure chain-specific token addresses");
    console.log("4. Test cross-chain mining operations");
    console.log("5. Deploy to mainnet networks");

    return {
        xmrtZRC20: await xmrtZRC20.getAddress(),
        universalMeshMiner: await universalMeshMiner.getAddress(),
        meshNetGateway: await meshNetGateway.getAddress()
    };
}

// Error handling
main()
    .then((addresses) => {
        console.log("\n✅ All contracts deployed:", addresses);
        process.exit(0);
    })
    .catch((error) => {
        console.error("❌ Deployment failed:", error);
        process.exit(1);
    });
