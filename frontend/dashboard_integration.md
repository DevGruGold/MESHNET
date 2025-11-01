# Frontend Integration Plan for MESHNET Phase 2

## Overview
This document outlines the frontend integration requirements for xmrtdao.vercel.app to support MESHNET Phase 2 functionality.

## 1. Mesh Uptime + Mining Score Dashboard

### Components to Add:
- **MeshMinerDashboard.jsx**: Main dashboard component
- **RigStatusCard.jsx**: Individual rig status display
- **MiningScoreChart.jsx**: Visual representation of mining scores
- **UptimeTracker.jsx**: Real-time uptime monitoring

### Features:
- Real-time display of connected rigs
- Hash rate visualization per rig
- Uptime percentage tracking
- Mining efficiency metrics
- Network topology visualization

### API Endpoints Needed:
```javascript
// Get all registered rigs
GET /api/mesh/rigs

// Get rig performance data
GET /api/mesh/rigs/{rigId}/performance

// Get network uptime statistics
GET /api/mesh/network/uptime
```

## 2. Wallet Registration Form

### Component: **WalletRegistrationForm.jsx**

### Features:
- Rig ID input field with validation
- Wallet address connection via Web3
- Registration confirmation
- QR code generation for mobile setup

### Form Fields:
```javascript
{
  rigId: string,        // User-provided rig identifier
  walletAddress: string, // Connected wallet address
  deviceInfo: {
    platform: string,   // Android/iOS/Linux
    version: string,    // OS version
    capabilities: []    // Supported features
  }
}
```

### Integration with Smart Contract:
- Call `registerRig(rigId, walletAddress)` on MeshMiner.sol
- Validate rig ID uniqueness
- Store mapping in XMRT.sol via `setRigIdToWallet()`

## 3. Claimable Reward Tracker

### Component: **RewardTracker.jsx**

### Features:
- Display pending rewards per wallet
- Claim button for available rewards
- Transaction history
- Reward calculation breakdown

### Data Sources:
- Listen to `RewardDistributed` events from MeshMiner.sol
- Query reward balance from XMRT contract
- Display hash contribution vs. reward ratio

### UI Elements:
```javascript
{
  pendingRewards: number,
  claimableAmount: number,
  lastClaimDate: Date,
  totalEarned: number,
  hashContribution: number,
  rewardHistory: []
}
```

## 4. Technical Implementation

### State Management:
- Use Redux Toolkit for global state
- Implement real-time updates via WebSocket
- Cache rig data locally for offline viewing

### Web3 Integration:
```javascript
// Contract interaction hooks
useContract('MeshMiner', meshMinerAddress, meshMinerABI)
useContract('XMRT', xmrtAddress, xmrtABI)

// Event listeners
useContractEvent('MeshMiner', 'ProofSubmitted', handleProofSubmitted)
useContractEvent('MeshMiner', 'RewardDistributed', handleRewardDistributed)
```

### Responsive Design:
- Mobile-first approach for Termux users
- Touch-friendly interface elements
- Offline-capable PWA features
- Dark mode support for terminal users

## 5. Integration Points

### Backend API Requirements:
```javascript
// Mesh network status
GET /api/mesh/status
POST /api/mesh/register
GET /api/mesh/rewards/{address}
POST /api/mesh/claim-rewards

// Oracle data
GET /api/oracle/scoreboard
POST /api/oracle/submit-proof
```

### Database Schema Updates:
```sql
-- Rig registration table
CREATE TABLE mesh_rigs (
  rig_id VARCHAR(66) PRIMARY KEY,
  wallet_address VARCHAR(42) NOT NULL,
  registered_at TIMESTAMP DEFAULT NOW(),
  last_seen TIMESTAMP,
  status ENUM('online', 'offline', 'mining') DEFAULT 'offline'
);

-- Mining sessions table
CREATE TABLE mining_sessions (
  id SERIAL PRIMARY KEY,
  rig_id VARCHAR(66) REFERENCES mesh_rigs(rig_id),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  hash_count BIGINT,
  reward_amount DECIMAL(18,8)
);
```

## 6. Security Considerations

### Input Validation:
- Sanitize rig ID inputs
- Validate wallet addresses
- Rate limit registration attempts

### Access Control:
- Verify wallet ownership before registration
- Implement signature-based authentication
- Protect against replay attacks

## 7. Testing Strategy

### Unit Tests:
- Component rendering tests
- Contract interaction tests
- Form validation tests

### Integration Tests:
- End-to-end registration flow
- Reward claiming process
- Real-time data updates

### Performance Tests:
- Load testing with multiple rigs
- WebSocket connection stability
- Mobile device compatibility

## 8. Deployment Checklist

- [ ] Update environment variables for contract addresses
- [ ] Configure Web3 provider for Sepolia testnet
- [ ] Set up monitoring for frontend errors
- [ ] Implement analytics for user interactions
- [ ] Create user documentation and tutorials

## 9. Future Enhancements

### Phase 3 Considerations:
- Multi-network support (Ethereum mainnet)
- Advanced analytics and reporting
- Gamification elements (leaderboards, achievements)
- Mobile app development
- Integration with hardware wallets

