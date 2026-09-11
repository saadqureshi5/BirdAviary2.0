from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class ChickBase(SQLModel):
    clutch_id: int = Field(foreign_key='clutch.id')
    ring_id: Optional[str] = None
    mutation: Optional[str] = None
    sex: str = Field(default='unknown')
    status: str = Field(default='hatched') # hatched, fledged, deceased, added_to_stock
    mortality_reason: Optional[str] = None
    promoted_bird_id: Optional[int] = Field(default=None, foreign_key='bird.id')
    hatch_date: Optional[datetime] = None
    fledge_date: Optional[datetime] = None

class Chick(ChickBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChickCreate(SQLModel):
    clutch_id: int
    ring_id: Optional[str] = None
    mutation: Optional[str] = None
    sex: str = 'unknown'
    hatch_date: Optional[datetime] = None

class ChickRead(ChickBase):
    id: int
    created_at: datetime

class ChickUpdate(SQLModel):
    status: Optional[str] = None
    mortality_reason: Optional[str] = None
    fledge_date: Optional[datetime] = None
    ring_id: Optional[str] = None
    mutation: Optional[str] = None
    sex: Optional[str] = None
    hatch_date: Optional[datetime] = None
