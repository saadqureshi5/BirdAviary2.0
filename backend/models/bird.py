from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class BirdBase(SQLModel):
    ring_id: Optional[str] = Field(default=None, unique=True, index=True)
    name: Optional[str] = Field(default=None, index=True)
    mutation: Optional[str] = None
    sex: str = Field(default='unknown')
    photo_url: Optional[str] = None
    cage_number: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key='category.id')
    father_id: Optional[int] = Field(default=None, foreign_key='bird.id')
    mother_id: Optional[int] = Field(default=None, foreign_key='bird.id')
    status: str = Field(default='in_stock')
    notes: Optional[str] = None

class Bird(BirdBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BirdCreate(BirdBase):
    pass

class BirdUpdate(SQLModel):
    ring_id: Optional[str] = None
    name: Optional[str] = None
    mutation: Optional[str] = None
    sex: Optional[str] = None
    photo_url: Optional[str] = None
    cage_number: Optional[str] = None
    category_id: Optional[int] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class BirdRead(BirdBase):
    id: int
    created_at: datetime
    updated_at: datetime
