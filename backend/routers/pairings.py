from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from database import get_session
from models.pairing import PairingCreate, PairingRead, PairingUpdate
from services import breeding_service
from typing import List, Any

router = APIRouter()

@router.post("", response_model=PairingRead)
def create_pairing(data: PairingCreate, session: Session = Depends(get_session)):
    return breeding_service.create_pairing(session, data)

@router.get("", response_model=List[Any])
def list_pairings(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return breeding_service.get_all_pairings(session, skip, limit)

@router.get("/{pairing_id}", response_model=Any)
def get_pairing(pairing_id: int, session: Session = Depends(get_session)):
    return breeding_service.get_pairing_by_id(session, pairing_id)

@router.put("/{pairing_id}", response_model=PairingRead)
def update_pairing(pairing_id: int, data: PairingUpdate, session: Session = Depends(get_session)):
    return breeding_service.update_pairing(session, pairing_id, data)
