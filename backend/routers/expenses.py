from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from models.expense import ExpenseRead, ExpenseCreate, ExpenseUpdate
from services import expense_service
from typing import List, Optional

router = APIRouter()

@router.post("", response_model=ExpenseRead)
def create_expense(data: ExpenseCreate, session: Session = Depends(get_session)):
    return expense_service.create_expense(session, data)

@router.get("/analytics")
def get_expense_analytics(session: Session = Depends(get_session)):
    return expense_service.get_expense_analytics(session)

@router.get("", response_model=List[ExpenseRead])
def list_expenses(
    year: Optional[int] = None,
    month: Optional[int] = None,
    session: Session = Depends(get_session)
):
    return expense_service.get_all_expenses(session, year, month)

@router.get("/{id}", response_model=ExpenseRead)
def get_expense(id: int, session: Session = Depends(get_session)):
    return expense_service.get_expense(session, id)

@router.put("/{id}", response_model=ExpenseRead)
def update_expense(id: int, data: ExpenseUpdate, session: Session = Depends(get_session)):
    return expense_service.update_expense(session, id, data)

@router.delete("/{id}")
def delete_expense(id: int, session: Session = Depends(get_session)):
    expense_service.delete_expense(session, id)
    return {"message": "Expense deleted successfully"}
