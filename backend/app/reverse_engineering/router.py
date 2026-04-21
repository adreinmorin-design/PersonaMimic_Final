from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.reverse_engineering.repository import reverse_engineering_repo
from app.reverse_engineering.schemas import (
    AgentTargetCreateRequest,
    AgentTargetResponse,
    ReplicatedToolResponse,
    SynthesisRequest,
    SynthesisResponse,
)
from app.reverse_engineering.service import reverse_engineering_service

router = APIRouter(prefix="/reverse-engineering", tags=["reverse-engineering"])


@router.post(
    "/synthesize",
    response_model=SynthesisResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def synthesize_pattern(request: SynthesisRequest, db: Session = Depends(get_db)):
    if not request.target.strip() or not request.cluster_id.strip():
        raise HTTPException(status_code=400, detail="Invalid target or cluster.")

    job = await reverse_engineering_service.trigger_synthesis(db, request)
    if not job:
        raise HTTPException(status_code=400, detail="Failed to initialize synthesis job.")

    return job


@router.get("/status/{job_id}", response_model=SynthesisResponse)
async def check_job_status(job_id: int, db: Session = Depends(get_db)):
    if job_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    job = await reverse_engineering_repo.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/history", response_model=list[SynthesisResponse])
async def get_synthesis_history(db: Session = Depends(get_db)):
    """Fetch the vault of all synthesized industrial artifacts."""
    return await reverse_engineering_repo.list_all_jobs(db)


@router.get("/targets", response_model=list[AgentTargetResponse])
async def list_targets(db: Session = Depends(get_db)):
    targets = await reverse_engineering_service.list_targets(db)
    return [reverse_engineering_service.serialize_target(target) for target in targets]


@router.post("/targets", response_model=AgentTargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(request: AgentTargetCreateRequest, db: Session = Depends(get_db)):
    try:
        target = await reverse_engineering_service.create_custom_target(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return reverse_engineering_service.serialize_target(target)


@router.get("/tools", response_model=list[ReplicatedToolResponse])
async def list_tools(
    target_id: str | None = None,
    tool_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    tools = await reverse_engineering_repo.list_replicated_tools(
        db,
        target_id=target_id,
        status=tool_status,
    )
    return [reverse_engineering_service.serialize_tool(tool) for tool in tools]


@router.get("/tools/{tool_id}", response_model=ReplicatedToolResponse)
async def get_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = await reverse_engineering_repo.get_replicated_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Replicated tool not found")
    return reverse_engineering_service.serialize_tool(tool)


@router.get("/jobs/{job_id}/tools", response_model=list[ReplicatedToolResponse])
async def get_job_tools(job_id: int, db: Session = Depends(get_db)):
    if job_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    tools = await reverse_engineering_repo.list_replicated_tools_by_job(db, job_id)
    return [reverse_engineering_service.serialize_tool(tool) for tool in tools]
