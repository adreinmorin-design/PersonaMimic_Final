import json
import logging

from app.swarm.persona_engine import PersonaEngine

logger = logging.getLogger("swarm.tools.orchestration")


async def strategic_planner(niche: str, current_specs: str = ""):
    """
    Top-Notch Orchestrator: High-level strategic planning for product development.
    Uses Reasoning (DeepSeek-R1) followed by Architecture (Qwen-32B).
    """
    try:
        import os

        # Step 1: Deep Reasoning (Think)
        # We use qwen2.5-coder:7b for its superior chain-of-thought capabilities
        reasoning_engine = PersonaEngine(model="qwen2.5-coder:7b")
        thought_prompt = (
            f"STRATEGIC THINKING: You are the Lead Architect for PersonaMimic.\n"
            f"MISSION: Build a product in the '{niche}' niche.\n"
            f"INITIAL SPECS: {current_specs}\n\n"
            "TASK: Perform deep architectural reasoning. Think about the domain model, "
            "potential scalability issues, and industrial standards (DDD, Guard Clauses).\n"
            "Output your chain of thought on how to build this perfectly."
        )

        logger.info("Orchestrator: Engaging Reasoning Engine (Qwen-Coder)...")
        thought_res = await reasoning_engine.generate_response(
            thought_prompt, persona_type="reasoning"
        )
        thoughts = thought_res.get("content", "No specific architectural thoughts.")

        # Step 2: Formal Architecture (Do)
        # We use the 32B Coder model (or cloud fallback) to turn thoughts into a manifest
        model = os.getenv("CLOUD_MODEL", "qwen2.5-coder:7b")
        engine = PersonaEngine(model=model)

        logger.info(f"Orchestrator: Engaging Architecture Engine ({model})...")
        prompt = (
            f"MISSION ARCHITECT: Create a build plan based on these strategic thoughts:\n\n"
            f"STRATEGIC THOUGHTS:\n{thoughts}\n\n"
            f"TARGET NICHE: {niche}\n"
            f"INITIAL SPECS: {current_specs}\n\n"
            "OUTPUT: Respond ONLY with a JSON object containing 'product_name', 'refined_specs', and 'file_manifest'."
        )

        res = await engine.generate_response(prompt, persona_type="director")
        content = res.get("content", "{}")

        # Ensure we have valid JSON
        from app.swarm.persona_engine import ResponseParser

        data = ResponseParser.extract_json(content)
        if not data:
            data = {"refined_specs": content, "product_name": f"{niche}_tool"}

        return json.dumps(data)
    except Exception as e:
        logger.error(f"Strategic planning failed: {e}")
        return json.dumps({"error": str(e), "refined_specs": current_specs})
