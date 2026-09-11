from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlmodel import Session
from typing import List, Optional
import os
import shutil

from database import get_session
from models.bird import BirdRead, BirdCreate, BirdUpdate
from services import bird_service, search_service, genealogy_service

router = APIRouter()

@router.get("")
def get_birds(category_id: Optional[int] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return bird_service.get_all_birds(session, category_id, status, skip, limit)

@router.get("/search", response_model=List[BirdRead])
def search_birds(q: str, session: Session = Depends(get_session)):
    return search_service.fuzzy_search_birds(session, q)

@router.get("/stats")
def get_bird_stats(session: Session = Depends(get_session)):
    return bird_service.get_bird_count_by_category(session)

@router.get("/stats/summary")
def get_bird_stats_summary(session: Session = Depends(get_session)):
    return bird_service.get_bird_stats_summary(session)

@router.get("/{bird_id}")
def get_bird(bird_id: int, session: Session = Depends(get_session)):
    return bird_service.get_bird_by_id(session, bird_id)

@router.post("", response_model=BirdRead)
def create_bird(bird: BirdCreate, session: Session = Depends(get_session)):
    return bird_service.create_bird(session, bird)

@router.put("/{bird_id}", response_model=BirdRead)
def update_bird(bird_id: int, bird: BirdUpdate, session: Session = Depends(get_session)):
    return bird_service.update_bird(session, bird_id, bird)

@router.delete("/{bird_id}", response_model=BirdRead)
def delete_bird(bird_id: int, session: Session = Depends(get_session)):
    update = BirdUpdate(status="deceased")
    return bird_service.update_bird(session, bird_id, update)

@router.get("/{bird_id}/siblings", response_model=List[BirdRead])
def get_siblings(bird_id: int, session: Session = Depends(get_session)):
    return bird_service.get_bird_siblings(session, bird_id)

@router.get("/{bird_id}/pairings")
def get_pairings(bird_id: int, session: Session = Depends(get_session)):
    return bird_service.get_bird_pairings(session, bird_id)

@router.get("/{bird_id}/ancestry")
def get_ancestry(bird_id: int, depth: int = Query(default=5, ge=1, le=10), session: Session = Depends(get_session)):
    return genealogy_service.get_ancestors(session, bird_id, max_depth=depth)

@router.get("/{bird_id}/ancestry/tree")
def get_ancestry_tree(bird_id: int, depth: int = Query(default=5, ge=1, le=10), session: Session = Depends(get_session)):
    tree = genealogy_service.get_ancestry_tree(session, bird_id, max_depth=depth)
    if tree is None:
        raise HTTPException(status_code=404, detail="Bird not found")
    return tree

@router.get("/{bird_id}/descendants")
def get_descendants(bird_id: int, depth: int = Query(default=5, ge=1, le=10), session: Session = Depends(get_session)):
    return genealogy_service.get_descendants(session, bird_id, max_depth=depth)

@router.get("/{bird_id}/descendants/tree")
def get_descendants_tree(bird_id: int, depth: int = Query(default=5, ge=1, le=10), session: Session = Depends(get_session)):
    tree = genealogy_service.get_descendants_tree(session, bird_id, max_depth=depth)
    if tree is None:
        raise HTTPException(status_code=404, detail="Bird not found")
    return tree

@router.post("/{bird_id}/photo")
def upload_photo(bird_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    bird = bird_service.get_bird_by_id(session, bird_id)
    upload_dir = "uploads/photos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{bird_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    update = BirdUpdate(photo_url=file_path)
    bird_service.update_bird(session, bird_id, update)
    return {"photo_url": file_path}
