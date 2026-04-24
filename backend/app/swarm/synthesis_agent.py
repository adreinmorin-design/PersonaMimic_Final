# © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset
#
# app/swarm/synthesis_agent.py - Forensic Neural Synthesizer
# Translates decompiled neural patterns into functional code.
#

import asyncio
import logging
import re

from app.config.service import config_service
from app.database.database import db_session as get_db
from app.forge.diagnostic import diagnostic_suite
from app.swarm.persona_engine import PersonaEngine

logger = logging.getLogger("swarm.synthesis")


class SynthesisAgent:
    """
    The Forensic Synthesizer:
    Bridges the gap between Mechanistic Interpretability and Code Generation.
    """

    def __init__(self, model_name: str = "qwen2.5-coder:7b"):
        self.engine = PersonaEngine(model=model_name)

    @staticmethod
    def _extract_section(content: str, label: str, all_labels: list[str]) -> str:
        start_pattern = re.compile(rf"(?im)^\s*{re.escape(label)}\s*:\s*")
        start_match = start_pattern.search(content)
        if not start_match:
            return ""

        start = start_match.end()
        next_index = len(content)
        for candidate in all_labels:
            if candidate == label:
                continue
            candidate_match = re.search(
                rf"(?im)^\s*{re.escape(candidate)}\s*:\s*",
                content[start:],
            )
            if candidate_match:
                next_index = min(next_index, start + candidate_match.start())
        return content[start:next_index].strip()

    def _parse_structured_payload(self, content: str) -> dict[str, object]:
        labels = [
            "TOOL_NAME",
            "PURPOSE_SUMMARY",
            "EXPLANATION",
            "PREREQUISITES[]",
            "SETUP_STEPS[]",
            "RUN_STEPS[]",
            "INTEGRATION_STEPS[]",
            "LIMITATIONS[]",
            "CODE",
        ]

        parsed = {
            "tool_name": self._extract_section(content, "TOOL_NAME", labels),
            "purpose_summary": self._extract_section(content, "PURPOSE_SUMMARY", labels),
            "explanation": self._extract_section(content, "EXPLANATION", labels),
            "prerequisites": self._extract_section(content, "PREREQUISITES[]", labels),
            "setup_steps": self._extract_section(content, "SETUP_STEPS[]", labels),
            "run_steps": self._extract_section(content, "RUN_STEPS[]", labels),
            "integration_steps": self._extract_section(content, "INTEGRATION_STEPS[]", labels),
            "limitations": self._extract_section(content, "LIMITATIONS[]", labels),
            "code": self._extract_section(content, "CODE", labels),
        }
        return parsed

    async def synthesize_from_cluster(
        self, cluster_id: str, context: str = ""
    ) -> dict[str, object]:
        """
        Reads a neural cluster via the diagnostic suite and generates code + purpose blurb.
        """
        logger.info(f"[SYNTHESIS] Decoding and Synthesizing Cluster: {cluster_id}")

        # 1. Forensic Decompilation
        pattern = diagnostic_suite.neural_decompile(cluster_id)
        if "Unknown" in pattern:
            return {
                "code": f"# Error: Could not synthesize from unknown cluster {cluster_id}",
                "purpose": "Unknown",
            }

        logger.info(f"[SYNTHESIS] Patterns identified: {pattern}")

        # 2. Neural Generation Directive
        prompt = f"""
        ## MISSION: SENSORY SYNTHESIS (STUDIO GRADE)
        You are implementing high-performance code identified via neural forensic reverse-engineering.
        Your output MUST emulate the peak performance of elite tools like SWE-Agent and OpenHands.

        ## IDENTIFIED PATTERN:
        {pattern}

        ## CONTEXT:
        {context}

        ## REQUIREMENTS:
        Return ONLY these sections in this exact format:
        TOOL_NAME: [Official name of the replicated logic component]
        PURPOSE_SUMMARY: [Clear, industrial-standard purpose]
        EXPLANATION: [Depth-heavy explanation for digital product architects]
        PREREQUISITES[]: [one bullet per line, include all required dependencies]
        SETUP_STEPS[]: [one numbered step per line]
        RUN_STEPS[]: [one numbered step per line]
        INTEGRATION_STEPS[]: [one numbered step per line]
        LIMITATIONS[]: [one bullet per line, be brutally honest about edge cases]
        CODE: [fully functional, production-ready implementation.
              STRICT RULE 1: EVERY file MUST begin with the '© 2026 Dre's Autonomous Neural Interface | Professional Grade Asset' header.
              STRICT RULE 2: EVERY function must be wrapped in a try/except block with professional logging (import logging).
              STRICT RULE 3: No placeholders, no TODOs, no 'pass' statements.
              The code must be valid, bug-free, and complete.]
        """

        response = await self.engine.generate_response(prompt, persona_type="coding")
        content = response.get("content", "")
        structured = self._parse_structured_payload(content)

        purpose = (
            structured["purpose_summary"] or "Industrial tool integrated for system optimization."
        )
        generated_code = structured["code"] or content

        # 3. Hybrid Quality Gate Assessment (#3 - Best Practice)
        archetype_match = diagnostic_suite.trace_archetype_influence(pattern, None)
        semantic_score = await self._evaluate_forensic_quality(pattern, generated_code)
        final_score = (archetype_match * 0.4) + (semantic_score * 0.6)

        with get_db() as db:
            threshold_str = await asyncio.to_thread(
                config_service.get_setting, db, "min_forensic_score"
            )
            threshold = float(threshold_str) if threshold_str else 0.75

        if final_score < threshold:
            logger.warning(
                f"[QUALITY-GATE] REJECTED. Score: {final_score:.2f} < Threshold: {threshold}"
            )
            return {
                "code": f"# Quality Gate Rejection: Hybrid score {final_score:.2f} failed to meet studio threshold.",
                "purpose": purpose,
                "purpose_summary": purpose,
                "tool_name": structured["tool_name"] or "Rejected Tool Artifact",
                "explanation": structured["explanation"],
                "prerequisites": structured["prerequisites"],
                "setup_steps": structured["setup_steps"],
                "run_steps": structured["run_steps"],
                "integration_steps": structured["integration_steps"],
                "limitations": structured["limitations"],
                "raw_content": content,
            }

        logger.info(
            f"[SYNTHESIS] Successfully forged code (Score: {final_score:.2f}) for pattern: {pattern}"
        )
        return {
            "code": generated_code,
            "purpose": purpose,
            "purpose_summary": purpose,
            "tool_name": structured["tool_name"] or "Replicated Tool",
            "explanation": structured["explanation"],
            "prerequisites": structured["prerequisites"],
            "setup_steps": structured["setup_steps"],
            "run_steps": structured["run_steps"],
            "integration_steps": structured["integration_steps"],
            "limitations": structured["limitations"],
            "raw_content": content,
        }

    async def _evaluate_forensic_quality(self, pattern: str, code: str) -> float:
        """
        Self-evaluation audit to determine if synthesized code matches neural signals.
        """
        eval_prompt = f"""
        ## MISSION: FORENSIC AUDIT
        Evaluate the following synthesized code against the identified neural pattern.

        ## PATTERN:
        {pattern}

        ## SYNTHESIZED CODE:
        ```
        {code}
        ```

        ## TASK:
        Rate the alignment between the code and the pattern from 0.0 to 1.0.
        Consider: Functional accuracy, structural mapping, and professional standards.
        Return ONLY a single numeric value.
        """
        eval_resp = await self.engine.generate_response(eval_prompt, persona_type="reasoning")
        content = eval_resp.get("content", "0.0").strip()

        # Extract float
        try:
            import re

            match = re.search(r"(\d\.\d+)", content)
            return float(match.group(1)) if match else float(content)
        except Exception:
            return 0.5


# Singleton instance
synthesis_agent = SynthesisAgent()
