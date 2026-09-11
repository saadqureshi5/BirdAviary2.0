from __future__ import annotations
from sqlmodel import Session, select
from models.bird import Bird, BirdCreate, BirdUpdate
from models.pairing import Pairing
from models.category import Category
from models.audit_log import AuditLog
from fastapi import HTTPException
import json
from datetime import datetime

def get_all_birds(session: Session, category_id: int | None = None, status: str | None = None, skip: int = 0, limit: int = 100):
    query = select(Bird)
    if category_id:
        query = query.where(Bird.category_id == category_id)
    if status:
        query = query.where(Bird.status == status)
    else:
        query = query.where(Bird.status != 'external')
    query = query.offset(skip).limit(limit)
    birds = session.exec(query).all()
    
    # Include category data for each bird
    results = []
    for bird in birds:
        bird_dict = bird.model_dump()
        if bird.category_id:
            category = session.get(Category, bird.category_id)
            if category:
                bird_dict["category"] = {"id": category.id, "name": category.name, "description": category.description}
        results.append(bird_dict)
    return results

def get_bird_by_id(session: Session, bird_id: int):
    bird = session.get(Bird, bird_id)
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    
    # Build response with related data
    bird_dict = bird.model_dump()
    
    # Include category
    if bird.category_id:
        category = session.get(Category, bird.category_id)
        if category:
            bird_dict["category"] = {"id": category.id, "name": category.name, "description": category.description}
    
    # Include father
    if bird.father_id:
        father = session.get(Bird, bird.father_id)
        if father:
            bird_dict["father"] = father.model_dump()
    
    # Include mother
    if bird.mother_id:
        mother = session.get(Bird, bird.mother_id)
        if mother:
            bird_dict["mother"] = mother.model_dump()
    
    return bird_dict

def create_bird(session: Session, bird_data: BirdCreate):
    if bird_data.ring_id:
        existing = session.exec(select(Bird).where(Bird.ring_id == bird_data.ring_id)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ring ID already exists")
    bird = Bird.model_validate(bird_data)
    session.add(bird)
    session.commit()
    session.refresh(bird)
    
    audit = AuditLog(
        table_name="bird",
        record_id=bird.id,
        action="INSERT",
        old_values=None,
        new_values=json.dumps(bird.model_dump(), default=str)
    )
    session.add(audit)
    session.commit()
    
    return bird

def update_bird(session: Session, bird_id: int, bird_data: BirdUpdate):
    bird = session.get(Bird, bird_id)
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    
    old_values = bird.model_dump()
    new_data = bird_data.model_dump(exclude_unset=True)
    
    for key, value in new_data.items():
        setattr(bird, key, value)
    
    bird.updated_at = datetime.utcnow()
    
    session.add(bird)
    
    audit = AuditLog(
        table_name="bird",
        record_id=bird.id,
        action="UPDATE",
        old_values=json.dumps(old_values, default=str),
        new_values=json.dumps(bird.model_dump(), default=str)
    )
    session.add(audit)
    
    session.commit()
    session.refresh(bird)
    return bird

def get_bird_siblings(session: Session, bird_id: int):
    bird = session.get(Bird, bird_id)
    if not bird or not bird.father_id or not bird.mother_id:
        return []
    query = select(Bird).where(Bird.father_id == bird.father_id, Bird.mother_id == bird.mother_id, Bird.id != bird_id)
    return session.exec(query).all()

def get_bird_pairings(session: Session, bird_id: int):
    query = select(Pairing).where((Pairing.bird_a_id == bird_id) | (Pairing.bird_b_id == bird_id))
    return session.exec(query).all()

def get_bird_count_by_category(session: Session):
    # Basic implementation
    categories = session.exec(select(Category)).all()
    stats = []
    for cat in categories:
        count = len(session.exec(select(Bird).where(Bird.category_id == cat.id, Bird.status != 'external')).all())
        stats.append({"category_id": cat.id, "name": cat.name, "count": count})
    return stats

def get_bird_stats_summary(session: Session):
    all_birds = session.exec(select(Bird)).all()
    in_stock = len([b for b in all_birds if b.status == 'in_stock'])
    sold = len([b for b in all_birds if b.status == 'sold'])
    deceased = len([b for b in all_birds if b.status == 'deceased'])
    total_birds = in_stock + sold + deceased
    active_pairs = len(session.exec(select(Pairing).where(Pairing.end_date == None)).all())
    return {
        "total_birds": total_birds,
        "in_stock": in_stock,
        "sold": sold,
        "deceased": deceased,
        "active_pairs": active_pairs
    }
