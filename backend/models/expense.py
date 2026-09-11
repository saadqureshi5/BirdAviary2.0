from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import date, datetime
from typing import Optional

class ExpenseBase(SQLModel):
    year: int
    month: int
    date: date
    description: str
    amount: float

class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(SQLModel):
    year: Optional[int] = None
    month: Optional[int] = None
    date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = None

class ExpenseRead(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: datetime
