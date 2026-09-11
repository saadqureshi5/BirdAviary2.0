from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class ClutchBase(SQLModel):
    pairing_id: int = Field(foreign_key='pairing.id')
    clutch_date: datetime = Field(default_factory=datetime.utcnow)
    total_eggs: int = Field(default=0)
    fertile_eggs: int = Field(default=0)
    hatched_eggs: int = Field(default=0)
    eggs_lost: int = Field(default=0)
    loss_reason: Optional[str] = None
    notes: Optional[str] = None

class Clutch(ClutchBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClutchCreate(ClutchBase):
    pass

class ClutchRead(ClutchBase):
    id: int
    created_at: datetime

class ClutchUpdate(SQLModel):
    clutch_date: Optional[datetime] = None
    total_eggs: Optional[int] = None
    fertile_eggs: Optional[int] = None
    hatched_eggs: Optional[int] = None
    eggs_lost: Optional[int] = None
    loss_reason: Optional[str] = None
    notes: Optional[str] = None
