from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class SyncLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str
    table_name: str
    record_id: int
    action: str
    payload: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    synced: bool = Field(default=False)
