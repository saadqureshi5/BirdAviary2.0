from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from database import get_session
from models.clutch import ClutchCreate, ClutchRead, ClutchUpdate
from models.chick import ChickCreate, ChickRead, ChickUpdate
from models.bird import BirdRead
from services import breeding_service
from typing import Any, Optional

router = APIRouter()

@router.post("/pairings/{pairing_id}/clutches", response_model=ClutchRead)
def create_clutch(pairing_id: int, data: ClutchCreate, session: Session = Depends(get_session)):
    return breeding_service.create_clutch(session, pairing_id, data)

@router.put("/clutches/{clutch_id}", response_model=ClutchRead)
def update_clutch(clutch_id: int, data: ClutchUpdate, session: Session = Depends(get_session)):
    return breeding_service.update_clutch(session, clutch_id, data)

@router.post("/clutches/{clutch_id}/chicks", response_model=ChickRead)
def create_chick(clutch_id: int, data: ChickCreate, session: Session = Depends(get_session)):
    return breeding_service.create_chick(session, clutch_id, data)

@router.put("/chicks/{chick_id}", response_model=ChickRead)
def update_chick(chick_id: int, data: ChickUpdate, session: Session = Depends(get_session)):
    return breeding_service.update_chick(session, chick_id, data)

@router.post("/chicks/{chick_id}/promote", response_model=BirdRead)
def promote_chick_to_stock(chick_id: int, session: Session = Depends(get_session)):
    return breeding_service.promote_chick_to_stock(session, chick_id)

@router.get("/analytics", response_model=Any)
def get_breeding_analytics(category_id: Optional[int] = None, session: Session = Depends(get_session)):
    return breeding_service.get_breeding_analytics(session, category_id)
