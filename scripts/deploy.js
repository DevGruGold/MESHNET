const { ethers } = require("hardhat");

async function main() {
  console.log("Starting MESHNET Phase 2 deployment to Sepolia...");

  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy XMRT contract
  console.log("\n1. Deploying XMRT contract...");
  const XMRT = await ethers.getContractFactory("XMRT");
  const xmrt = await XMRT.deploy();
  await xmrt.deployed();
  console.log("XMRT deployed to:", xmrt.address);

  // Deploy MeshMiner contract
  console.log("\n2. Deploying MeshMiner contract...");
  const MeshMiner = await ethers.getContractFactory("MeshMiner");
  const meshMiner = await MeshMiner.deploy(xmrt.address);
  await meshMiner.deployed();
  console.log("MeshMiner deployed to:", meshMiner.address);

  // Set up roles
  console.log("\n3. Setting up roles...");
  
  // Example addresses - replace with actual addresses
  const elizaAddress = "0x742d35Cc6634C0532925a3b8D0C9e3e0C8b0e5B2"; // Replace with actual Eliza address
  const langflowAddress = "0x8ba1f109551bD432803012645Hac136c5c2BD754"; // Replace with actual Langflow address
  const validatorAddress = "0x9f2d04a9c2f0f6c3e8b1a5d4c7e9f2a8b5c6d3e7"; // Replace with actual Validator address

  const CEO_AI_ROLE = await xmrt.CEO_AI_ROLE();
  const AUDIT_AI_ROLE = await xmrt.AUDIT_AI_ROLE();
  const MESH_VALIDATOR_ROLE = await meshMiner.MESH_VALIDATOR_ROLE();

  // Grant roles in XMRT contract
  await xmrt.grantRole(CEO_AI_ROLE, elizaAddress);
  console.log("Granted CEO_AI_ROLE to Eliza:", elizaAddress);

  await xmrt.grantRole(AUDIT_AI_ROLE, langflowAddress);
  console.log("Granted AUDIT_AI_ROLE to Langflow:", langflowAddress);

  await xmrt.grantRole(await xmrt.MESH_VALIDATOR_ROLE(), validatorAddress);
  console.log("Granted MESH_VALIDATOR_ROLE in XMRT to Validator:", validatorAddress);

  // Grant roles in MeshMiner contract
  await meshMiner.grantRole(MESH_VALIDATOR_ROLE, validatorAddress);
  console.log("Granted MESH_VALIDATOR_ROLE in MeshMiner to Validator:", validatorAddress);

  // Verify deployments
  console.log("\n4. Verifying deployments...");
  console.log("XMRT name:", await xmrt.name());
  console.log("XMRT symbol:", await xmrt.symbol());
  console.log("MeshMiner XMRT address:", await meshMiner.xmrtContract());

  // Save deployment info
  const deploymentInfo = {
    network: "sepolia",
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {
      XMRT: {
        address: xmrt.address,
        name: await xmrt.name(),
        symbol: await xmrt.symbol()
      },
      MeshMiner: {
        address: meshMiner.address,
        xmrtContract: await meshMiner.xmrtContract()
      }
    },
    roles: {
      eliza: elizaAddress,
      langflow: langflowAddress,
      validator: validatorAddress
    }
  };

  console.log("\n5. Deployment Summary:");
  console.log(JSON.stringify(deploymentInfo, null, 2));

  // Save to file
  const fs = require('fs');
  fs.writeFileSync('deployment-info.json', JSON.stringify(deploymentInfo, null, 2));
  console.log("\nDeployment info saved to deployment-info.json");

  console.log("\n✅ MESHNET Phase 2 deployment completed successfully!");
  console.log("\nNext steps:");
  console.log("1. Update frontend with contract addresses");
  console.log("2. Configure Oracle with validator private key");
  console.log("3. Set up Eliza agent with contract addresses");
  console.log("4. Test with 3 miners as specified in requirements");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

