from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class ReminderBase(SQLModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    recurrence_pattern: Optional[str] = None
    is_active: bool = Field(default=True)
    notification_sent: bool = Field(default=False)

class Reminder(ReminderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None
    is_active: Optional[bool] = None
    notification_sent: Optional[bool] = None

class ReminderRead(ReminderBase):
    id: int
    created_at: datetime
    updated_at: datetime
