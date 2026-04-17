from fastapi import APIRouter, HTTPException

from app.core.paths import DATABASE_PATH
from app.forge.diagnostic import diagnostic_suite
from app.forge.steering import INDUSTRIAL_STEERING_COLLECTION, steer_service
from app.forge.training import forge_worker

router = APIRouter(prefix="/forge", tags=["forge"])


@router.get("/status")
async def forge_status():
    """Hardware and Neural Audit: Monitor the health of the Forge."""
    return diagnostic_suite.benchmark_memory()


@router.get("/features")
async def list_features():
    """List available steering features (reverse-engineered from SAEs)."""
    return INDUSTRIAL_STEERING_COLLECTION


@router.post("/steer")
async def apply_steering(feature_name: str, coefficient: float = 1.0):
    """Apply an activation steering vector to the swarm's neural fabric."""
    if feature_name not in INDUSTRIAL_STEERING_COLLECTION:
        raise HTTPException(status_code=404, detail="Feature not found in collection.")

    feature = INDUSTRIAL_STEERING_COLLECTION[feature_name]
    steer_service.add_vector(
        name=feature_name,
        layer=feature["layer"],
        vector_data=feature["vector"],
        coefficient=coefficient,
    )
    return {"status": "steered", "feature": feature_name, "coefficient": coefficient}


@router.post("/train/autostart")
async def trigger_training():
    """Trigger an autonomous fine-tuning session based on historical quality gaps."""
    try:
        dataset = forge_worker.prepare_dataset(DATABASE_PATH)
        run_id = forge_worker.trigger_training(dataset)
        return {"status": "training_initiated", "run_id": run_id, "sample_count": len(dataset)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forge training failed: {str(e)}") from e


@router.delete("/steer/clear")
async def clear_steering():
    """Remove all steering vectors and reset the model to base behavior."""
    steer_service.clear()
    return {"status": "reset_to_base"}
