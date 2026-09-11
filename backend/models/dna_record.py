from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class DNARecordBase(SQLModel):
    bird_id: int = Field(foreign_key='bird.id')
    file_path: str
    file_type: str # image/pdf

class DNARecord(DNARecordBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DNARecordCreate(DNARecordBase):
    pass

class DNARecordRead(DNARecordBase):
    id: int
    created_at: datetime
