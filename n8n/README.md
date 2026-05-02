# n8n Automation for PersonaMimic

This directory contains the n8n automation suite for the PersonaMimic Industrial Loop.

## How to Start
1. Run `docker-compose up -d n8n`.
2. Access the n8n interface at `http://localhost:5678`.
3. Create your first account.
4. Import the workflows from this directory.

## Workflows Included

### 1. `industrial_distribution_loop.json`
- **Purpose**: Automatically detects new digital products in the `./products` directory and prepares them for market launch.
- **Trigger**: File Watcher (on `/home/node/products`).
- **Action**: Zips the product, generates a marketing description via the backend API, and (optionally) posts to a webhook.

### 2. `swarm_monitor.json`
- **Purpose**: Periodically polls the `/swarm/status` endpoint and sends alerts if any "brain" is stuck or has high error rates.
- **Trigger**: Schedule (every 5 minutes).
- **Action**: HTTP Request to `http://backend:8055/swarm/status`.

## Integration Tips
- Use the `http://backend:8055` URL within n8n to communicate with the internal API.
- The `products` folder is shared between the host and the n8n container.
