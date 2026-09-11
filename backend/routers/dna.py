from __future__ import annotations
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session
from database import get_session
from models.dna_record import DNARecordRead
from services import dna_service
from typing import List
import os
import uuid
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads/dna"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("")
def upload_dna_record(
    bird_id: int = Form(...),
    file_type: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if file_type not in ["image", "pdf"]:
        raise HTTPException(status_code=400, detail="file_type must be 'image' or 'pdf'")
    
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Ensure correct format for paths in DB on windows
    file_path = file_path.replace("\\", "/")
    
    return dna_service.upload_dna_record(session, bird_id, file_path, file_type)

@router.get("/search")
def search_dna(q: str = Query(""), category_id: int = Query(None), session: Session = Depends(get_session)):
    return dna_service.search_dna(session, q, category_id)

@router.get("/{dna_id}/file")
def get_dna_file(dna_id: int, session: Session = Depends(get_session)):
    record = dna_service.get_dna_record(session, dna_id)
    if not os.path.exists(record.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(record.file_path)

@router.get("/bird/{bird_id}")
def get_dna_records_for_bird(bird_id: int, session: Session = Depends(get_session)):
    return dna_service.get_dna_records_for_bird(session, bird_id)

@router.delete("/{dna_id}")
def delete_dna_record(dna_id: int, session: Session = Depends(get_session)):
    dna_service.delete_dna_record(session, dna_id)
    return {"message": "DNA record deleted successfully"}
