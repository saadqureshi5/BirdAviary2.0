from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class SaleBase(SQLModel):
    bird_id: int = Field(foreign_key='bird.id')
    sale_price: float = Field(default=0.0)
    buyer_name: Optional[str] = None
    notes: Optional[str] = None


class Sale(SaleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date_sold: datetime = Field(default_factory=datetime.utcnow)


class SaleCreate(SaleBase):
    date_sold: Optional[datetime] = None


class SaleUpdate(SQLModel):
    sale_price: Optional[float] = None
    buyer_name: Optional[str] = None
    notes: Optional[str] = None
    date_sold: Optional[datetime] = None


class SaleRead(SaleBase):
    id: int
    date_sold: datetime
