from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from models.soft_food import SoftFoodLogRead, SoftFoodLogCreate, SoftFoodLogUpdate
from services import soft_food_service
from typing import List, Optional

router = APIRouter()

@router.post("", response_model=SoftFoodLogRead)
def create_soft_food_log(data: SoftFoodLogCreate, session: Session = Depends(get_session)):
    return soft_food_service.create_soft_food_log(session, data)

@router.get("", response_model=List[SoftFoodLogRead])
def list_soft_food_logs(
    year: Optional[int] = None,
    season: Optional[str] = None,
    session: Session = Depends(get_session)
):
    return soft_food_service.get_all_soft_food_logs(session, year, season)

@router.get("/{id}", response_model=SoftFoodLogRead)
def get_soft_food_log(id: int, session: Session = Depends(get_session)):
    return soft_food_service.get_soft_food_log(session, id)

@router.put("/{id}", response_model=SoftFoodLogRead)
def update_soft_food_log(id: int, data: SoftFoodLogUpdate, session: Session = Depends(get_session)):
    return soft_food_service.update_soft_food_log(session, id, data)

@router.delete("/{id}")
def delete_soft_food_log(id: int, session: Session = Depends(get_session)):
    soft_food_service.delete_soft_food_log(session, id)
    return {"message": "Soft food log deleted successfully"}
