const { ethers, upgrades } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);

    // Deploy XMRT (Upgradeable)
    const XMRT = await ethers.getContractFactory("XMRT");
    const xmrt = await upgrades.deployProxy(XMRT, [deployer.address, ethers.utils.parseEther("1000000")], { initializer: "initialize" });
    await xmrt.deployed();
    console.log("XMRT deployed to:", xmrt.address);

    // Deploy DAO (Upgradeable)
    const DAO = await ethers.getContractFactory("DAO");
    const dao = await upgrades.deployProxy(DAO, [deployer.address], { initializer: "initialize" });
    await dao.deployed();
    console.log("DAO deployed to:", dao.address);

    // Deploy MeshMiner (Upgradeable)
    const MeshMiner = await ethers.getContractFactory("MeshMiner");
    const meshMiner = await upgrades.deployProxy(MeshMiner, [xmrt.address, deployer.address], { initializer: "initialize" });
    await meshMiner.deployed();
    console.log("MeshMiner deployed to:", meshMiner.address);

    // Grant MESH_VALIDATOR_ROLE to MeshMiner contract in XMRT
    const MESH_VALIDATOR_ROLE = await xmrt.MESH_VALIDATOR_ROLE();
    await xmrt.grantRole(MESH_VALIDATOR_ROLE, meshMiner.address);
    console.log("Granted MESH_VALIDATOR_ROLE to MeshMiner in XMRT");

    // Set DAO contract address in XMRT
    await xmrt.setDAOContract(dao.address);
    console.log("Set DAO contract address in XMRT");

    // Grant PROPOSER_ROLE to deployer in DAO
    const PROPOSER_ROLE = await dao.PROPOSER_ROLE();
    await dao.grantRole(PROPOSER_ROLE, deployer.address);
    console.log("Granted PROPOSER_ROLE to deployer in DAO");

    // Grant VOTER_ROLE to deployer in DAO
    const VOTER_ROLE = await dao.VOTER_ROLE();
    await dao.grantRole(VOTER_ROLE, deployer.address);
    console.log("Granted VOTER_ROLE to deployer in DAO");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });


