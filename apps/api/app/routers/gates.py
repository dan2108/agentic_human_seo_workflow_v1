from fastapi import APIRouter
from app.schemas.gate import GateDecisionRequest, GateResponse

router = APIRouter()


@router.get("/{gate_id}", response_model=GateResponse)
async def get_gate(gate_id: str) -> dict:
    # TODO: fetch gate + AI output from Supabase
    raise NotImplementedError


@router.post("/{gate_id}/approve")
async def approve_gate(gate_id: str, request: GateDecisionRequest) -> dict:
    # TODO: update gate status, dispatch next phase via orchestrator
    raise NotImplementedError


@router.post("/{gate_id}/reject")
async def reject_gate(gate_id: str, request: GateDecisionRequest) -> dict:
    # TODO: update gate status, notify relevant step to revise
    raise NotImplementedError
