"""
app/swarm/compliance_service.py - Industrial Legal & Support Generation
Handles autonomous generation of FAQs, Terms of Service, and Privacy Policies.
"""

import asyncio
import logging
import os

from app.core.paths import WORKSPACE_DIR
from app.swarm.persona_engine import PersonaEngine

logger = logging.getLogger("swarm.compliance")


class ComplianceService:
    def __init__(self):
        self.engine = PersonaEngine()

    async def generate_faq(self, product_name: str, niche: str, specs: str) -> str:
        """Generates a comprehensive FAQ document for the product."""
        prompt = (
            f"Generate a comprehensive FAQ (Frequently Asked Questions) document for '{product_name}' in the '{niche}' niche.\n"
            f"Technical Specs: {specs}\n\n"
            "Requirements:\n"
            "- Include at least 8 high-value questions covering features, setup, and support.\n"
            "- Use a professional, studio-grade tone.\n"
            "- Format as a clean MARKDOWN file.\n"
            "- NO EXPLANATION. OUTPUT ONLY THE MARKDOWN CONTENT."
        )
        res = await self.engine.generate_response(prompt, persona_type="mimic")
        content = res.get("content", "# FAQ")

        # Ensure it's not wrapped in backticks
        if content.startswith("```"):
            from app.swarm.tools.base import _extract_code

            content = _extract_code(content)

        return content

    async def generate_legal_bundle(self, product_name: str, niche: str) -> dict[str, str]:
        """Generates Terms of Service and Privacy Policy."""
        bundle = {}

        # 1. Terms of Service
        tos_prompt = (
            f"Generate a 'Studio-Grade' Terms of Service agreement for '{product_name}', a digital product in the '{niche}' niche.\n\n"
            "Requirements:\n"
            "- Standard clauses: License, Restrictions, Termination, Limitation of Liability, Governing Law.\n"
            "- Include 'Dre Proprietary' as the governing entity.\n"
            "- Professional legal tone (Studio Standard).\n"
            "- Format as MARKDOWN.\n"
            "- NO EXPLANATION. OUTPUT ONLY THE MARKDOWN CONTENT."
        )
        tos_res = await self.engine.generate_response(tos_prompt, persona_type="mimic")
        bundle["TERMS_OF_SERVICE.md"] = tos_res.get("content", "# Terms of Service")

        # 2. Privacy Policy
        pp_prompt = (
            f"Generate a 'Studio-Grade' Privacy Policy for '{product_name}' in the '{niche}' niche.\n\n"
            "Requirements:\n"
            "- GDPR/CCPA compliance baseline.\n"
            "- Clauses: Data Collection, Usage, Third-Party Sharing, User Rights.\n"
            "- Format as MARKDOWN.\n"
            "- NO EXPLANATION. OUTPUT ONLY THE MARKDOWN CONTENT."
        )
        pp_res = await self.engine.generate_response(pp_prompt, persona_type="mimic")
        bundle["PRIVACY_POLICY.md"] = pp_res.get("content", "# Privacy Policy")

        # Clean all content
        from app.swarm.tools.base import _extract_code

        for key in bundle:
            if bundle[key].strip().startswith("```"):
                bundle[key] = _extract_code(bundle[key])

        return bundle

    async def write_compliance_docs(self, product_name: str, niche: str, specs: str) -> str:
        """Generates and writes all compliance and support docs to the workspace."""
        try:
            target_dir = os.path.join(WORKSPACE_DIR, product_name)
            await asyncio.to_thread(os.makedirs, target_dir, exist_ok=True)

            log = [f"[*] Generating Compliance Bundle for {product_name}"]

            # FAQ
            faq_content = await self.generate_faq(product_name, niche, specs)

            def _write_faq():
                with open(os.path.join(target_dir, "FAQ.md"), "w", encoding="utf-8") as f:
                    f.write(faq_content)

            await asyncio.to_thread(_write_faq)
            log.append("[OK] FAQ.md generated.")

            # Legal
            legal_bundle = await self.generate_legal_bundle(product_name, niche)

            def _write_legal():
                for filename, content in legal_bundle.items():
                    with open(os.path.join(target_dir, filename), "w", encoding="utf-8") as f:
                        f.write(content)

            await asyncio.to_thread(_write_legal)
            log.append("[OK] Legal documents generated.")

            return "\n".join(log)
        except Exception as e:
            logger.error(f"Compliance generation failed: {e}")
            return f"Compliance Error: {str(e)}"


compliance_service = ComplianceService()
