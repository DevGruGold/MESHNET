# 🚀 Enhanced Eliza Daemon Deployment Guide

## Overview

The Enhanced Eliza Daemon integrates sophisticated AI-powered autonomous operations with MESHNET smart contracts, providing complete automation for DAO operations, reward distribution, and community management.

## Architecture

```
Enhanced Eliza Daemon
├── Core AI Engine (GPT-4 + LangChain)
├── MESHNET Smart Contract Integration
├── Multi-Platform Monitoring
├── Persistent Memory (Supabase)
├── Autonomous Decision Making
└── Real-time Community Engagement
```

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 16+ (for contract interaction)
- Docker (recommended for production)
- Minimum 2GB RAM
- Persistent storage for logs and memory

### API Keys and Services
1. **OpenAI API Key** - For GPT-4 intelligence
2. **Supabase Project** - For persistent memory
3. **Twitter Bearer Token** - For social monitoring
4. **Discord Webhook** - For community notifications
5. **Ethereum Node Access** - Sepolia testnet (Infura/Alchemy)

## Installation

### Step 1: Environment Setup

```bash
# Clone MESHNET repository
git clone https://github.com/DevGruGold/MESHNET.git
cd MESHNET
git checkout phase-2-deploy

# Navigate to enhanced daemon
cd agents/eliza-daemon

# Create virtual environment
python3 -m venv eliza_env
source eliza_env/bin/activate  # On Windows: eliza_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

```bash
# Copy configuration template
cp config.meshnet.json.template config.meshnet.json

# Edit configuration with your values
nano config.meshnet.json
```

Required configuration:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL` & `SUPABASE_KEY`: Supabase project credentials
- `MESHNET_CONTRACTS`: Contract addresses from deployment
- `VALIDATOR_PRIVATE_KEY`: Private key for blockchain operations
- `DISCORD_WEBHOOK`: Discord webhook URL for notifications

### Step 3: Smart Contract Integration

```bash
# Ensure contracts are deployed
cd ../../
npm run deploy:sepolia

# Update contract addresses in config
# Copy addresses from deployment-info.json to config.meshnet.json
```

### Step 4: Memory System Setup

1. **Create Supabase Project**
   - Go to https://supabase.com
   - Create new project
   - Copy URL and anon key to config

2. **Setup Database Tables**
   ```sql
   -- Run in Supabase SQL editor
   CREATE TABLE eliza_memory (
       id SERIAL PRIMARY KEY,
       key VARCHAR(255) NOT NULL,
       data JSONB NOT NULL,
       timestamp TIMESTAMP DEFAULT NOW()
   );

   CREATE INDEX idx_eliza_memory_key ON eliza_memory(key);
   CREATE INDEX idx_eliza_memory_timestamp ON eliza_memory(timestamp);
   ```

## Usage

### Development Mode

```bash
# Activate environment
source eliza_env/bin/activate

# Run daemon
python3 enhanced_daemon.py
```

### Production Deployment

#### Option 1: Docker (Recommended)

```bash
# Build container
docker build -t eliza-daemon .

# Run with persistent volume
docker run -d \
  --name eliza-daemon \
  --restart unless-stopped \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config.meshnet.json:/app/config.meshnet.json \
  eliza-daemon
```

#### Option 2: Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/eliza-daemon.service
```

```ini
[Unit]
Description=Enhanced Eliza Daemon
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MESHNET/agents/eliza-daemon
Environment=PATH=/home/ubuntu/MESHNET/agents/eliza-daemon/eliza_env/bin
ExecStart=/home/ubuntu/MESHNET/agents/eliza-daemon/eliza_env/bin/python enhanced_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable eliza-daemon
sudo systemctl start eliza-daemon
sudo systemctl status eliza-daemon
```

## Monitoring and Maintenance

### Log Management

```bash
# View real-time logs
tail -f logs/eliza_daemon_$(date +%Y%m%d).log

# Docker logs
docker logs -f eliza-daemon
```

### Health Checks

The daemon exposes health metrics:
- Decision loop status
- Blockchain connectivity
- AI model availability
- Memory system health

### Performance Optimization

1. **Memory Management**
   - Configure memory window size in config
   - Regularly cleanup old log files
   - Monitor Supabase usage

2. **Blockchain Optimization**
   - Use appropriate gas prices
   - Batch transactions when possible
   - Monitor validator account balance

3. **AI Model Optimization**
   - Adjust temperature settings
   - Optimize prompt lengths
   - Use conversation memory efficiently

## Troubleshooting

### Common Issues

1. **Blockchain Connection Failed**
   ```bash
   # Check RPC URL and network
   curl -X POST -H "Content-Type: application/json" \
     --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
     YOUR_RPC_URL
   ```

2. **OpenAI API Errors**
   - Verify API key validity
   - Check rate limits and billing
   - Monitor token usage

3. **Memory System Issues**
   - Check Supabase connectivity
   - Verify table structure
   - Monitor database size limits

### Debug Mode

```bash
# Run with verbose logging
LOG_LEVEL=DEBUG python3 enhanced_daemon.py
```

## Security Considerations

1. **Private Key Security**
   - Never commit private keys to git
   - Use environment variables in production
   - Consider hardware wallet integration

2. **API Key Protection**
   - Rotate keys regularly
   - Monitor usage for anomalies
   - Use minimum required permissions

3. **Network Security**
   - Use HTTPS for all external connections
   - Implement rate limiting
   - Monitor for suspicious activity

## Performance Metrics

Expected performance characteristics:
- **Decision Cycle**: 10-15 seconds
- **Memory Usage**: 200-500MB
- **CPU Usage**: 5-15% (during active cycles)
- **Network**: 1-5MB per cycle

## Support and Development

For issues and contributions:
- GitHub Issues: https://github.com/DevGruGold/MESHNET/issues
- Documentation: https://github.com/DevGruGold/MESHNET/wiki
- Community: Discord Server

## License

MIT License - see LICENSE file for details.
