from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    table_name: str
    record_id: int
    action: str
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
