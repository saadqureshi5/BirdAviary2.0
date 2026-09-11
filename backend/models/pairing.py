from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class PairingBase(SQLModel):
    bird_a_id: int = Field(foreign_key='bird.id')
    bird_b_id: int = Field(foreign_key='bird.id')
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    cage_number: Optional[str] = None
    notes: Optional[str] = None

class Pairing(PairingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PairingCreate(PairingBase):
    pass

class PairingRead(PairingBase):
    id: int
    created_at: datetime

class PairingUpdate(SQLModel):
    end_date: Optional[datetime] = None
    cage_number: Optional[str] = None
    notes: Optional[str] = None
