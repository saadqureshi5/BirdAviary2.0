from __future__ import annotations
from sqlmodel import Session, select
from fastapi import HTTPException
from models.soft_food import SoftFoodLog, SoftFoodLogCreate, SoftFoodLogUpdate
from models.audit_log import AuditLog
from datetime import datetime

def create_soft_food_log(session: Session, data: SoftFoodLogCreate) -> SoftFoodLog:
    log = SoftFoodLog.model_validate(data)
    session.add(log)
    session.commit()
    session.refresh(log)
    
    audit = AuditLog(
        table_name="soft_food_log",
        record_id=log.id,
        action="INSERT",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    
    return log

def get_all_soft_food_logs(session: Session, year: int | None = None, season: str | None = None) -> list[SoftFoodLog]:
    query = select(SoftFoodLog)
    if year is not None:
        query = query.where(SoftFoodLog.year == year)
    if season is not None:
        query = query.where(SoftFoodLog.season == season)
    return session.exec(query).all()

def get_soft_food_log(session: Session, id: int) -> SoftFoodLog:
    log = session.get(SoftFoodLog, id)
    if not log:
        raise HTTPException(status_code=404, detail="Soft food log not found")
    return log

def update_soft_food_log(session: Session, id: int, data: SoftFoodLogUpdate) -> SoftFoodLog:
    log = get_soft_food_log(session, id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(log, key, value)
    
    session.add(log)
    session.commit()
    session.refresh(log)
    
    audit = AuditLog(
        table_name="soft_food_log",
        record_id=log.id,
        action="UPDATE",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    
    return log

def delete_soft_food_log(session: Session, id: int):
    log = get_soft_food_log(session, id)
    session.delete(log)
    session.commit()
    
    audit = AuditLog(
        table_name="soft_food_log",
        record_id=id,
        action="DELETE",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
