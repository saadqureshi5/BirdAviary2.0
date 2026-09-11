from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from database import get_session
from models.category import Category
from models.bird import Bird

router = APIRouter()

@router.get("")
def get_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    results = []
    for cat in categories:
        count = len(session.exec(select(Bird).where(Bird.category_id == cat.id, Bird.status == 'in_stock')).all())
        results.append({**cat.model_dump(), "bird_count": count})
    return results

@router.post("")
def create_category(category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.put("/{category_id}")
def update_category(category_id: int, category: Category, session: Session = Depends(get_session)):
    db_cat = session.get(Category, category_id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    cat_data = category.model_dump(exclude_unset=True)
    for key, value in cat_data.items():
        setattr(db_cat, key, value)
    
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return db_cat

@router.delete("/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    db_cat = session.get(Category, category_id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    birds = session.exec(select(Bird).where(Bird.category_id == category_id)).all()
    if birds:
        raise HTTPException(status_code=400, detail="Cannot delete category with existing birds")
    
    session.delete(db_cat)
    session.commit()
    return {"ok": True}
