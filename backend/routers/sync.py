from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services import sync_service
from pydantic import BaseModel

router = APIRouter()

class MarkSyncedRequest(BaseModel):
    entry_ids: list[int]

class ReplayRequest(BaseModel):
    entries: list[dict]

@router.get("/pending")
def get_pending(limit: int = Query(100), session: Session = Depends(get_session)):
    entries = sync_service.get_pending_entries(session, limit)
    return {"items": entries, "total": len(entries)}

@router.post("/mark-synced")
def mark_synced(request: MarkSyncedRequest, session: Session = Depends(get_session)):
    count = sync_service.mark_entries_synced(session, request.entry_ids)
    return {"marked_count": count}

@router.post("/replay")
def replay(request: ReplayRequest, session: Session = Depends(get_session)):
    result = sync_service.replay_entries(session, request.entries)
    return result

@router.get("/status")
def get_status(session: Session = Depends(get_session)):
    return sync_service.get_sync_status(session)
