from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.swarm.models import ReviewPool
from app.swarm.schemas import AdversaryRequest, SwarmDirectiveRequest, SwarmSpawnRequest
from app.swarm.service import swarm_manager

router = APIRouter(prefix="/swarm", tags=["swarm"])


@router.post("/spawn")
async def swarm_spawn(req: SwarmSpawnRequest):
    brain = await swarm_manager.spawn(req.name, req.model, req.persona_type)
    if brain:
        brain.start(niche=req.niche)
    return {"status": "brain_spawned", "name": req.name}


@router.get("/status", response_model=dict[str, dict])
async def swarm_status():
    return swarm_manager.get_status()


@router.post("/stop")
async def swarm_stop(name: str):
    if name in swarm_manager.brains:
        swarm_manager.brains[name].stop()
        return {"status": "stopped"}
    return {"status": "not_found"}


@router.get("/autonomy/status")
async def autonomy_status():
    # Legacy support for main Dre brain
    if "Dre" not in swarm_manager.brains:
        return {"running": False, "tasks_completed": 0, "log": []}
    dre = swarm_manager.brains["Dre"]
    return {"running": dre.running, "tasks_completed": dre.task_count, "log": dre.log[-30:]}


@router.post("/adversary/review")
async def adversary_review(req: AdversaryRequest):
    """Manually trigger a peer adversary review."""
    from app.swarm.adversary_service import run_adversary_review

    try:
        verdict = run_adversary_review(req.product_name)
        return verdict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/directive")
async def set_swarm_directive(req: SwarmDirectiveRequest):
    swarm_manager.set_directive(req.directive)
    return {"status": "directive_updated", "directive": req.directive}


@router.get("/reviews")
async def get_reviews(db: Session = Depends(get_db)):
    reviews = (
        db.query(
            ReviewPool.id,
            ReviewPool.product_name,
            ReviewPool.reviewer_brain,
            ReviewPool.status,
            ReviewPool.critique,
            ReviewPool.iteration,
            ReviewPool.timestamp,
        )
        .order_by(ReviewPool.timestamp.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": review_id,
            "product_name": product_name,
            "reviewer_brain": reviewer_brain,
            "status": status,
            "critique": critique,
            "iteration": iteration,
            "timestamp": timestamp.isoformat() + "Z",
        }
        for review_id, product_name, reviewer_brain, status, critique, iteration, timestamp in reviews
    ]
