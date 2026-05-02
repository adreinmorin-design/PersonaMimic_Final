import asyncio
import datetime
import logging
import random

from sqlalchemy.orm import Session

from app.config.service import config_service
from app.reverse_engineering.repository import reverse_engineering_repo
from app.swarm.models import UsageQuota
from app.swarm.repository import swarm_repo

logger = logging.getLogger("swarm.governor")


class SwarmGovernor:
    """
    Industrial Governance Node:
    Enforces quotas, probability weights, and whitelists for autonomous brains.
    """

    @staticmethod
    async def get_quota(db: Session, brain_name: str) -> UsageQuota:
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        quota = await swarm_repo.get_quota(db, brain_name, today)
        if not quota:
            quota = UsageQuota(
                brain_name=brain_name, day=today, tokens_consumed=0, tasks_completed=0
            )
            db.add(quota)
            db.commit()
            db.refresh(quota)
        return quota

    @staticmethod
    async def check_token_limit(db: Session, brain_name: str) -> bool:
        quota = await SwarmGovernor.get_quota(db, brain_name)
        limit_str = await asyncio.to_thread(config_service.get_setting, db, "daily_token_quota")
        limit = int(limit_str) if limit_str else 1000000

        if quota.tokens_consumed >= limit:
            logger.warning(f"[GOVERNOR] Quota Lock: {brain_name} reached limit ({limit}).")
            return False
        return True

    @staticmethod
    def get_autonomous_mission_type(db: Session) -> str:
        """Determines if the next mission should be Market Discovery or Reverse Engineering."""
        prob_str = config_service.get_setting(db, "synthesis_probability")
        synthesis_prob = float(prob_str) if prob_str else 0.5

        if random.random() < synthesis_prob:
            return "reverse_engineering"
        return "market_discovery"

    @staticmethod
    async def get_synthesis_target(db: Session) -> str:
        """Returns a random reverse-engineering target from the catalog."""
        targets = await reverse_engineering_repo.list_targets(db)
        if targets:
            return random.choice(targets).target_id

        # Fallback safety if catalog is unavailable.
        return random.choice(
            [
                "openhands",
                "crewai",
                "metagpt",
                "autogpt",
                "superagi",
                "gpt-engineer",
                "devika",
                "swe-agent",
            ]
        )

    @staticmethod
    async def track_usage(db: Session, brain_name: str, tokens: int = 0):
        """Updates the brain's daily quota usage."""
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        await swarm_repo.track_usage(db, brain_name, today, tokens)


swarm_governor = SwarmGovernor()
