from __future__ import annotations
from sqlmodel import Session, select, col, or_
from fastapi import HTTPException
from models.dna_record import DNARecord
from models.bird import Bird
from models.audit_log import AuditLog
from datetime import datetime
import os

def upload_dna_record(session: Session, bird_id: int, file_path: str, file_type: str) -> DNARecord:
    bird = session.get(Bird, bird_id)
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    
    record = DNARecord(bird_id=bird_id, file_path=file_path, file_type=file_type)
    session.add(record)
    session.commit()
    session.refresh(record)
    
    audit = AuditLog(
        table_name="dna_record",
        record_id=record.id,
        action="INSERT",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    
    record_dict = record.model_dump()
    record_dict["bird"] = bird.model_dump()
    
    return record_dict

def get_dna_records_for_bird(session: Session, bird_id: int):
    statement = select(DNARecord, Bird).join(Bird, DNARecord.bird_id == Bird.id).where(DNARecord.bird_id == bird_id)
    results = session.exec(statement).all()
    
    response = []
    for record, b in results:
        record_dict = record.model_dump()
        record_dict["bird"] = b.model_dump()
        response.append(record_dict)
        
    return response

def search_dna(session: Session, query: str = "", category_id: int = None):
    statement = select(DNARecord, Bird).join(Bird, DNARecord.bird_id == Bird.id)
    
    if query:
        pattern = f"%{query}%"
        statement = statement.where(
            or_(
                Bird.ring_id.ilike(pattern),
                Bird.name.ilike(pattern),
                Bird.mutation.ilike(pattern)
            )
        )
        
    if category_id is not None:
        statement = statement.where(Bird.category_id == category_id)
        
    results = session.exec(statement).all()
    
    response = []
    for record, b in results:
        record_dict = record.model_dump()
        record_dict["bird"] = b.model_dump()
        response.append(record_dict)
        
    return response

def get_dna_record(session: Session, dna_id: int) -> DNARecord:
    record = session.get(DNARecord, dna_id)
    if not record:
        raise HTTPException(status_code=404, detail="DNA record not found")
    return record

def delete_dna_record(session: Session, dna_id: int):
    record = session.get(DNARecord, dna_id)
    if not record:
        raise HTTPException(status_code=404, detail="DNA record not found")
    
    try:
        if os.path.exists(record.file_path):
            os.remove(record.file_path)
    except Exception:
        pass # Handle or log if needed
        
    session.delete(record)
    session.commit()
    
    audit = AuditLog(
        table_name="dna_record",
        record_id=dna_id,
        action="DELETE",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
