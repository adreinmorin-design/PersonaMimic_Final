from fastapi import APIRouter, Request
from app.swarm.service import swarm_manager
import logging

logger = logging.getLogger("n8n_integration")

router = APIRouter(prefix="/n8n", tags=["n8n"])

@router.post("/trigger-swarm")
async def trigger_swarm_from_n8n(payload: dict):
    """
    Triggered by n8n to start a new swarm mission.
    Expects: {"niche": "...", "goal": "..."}
    """
    niche = payload.get("niche", "Market Discovery")
    goal = payload.get("goal", "Automated product synthesis")
    
    # We use MasterBrain as the entry point for n8n-triggered tasks
    master = await swarm_manager.spawn("MasterBrain", "llama-3.3-70b-versatile", "director")
    if master:
        # Update global directive and start
        swarm_manager.set_directive(goal)
        master.start(niche=niche)
        return {"status": "triggered", "brain": "MasterBrain", "niche": niche}
    
    return {"status": "error", "message": "Failed to spawn MasterBrain"}

@router.get("/health")
async def n8n_health():
    return {"status": "ready", "integration": "active"}
