from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from models.reminder import ReminderRead, ReminderCreate, ReminderUpdate
from services import reminder_service
from typing import List

router = APIRouter()

@router.post("", response_model=ReminderRead)
def create_reminder(reminder: ReminderCreate, session: Session = Depends(get_session)):
    return reminder_service.create_reminder(session, reminder)

@router.get("", response_model=List[ReminderRead])
def list_reminders(active_only: bool = False, session: Session = Depends(get_session)):
    return reminder_service.get_all_reminders(session, active_only)

@router.get("/due", response_model=List[ReminderRead])
def get_due_reminders(session: Session = Depends(get_session)):
    return reminder_service.get_due_reminders(session)

@router.get("/{reminder_id}", response_model=ReminderRead)
def get_reminder(reminder_id: int, session: Session = Depends(get_session)):
    return reminder_service.get_reminder(session, reminder_id)

@router.put("/{reminder_id}", response_model=ReminderRead)
def update_reminder(reminder_id: int, reminder: ReminderUpdate, session: Session = Depends(get_session)):
    return reminder_service.update_reminder(session, reminder_id, reminder)

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, session: Session = Depends(get_session)):
    reminder_service.delete_reminder(session, reminder_id)
    return {"message": "Reminder deleted successfully"}

@router.post("/{reminder_id}/mark-sent", response_model=ReminderRead)
def mark_notification_sent(reminder_id: int, session: Session = Depends(get_session)):
    return reminder_service.mark_notification_sent(session, reminder_id)
