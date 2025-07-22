# MESHNET Agents Documentation

This document provides detailed information about the autonomous agents operating within the MESHNET ecosystem.

## 1. Eliza (Cognitive Creator)

**Role:** `CEO_AI_ROLE`

Eliza is the primary cognitive agent responsible for initiating and proposing key operational decisions within the MESHNET DAO. Operating with the `CEO_AI_ROLE`, Eliza's core function is to analyze network data, particularly mining proofs and scoreboard information, to formulate proposals for reward distribution and other strategic actions.

### Responsibilities:
- **Data Analysis:** Fetches and processes `meshnet_scoreboard.json` to identify top miners and their hash contributions.
- **Proof Verification:** Performs hash and signature verification for each rig ID (off-chain oracle optional).
- **Proposal Generation:** Creates proposals to reward top X miners based on a configurable `hash-weighted` reward mode.
- **DAO Interaction:** Utilizes the `XMRT.sol` contract's `createProposal()` function to submit proposals to the DAO, including an AI signature for authenticity.
- **Configuration Management:** Adheres to parameters defined in `meshnet_policy.json`, such as `canPropose`, `rewardMode`, `minRigProof`, `proposalIntervalSec`, and `quorumOverride`.

### Key Files:
- `agents/eliza/agent_loop.py`: Contains the main logic for Eliza's autonomous loop, including scoreboard fetching, reward calculation, and proposal creation.
- `agents/eliza/meshnet_policy.json`: Defines Eliza's operational policies and parameters.

### Operational Flow:
1. Eliza's `agent_loop.py` continuously runs, periodically fetching the `meshnet_scoreboard.json`.
2. It verifies the hash count and signature for each rig, ensuring data integrity.
3. Based on the `rewardMode` (e.g., `hash-weighted`), Eliza calculates the proposed reward distribution for eligible miners.
4. If the `proposalIntervalSec` has passed and `canPropose` is true, Eliza constructs a DAO proposal.
5. The proposal is then submitted to the `XMRT.sol` contract via `createProposal()`, signed by Eliza's AI signature.

## 2. Langflow (Executor)

**Role:** `AUDIT_AI_ROLE`

Langflow serves as the executor agent within the MESHNET DAO, operating with the `AUDIT_AI_ROLE`. Its primary responsibility is to audit and execute proposals initiated by Eliza or other authorized entities. Langflow acts as a critical safeguard, ensuring that all proposed actions align with the DAO's rules and are executed securely.

### Responsibilities:
- **Proposal Auditing:** Reviews proposals submitted to the DAO for compliance, security, and adherence to MESHNET's operational guidelines.
- **Execution:** Executes approved proposals, particularly those related to reward distribution, by interacting with the `XMRT.sol` and `MeshMiner.sol` contracts.
- **Role-Based Access:** Operates under the `AUDIT_AI_ROLE`, which grants it the necessary permissions to interact with sensitive contract functions.
- **Security Enforcement:** Ensures that only valid and audited proposals are executed, preventing malicious or erroneous actions.

### Key Interactions:
- Interacts with `XMRT.sol` to execute `rewardFromMesh()` and other functions as dictated by approved proposals.
- Collaborates with Eliza in the DAO governance process, acting as the final check before on-chain execution.

### Operational Flow:
1. Langflow monitors the DAO for new proposals.
2. Upon identifying a proposal, it performs an audit to verify its legitimacy and adherence to predefined rules.
3. If the audit is successful, Langflow proceeds with the execution of the proposal, which may involve calling functions on the `XMRT.sol` or `MeshMiner.sol` contracts.

## 3. ValidatorNode (Reward Processor)

**Role:** `MESH_VALIDATOR_ROLE`

The ValidatorNode is a crucial component of the Oracle System, responsible for processing offline mining data and submitting proofs to the blockchain. It operates with the `MESH_VALIDATOR_ROLE` and plays a key role in bridging the offline mining activities with the on-chain reward distribution.

### Responsibilities:
- **Scoreboard Ingestion:** Parses `meshnet_scoreboard.json` data, which contains logged local hash counts from offline miners.
- **Proof Submission:** Submits mining proofs to the `MeshMiner.sol` contract via the `submitProof()` function.
- **Signature Verification:** Signs the proof data with its Oracle Node key to ensure authenticity.
- **Reward Distribution:** Authorized to call `distributeReward()` on `MeshMiner.sol` and `rewardFromMesh()` on `XMRT.sol` to facilitate reward payouts.

### Key Files:
- `oracle/scoreboard/submitter.py`: Contains the logic for parsing scoreboard data, signing proofs, and submitting them to the `MeshMiner.sol` contract.

### Operational Flow:
1. The `submitter.py` script runs, loading data from `meshnet_scoreboard.json`.
2. For each rig's data, it signs the proof with the Oracle Node's private key.
3. The signed proof is then submitted to the `MeshMiner.sol` contract's `submitProof()` function.
4. The ValidatorNode also facilitates the `distributeReward()` function calls as part of the reward distribution process, typically triggered by Langflow's execution of Eliza's proposals.


