"""
app/swarm/nats_service.py - High-speed industrial message bus
Utilizes NATS for microsecond-latency task handoffs and agent synchronization.
"""

import json
import logging
import os

import nats
from nats.errors import NoServersError, TimeoutError

logger = logging.getLogger("swarm.nats")


class NatsService:
    def __init__(self, url: str | None = None):
        self.url = url or os.getenv("NATS_URL", "nats://localhost:4222")
        self.nc = None

    async def connect(self):
        """Establish connection to the high-speed NATS bus."""
        try:
            # Add a strict timeout to avoid blocking the swarm loop
            self.nc = await nats.connect(self.url, connect_timeout=2)
            logger.info(f"NATS Bus Connected: {self.url}")
        except (NoServersError, TimeoutError, Exception) as e:
            logger.error(
                f"NATS Connection Error: {e}. Swarm telemetry falling back to local logging."
            )
            self.nc = None

    async def publish_task(self, subject: str, task_data: dict):
        """Publish a task to the swarm."""
        if not self.nc:
            await self.connect()

        if self.nc:
            payload = json.dumps(task_data).encode()
            await self.nc.publish(subject, payload)
            logger.debug(f"NATS Published -> {subject}")

    async def subscribe(self, subject: str, callback):
        """Subscribe to a specific swarm channel."""
        if not self.nc:
            await self.connect()

        if self.nc:

            async def msg_handler(msg):
                data = json.loads(msg.data.decode())
                await callback(data)

            await self.nc.subscribe(subject, cb=msg_handler)
            logger.info(f"NATS Subscribed -> {subject}")

    async def request(self, subject: str, task_data: dict, timeout: int = 30):
        """Synchronous request-response over NATS."""
        if not self.nc:
            await self.connect()

        if self.nc:
            payload = json.dumps(task_data).encode()
            try:
                msg = await self.nc.request(subject, payload, timeout=timeout)
                return json.loads(msg.data.decode())
            except TimeoutError:
                logger.warning(f"NATS Request Timing Out: {subject}")
                return {"error": "NATS_TIMEOUT"}
        return {"error": "NATS_DISCONNECTED"}

    async def close(self):
        if self.nc:
            await self.nc.close()
            logger.info("NATS Bus Disconnected.")


# Singleton for the swarm
nats_service = NatsService()
