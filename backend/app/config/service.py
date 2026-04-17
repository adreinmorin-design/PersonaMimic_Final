import base64
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.repository import config_repo

logger = logging.getLogger("config_service")


class ConfigService:
    def __init__(self, master_key: str = "dre_sentinel_2026"):
        self.salt = b"mimic_neural_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        if not token:
            return ""
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception as exc:
            logger.warning("Failed to decrypt config token: %s", exc)
            return "[DECRYPTION_ERROR]"

    def get_setting(self, db: Session, key: str) -> str | None:
        try:
            setting = config_repo.get_setting(db, key)
        except SQLAlchemyError as exc:
            logger.warning("Config lookup for '%s' failed; using defaults. Error: %s", key, exc)
            return None

        if not setting:
            return None

        value = setting.value
        return self.decrypt(value) if setting.is_encrypted else value

    def update_setting(self, db: Session, key: str, value: str, encrypt: bool = False):
        final_value = self.encrypt(value) if encrypt else value
        return config_repo.update_setting(db, key, final_value, is_encrypted=encrypt)

    def list_settings(self, db: Session, decrypt_all: bool = False) -> list[dict]:
        settings = config_repo.list_settings(db)
        rows = []
        for setting in settings:
            value = setting.value
            if setting.is_encrypted:
                value = self.decrypt(value) if decrypt_all else "********"

            rows.append(
                {
                    "key": setting.key,
                    "value": value,
                    "is_encrypted": setting.is_encrypted,
                }
            )
        return rows


config_service = ConfigService()

# --- SWARM DIRECTIVES & STATIC CONFIG ---

ROLE_MAP = {
    "Dre": "Solution Architect & Orchestrator",
    "Fenko": "Security Architect & Adversary",
    "Codesmith": "Lead Systems Engineer",
}

NICHES = [
    "Creator Productivity SaaS Apps",
    "B2B Workflow Automation Apps",
    "AI Assistant Micro-SaaS Apps",
    "Analytics and Reporting Dashboards",
    "Agency Operations Toolkits",
    "Premium Template and Workflow Studios",
]


def get_autonomous_directive(
    name: str,
    role_desc: str,
    knowledge_context: str,
    memory_context: str,
    hive_context: str,
    consensus_context: str,
) -> str:
    """Generate the master directive for autonomous studio production."""
    return (
        f"CRITICAL: You are the {role_desc} for the {name} node. "
        f"DOMAIN KNOWLEDGE: {knowledge_context or 'Standard professional patterns.'}\n"
        f"{memory_context}\n"
        "HYPER-AUTONOMOUS DISCOVERY PROTOCOL:\n"
        "PRIMARY MISSION: Scout, Architect, and Launch premium digital assets in new, high-value markets.\n"
        "1. DISCOVERY: If no specific niche is active, use `discover_new_niche` to find untapped market demand.\n"
        "2. STRATEGY: Distill research into buildable specs via `market_analyzer`. Choose the most innovative product type.\n"
        "3. PRODUCTION: Build robust, professional infrastructure via `assemble_full_product`.\n"
        "4. MEMORY: If a discovery is highly successful, use `add_to_global_niches` to update the hive mind.\n"
        "5. QUALITY GATE: Ensure every asset exceeds Studio-Grade standards before packaging.\n"
        f"{hive_context}{consensus_context}\n\n"
        "ADAPT AND INNOVATE. EMIT TOOL CALLS TO EXPAND THE STUDIO TERRITORY."
    )
