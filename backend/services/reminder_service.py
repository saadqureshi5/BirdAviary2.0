from __future__ import annotations
from sqlmodel import Session, select
from fastapi import HTTPException
from models.reminder import Reminder, ReminderCreate, ReminderUpdate
from models.audit_log import AuditLog
from datetime import datetime, timedelta

def create_reminder(session: Session, reminder_data: ReminderCreate) -> Reminder:
    import json
    reminder = Reminder.model_validate(reminder_data)
    if reminder.due_date and reminder.due_date.tzinfo:
        reminder.due_date = reminder.due_date.replace(tzinfo=None)
        
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    
    audit = AuditLog(
        table_name="reminder",
        record_id=reminder.id,
        action="INSERT",
        old_values=None,
        new_values=json.dumps(reminder.model_dump(), default=str),
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    
    return reminder

def get_all_reminders(session: Session, active_only: bool = False):
    statement = select(Reminder)
    if active_only:
        statement = statement.where(Reminder.is_active == True)
    return session.exec(statement).all()

def get_reminder(session: Session, reminder_id: int) -> Reminder:
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

def update_reminder(session: Session, reminder_id: int, data: ReminderUpdate) -> Reminder:
    import json
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    old_vals = reminder.model_dump()
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "due_date" and value and value.tzinfo:
            value = value.replace(tzinfo=None)
        setattr(reminder, key, value)
    
    reminder.updated_at = datetime.utcnow()
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    
    audit = AuditLog(
        table_name="reminder",
        record_id=reminder.id,
        action="UPDATE",
        old_values=json.dumps(old_vals, default=str),
        new_values=json.dumps(reminder.model_dump(), default=str),
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    
    return reminder

def delete_reminder(session: Session, reminder_id: int):
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    session.delete(reminder)
    session.commit()
    
    audit = AuditLog(
        table_name="reminder",
        record_id=reminder_id,
        action="DELETE",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()

def get_due_reminders(session: Session):
    tomorrow = datetime.utcnow() + timedelta(days=1)
    statement = select(Reminder).where(
        Reminder.is_active == True,
        Reminder.notification_sent == False,
        Reminder.due_date <= tomorrow
    )
    return session.exec(statement).all()

def mark_notification_sent(session: Session, reminder_id: int) -> Reminder:
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.notification_sent = True
    reminder.updated_at = datetime.utcnow()
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    return reminder
