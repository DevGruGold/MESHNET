const { ethers } = require("hardhat");
const { expect } = require("chai");

describe("MESHNET Phase 2 Deployment Tests", function () {
  let xmrt, meshMiner;
  let owner, eliza, langflow, validator, miner1, miner2, miner3;

  beforeEach(async function () {
    [owner, eliza, langflow, validator, miner1, miner2, miner3] = await ethers.getSigners();

    // Deploy XMRT contract
    const XMRT = await ethers.getContractFactory("XMRT");
    xmrt = await XMRT.deploy();
    await xmrt.deployed();

    // Deploy MeshMiner contract
    const MeshMiner = await ethers.getContractFactory("MeshMiner");
    meshMiner = await MeshMiner.deploy(xmrt.address);
    await meshMiner.deployed();

    // Set up roles
    const CEO_AI_ROLE = await xmrt.CEO_AI_ROLE();
    const AUDIT_AI_ROLE = await xmrt.AUDIT_AI_ROLE();
    const MESH_VALIDATOR_ROLE = await meshMiner.MESH_VALIDATOR_ROLE();

    await xmrt.grantRole(CEO_AI_ROLE, eliza.address);
    await xmrt.grantRole(AUDIT_AI_ROLE, langflow.address);
    await xmrt.grantRole(await xmrt.MESH_VALIDATOR_ROLE(), validator.address);
    await meshMiner.grantRole(MESH_VALIDATOR_ROLE, validator.address);
  });

  describe("Contract Deployment", function () {
    it("Should deploy XMRT contract successfully", async function () {
      expect(await xmrt.name()).to.equal("XMRT Token");
      expect(await xmrt.symbol()).to.equal("XMRT");
    });

    it("Should deploy MeshMiner contract successfully", async function () {
      expect(await meshMiner.xmrtContract()).to.equal(xmrt.address);
    });

    it("Should set up roles correctly", async function () {
      const CEO_AI_ROLE = await xmrt.CEO_AI_ROLE();
      const AUDIT_AI_ROLE = await xmrt.AUDIT_AI_ROLE();
      const MESH_VALIDATOR_ROLE = await meshMiner.MESH_VALIDATOR_ROLE();

      expect(await xmrt.hasRole(CEO_AI_ROLE, eliza.address)).to.be.true;
      expect(await xmrt.hasRole(AUDIT_AI_ROLE, langflow.address)).to.be.true;
      expect(await meshMiner.hasRole(MESH_VALIDATOR_ROLE, validator.address)).to.be.true;
    });
  });

  describe("Rig Registration", function () {
    it("Should register a rig successfully", async function () {
      const rigId = ethers.utils.formatBytes32String("rig001");
      
      await meshMiner.registerRig(rigId, miner1.address);
      
      expect(await meshMiner.rigIdToOwner(rigId)).to.equal(miner1.address);
    });

    it("Should prevent duplicate rig registration", async function () {
      const rigId = ethers.utils.formatBytes32String("rig001");
      
      await meshMiner.registerRig(rigId, miner1.address);
      
      await expect(
        meshMiner.registerRig(rigId, miner2.address)
      ).to.be.revertedWith("Rig already registered");
    });
  });

  describe("Proof Submission", function () {
    it("Should submit proof successfully", async function () {
      const rigId = ethers.utils.formatBytes32String("rig001");
      const hashes = 100000;
      const signature = "0x1234567890abcdef";

      await meshMiner.registerRig(rigId, miner1.address);
      
      await expect(
        meshMiner.connect(validator).submitProof(rigId, hashes, signature)
      ).to.emit(meshMiner, "ProofSubmitted")
       .withArgs(rigId, hashes, signature);

      expect(await meshMiner.rigIdToHashes(rigId)).to.equal(hashes);
    });

    it("Should only allow validator to submit proofs", async function () {
      const rigId = ethers.utils.formatBytes32String("rig001");
      const hashes = 100000;
      const signature = "0x1234567890abcdef";

      await expect(
        meshMiner.connect(miner1).submitProof(rigId, hashes, signature)
      ).to.be.reverted;
    });
  });

  describe("Reward Distribution", function () {
    it("Should distribute rewards successfully", async function () {
      const rewardAmount = ethers.utils.parseEther("100");

      await expect(
        meshMiner.connect(validator).distributeReward(miner1.address, rewardAmount)
      ).to.emit(meshMiner, "RewardDistributed")
       .withArgs(miner1.address, rewardAmount);
    });

    it("Should only allow validator to distribute rewards", async function () {
      const rewardAmount = ethers.utils.parseEther("100");

      await expect(
        meshMiner.connect(miner1).distributeReward(miner1.address, rewardAmount)
      ).to.be.reverted;
    });
  });

  describe("Offline Mining Simulation", function () {
    it("Should simulate 3 miners offline then reconnect and submit", async function () {
      // Register 3 rigs
      const rig1 = ethers.utils.formatBytes32String("rig001");
      const rig2 = ethers.utils.formatBytes32String("rig002");
      const rig3 = ethers.utils.formatBytes32String("rig003");

      await meshMiner.registerRig(rig1, miner1.address);
      await meshMiner.registerRig(rig2, miner2.address);
      await meshMiner.registerRig(rig3, miner3.address);

      // Simulate offline mining (accumulate hashes)
      const hashes1 = 150000;
      const hashes2 = 200000;
      const hashes3 = 175000;

      // Reconnect and submit proofs
      await meshMiner.connect(validator).submitProof(rig1, hashes1, "0xsig1");
      await meshMiner.connect(validator).submitProof(rig2, hashes2, "0xsig2");
      await meshMiner.connect(validator).submitProof(rig3, hashes3, "0xsig3");

      // Verify submissions
      expect(await meshMiner.rigIdToHashes(rig1)).to.equal(hashes1);
      expect(await meshMiner.rigIdToHashes(rig2)).to.equal(hashes2);
      expect(await meshMiner.rigIdToHashes(rig3)).to.equal(hashes3);
    });
  });

  describe("Eliza Proposal and Langflow Execution", function () {
    it("Should allow Eliza to create proposal and Langflow to execute", async function () {
      // This is a simplified test - in reality, this would involve more complex DAO logic
      const proposalId = ethers.utils.formatBytes32String("proposal001");
      const target = miner1.address;
      const value = 0;
      const data = "0x";

      // Eliza creates proposal (simplified)
      await expect(
        xmrt.connect(eliza).createProposal(proposalId, target, value, data)
      ).to.not.be.reverted;

      // Langflow executes (simplified)
      const rewardAmount = ethers.utils.parseEther("50");
      await expect(
        meshMiner.connect(validator).distributeReward(miner1.address, rewardAmount)
      ).to.emit(meshMiner, "RewardDistributed");
    });
  });

  describe("Gas Usage Analysis", function () {
    it("Should track gas usage for key operations", async function () {
      const rigId = ethers.utils.formatBytes32String("rig001");
      
      // Register rig
      const registerTx = await meshMiner.registerRig(rigId, miner1.address);
      const registerReceipt = await registerTx.wait();
      console.log(`Register rig gas used: ${registerReceipt.gasUsed}`);

      // Submit proof
      const proofTx = await meshMiner.connect(validator).submitProof(rigId, 100000, "0x1234");
      const proofReceipt = await proofTx.wait();
      console.log(`Submit proof gas used: ${proofReceipt.gasUsed}`);

      // Distribute reward
      const rewardTx = await meshMiner.connect(validator).distributeReward(miner1.address, ethers.utils.parseEther("10"));
      const rewardReceipt = await rewardTx.wait();
      console.log(`Distribute reward gas used: ${rewardReceipt.gasUsed}`);

      // Ensure gas usage is reasonable (under 200k for each operation)
      expect(registerReceipt.gasUsed).to.be.below(200000);
      expect(proofReceipt.gasUsed).to.be.below(200000);
      expect(rewardReceipt.gasUsed).to.be.below(200000);
    });
  });
});

