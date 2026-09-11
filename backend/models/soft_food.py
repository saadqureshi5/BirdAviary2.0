from __future__ import annotations
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SoftFoodLogBase(SQLModel):
    year: int
    season: str
    recipe_name: str
    ingredients: str
    supplements: Optional[str] = None
    results: Optional[str] = None

class SoftFoodLog(SoftFoodLogBase, table=True):
    __tablename__ = "soft_food_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SoftFoodLogCreate(SoftFoodLogBase):
    pass

class SoftFoodLogUpdate(SQLModel):
    year: Optional[int] = None
    season: Optional[str] = None
    recipe_name: Optional[str] = None
    ingredients: Optional[str] = None
    supplements: Optional[str] = None
    results: Optional[str] = None

class SoftFoodLogRead(SoftFoodLogBase):
    id: int
    created_at: datetime
