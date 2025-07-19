# MESHNET: XMRT-Meshtastic Full-Stack Ecosystem

## Overview
MESHNET is a monorepo integrating Meshtastic mesh networking with the XMRT ecosystem for resilient, off-grid, agent-driven applications. Built for full-stack functionality: frontend UIs, backend bridges/agents, and core mesh logic.

### Structure
- **frontend/**: Web dashboards (from xmrt-meshtastic-web).
- **backend/**: Bridges and agents (from xmrt-bridge, xmrt-agents).
- **mesh/**: Meshtastic core (Python/Rust integrations).
- **utils/**: Shared tools/scripts.
- **docs/**: Guides and API refs.

### Setup
1. Clone: `git clone https://github.com/DevGruGold/MESHNET.git`
2. Install: `npm install` (for Node) and `pip install -r requirements.txt` (for Python).
3. Run: `npm start` for frontend, or `python backend/bridge.py` for bridging.

### Usage
- Simulate: Run integration script with 'simulate' port.
- Live: Connect Meshtastic hardware and bridge to XMRT API.
- Extend: Add agents for AI routing or trust scoring.

### Contributing
Fork, PR, or collaborate—let's mesh the world! 🚀

License: MIT (or your choice).

## Next Phase Enhancements
- **Docker Support:** Run with `docker compose up` for full-stack deployment.
- **CI/CD:** GitHub Actions auto-tests on push.
- **Diagrams:** (Add your architecture diagram here, e.g., via draw.io).

## Roadmap
- v1.1: Add real-time agent analytics.
- v2.0: Mobile integrations with Android/Apple forks.

Badges: [![CI](https://github.com/DevGruGold/MESHNET/actions/workflows/ci.yml/badge.svg)](https://github.com/DevGruGold/MESHNET/actions)

## Next Next Phase: Dashboard & Deployment
- **Dashboard:** Run `streamlit run frontend/dashboard/app.py` for real-time monitoring.
- **Tests:** `python -m unittest discover utils/tests`.
- **Deployment:** GitHub Actions for Vercel/cloud deploys.

## Next Next Next Phase: Auth, Integrations, Cloud Demo
- **Authentication:** Secure dashboard with passwords/OAuth.
- **Advanced Features:** Live mesh data and agent analytics.
- **Cloud Demo:** Deployed via Render/Heroku—try the live version [here](link).
