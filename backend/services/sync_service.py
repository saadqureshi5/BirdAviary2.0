from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlmodel import Session, select, func
from models.sync_log import SyncLog
from models.audit_log import AuditLog
import models

def get_pending_entries(session: Session, limit: int = 100):
    statement = select(SyncLog).where(SyncLog.synced == False).order_by(SyncLog.timestamp.asc()).limit(limit)
    entries = session.exec(statement).all()
    return [entry.model_dump() for entry in entries]

def mark_entries_synced(session: Session, entry_ids: list[int]):
    statement = select(SyncLog).where(SyncLog.id.in_(entry_ids))
    entries = session.exec(statement).all()
    for entry in entries:
        entry.synced = True
        session.add(entry)
    session.commit()
    return len(entries)

def replay_entries(session: Session, entries: list[dict]):
    replayed_count = 0
    errors = []
    
    # Dynamically find models
    model_classes = {m.__tablename__: m for name, m in models.__dict__.items() if hasattr(m, '__tablename__')}
    
    for entry in entries:
        try:
            table_name = entry.get("table_name")
            action = entry.get("action")
            payload = entry.get("payload")
            
            if isinstance(payload, str):
                payload = json.loads(payload)
                
            model_class = model_classes.get(table_name)
            if not model_class:
                errors.append(f"Model for table {table_name} not found")
                continue
                
            record_id = entry.get("record_id")
            
            if action == "INSERT":
                new_record = model_class(**payload)
                session.add(new_record)
            elif action == "UPDATE":
                record = session.get(model_class, record_id)
                if record:
                    for k, v in payload.items():
                        setattr(record, k, v)
                    session.add(record)
                else:
                    new_record = model_class(**payload)
                    session.add(new_record)
            elif action == "DELETE":
                record = session.get(model_class, record_id)
                if record:
                    session.delete(record)
                    
            audit = AuditLog(
                table_name=table_name,
                record_id=record_id,
                action=f"REPLAY_{action}",
                new_values=json.dumps(payload),
                timestamp=datetime.now(timezone.utc),
            )
            session.add(audit)
            replayed_count += 1
            
        except Exception as e:
            errors.append(f"Error replaying entry {entry.get('id')}: {str(e)}")
            
    session.commit()
    return {"replayed_count": replayed_count, "errors": errors}

def get_sync_status(session: Session):
    total_statement = select(func.count(SyncLog.id))
    total_entries = session.exec(total_statement).one_or_none() or 0
    
    unsynced_statement = select(func.count(SyncLog.id)).where(SyncLog.synced == False)
    unsynced_count = session.exec(unsynced_statement).one_or_none() or 0
    
    last_sync_statement = select(SyncLog).where(SyncLog.synced == True).order_by(SyncLog.timestamp.desc()).limit(1)
    last_sync_entry = session.exec(last_sync_statement).first()
    last_sync = last_sync_entry.timestamp if last_sync_entry else None
    
    return {
        "total_entries": total_entries,
        "unsynced_count": unsynced_count,
        "last_sync": last_sync
    }

def create_sync_entry(session: Session, device_id: str, table_name: str, record_id: int, action: str, payload: dict | str):
    if isinstance(payload, dict):
        payload = json.dumps(payload)
        
    entry = SyncLog(
        device_id=device_id,
        table_name=table_name,
        record_id=record_id,
        action=action,
        payload=payload,
        timestamp=datetime.now(timezone.utc),
        synced=False
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry
