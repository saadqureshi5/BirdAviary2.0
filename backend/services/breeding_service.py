from __future__ import annotations
from sqlmodel import Session, select, func
from fastapi import HTTPException
from models.pairing import Pairing, PairingCreate, PairingUpdate
from models.clutch import Clutch, ClutchCreate, ClutchUpdate
from models.chick import Chick, ChickCreate, ChickUpdate
from models.bird import Bird
from typing import List, Dict, Any

# PAIRING FUNCTIONS
def get_all_pairings(session: Session, skip: int = 0, limit: int = 100):
    pairings = session.exec(select(Pairing).offset(skip).limit(limit)).all()
    results = []
    for p in pairings:
        bird_a = session.get(Bird, p.bird_a_id)
        bird_b = session.get(Bird, p.bird_b_id)
        
        clutches = session.exec(select(Clutch).where(Clutch.pairing_id == p.id)).all()
        total_eggs = sum(c.total_eggs for c in clutches)
        
        total_chicks = 0
        chicks_fledged = 0
        chicks_added_to_stock = 0
        
        for c in clutches:
            chicks = session.exec(select(Chick).where(Chick.clutch_id == c.id)).all()
            total_chicks += len(chicks)
            chicks_fledged += sum(1 for ch in chicks if ch.status in ['fledged', 'added_to_stock'])
            chicks_added_to_stock += sum(1 for ch in chicks if ch.status == 'added_to_stock')
            
        # Flatten: spread pairing fields + bird objects + stats at root level
        results.append({
            **p.model_dump(),
            "bird_a": bird_a.model_dump() if bird_a else None,
            "bird_b": bird_b.model_dump() if bird_b else None,
            "total_clutches": len(clutches),
            "total_eggs": total_eggs,
            "total_chicks": total_chicks,
            "chicks_fledged": chicks_fledged,
            "chicks_added_to_stock": chicks_added_to_stock,
        })
    return results

def get_pairing_by_id(session: Session, pairing_id: int):
    p = session.get(Pairing, pairing_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pairing not found")
    
    bird_a = session.get(Bird, p.bird_a_id)
    bird_b = session.get(Bird, p.bird_b_id)
    
    clutches = session.exec(select(Clutch).where(Clutch.pairing_id == p.id)).all()
    clutch_data = []
    for c in clutches:
        chicks = session.exec(select(Chick).where(Chick.clutch_id == c.id)).all()
        # Flatten: spread clutch fields + chicks array at root level
        clutch_data.append({
            **c.model_dump(),
            "chicks": [ch.model_dump() for ch in chicks]
        })
        
    # Flatten: spread pairing fields + bird objects + clutches at root level
    return {
        **p.model_dump(),
        "bird_a": bird_a.model_dump() if bird_a else None,
        "bird_b": bird_b.model_dump() if bird_b else None,
        "clutches": clutch_data
    }

def create_pairing(session: Session, data: PairingCreate):
    bird_a = session.get(Bird, data.bird_a_id)
    bird_b = session.get(Bird, data.bird_b_id)
    
    if not bird_a or not bird_b:
        raise HTTPException(status_code=404, detail="One or both birds not found")
    if bird_a.status != "in_stock" or bird_b.status != "in_stock":
        raise HTTPException(status_code=400, detail="Both birds must be in_stock")
        
    db_pairing = Pairing.model_validate(data)
    session.add(db_pairing)
    session.commit()
    session.refresh(db_pairing)
    return db_pairing

def update_pairing(session: Session, pairing_id: int, data: PairingUpdate):
    db_pairing = session.get(Pairing, pairing_id)
    if not db_pairing:
        raise HTTPException(status_code=404, detail="Pairing not found")
        
    update_data = data.model_dump(exclude_unset=True)
    if "end_date" in data.model_fields_set:
        update_data["end_date"] = data.end_date
    
    for key, value in update_data.items():
        setattr(db_pairing, key, value)
        
    session.add(db_pairing)
    session.commit()
    session.refresh(db_pairing)
    return db_pairing

# CLUTCH FUNCTIONS
def create_clutch(session: Session, pairing_id: int, data: ClutchCreate):
    pairing = session.get(Pairing, pairing_id)
    if not pairing:
        raise HTTPException(status_code=404, detail="Pairing not found")
    
    # Set pairing_id from URL path param
    data.pairing_id = pairing_id
        
    db_clutch = Clutch.model_validate(data)
    session.add(db_clutch)
    session.commit()
    session.refresh(db_clutch)
    return db_clutch

def update_clutch(session: Session, clutch_id: int, data: ClutchUpdate):
    db_clutch = session.get(Clutch, clutch_id)
    if not db_clutch:
        raise HTTPException(status_code=404, detail="Clutch not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_clutch, key, value)
        
    session.add(db_clutch)
    session.commit()
    session.refresh(db_clutch)
    return db_clutch

# CHICK FUNCTIONS
def create_chick(session: Session, clutch_id: int, data: ChickCreate):
    clutch = session.get(Clutch, clutch_id)
    if not clutch:
        raise HTTPException(status_code=404, detail="Clutch not found")
    
    # Set clutch_id from URL path param
    data.clutch_id = clutch_id
        
    db_chick = Chick.model_validate(data)
    session.add(db_chick)
    session.commit()
    session.refresh(db_chick)
    return db_chick

def update_chick(session: Session, chick_id: int, data: ChickUpdate):
    db_chick = session.get(Chick, chick_id)
    if not db_chick:
        raise HTTPException(status_code=404, detail="Chick not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_chick, key, value)
        
    session.add(db_chick)
    session.commit()
    session.refresh(db_chick)
    return db_chick

# PROMOTION FUNCTION
def promote_chick_to_stock(session: Session, chick_id: int):
    chick = session.get(Chick, chick_id)
    if not chick:
        raise HTTPException(status_code=404, detail="Chick not found")
    if chick.status not in ['hatched', 'fledged']:
        raise HTTPException(status_code=400, detail="Chick status must be hatched or fledged to be promoted")
        
    clutch = session.get(Clutch, chick.clutch_id)
    if not clutch:
        raise HTTPException(status_code=404, detail="Clutch not found")
        
    pairing = session.get(Pairing, clutch.pairing_id)
    if not pairing:
        raise HTTPException(status_code=404, detail="Pairing not found")
        
    bird_a = session.get(Bird, pairing.bird_a_id)
    bird_b = session.get(Bird, pairing.bird_b_id)
    
    father_id = None
    mother_id = None
    category_id = None
    
    if bird_a and bird_a.sex == 'male':
        father_id = bird_a.id
    elif bird_b and bird_b.sex == 'male':
        father_id = bird_b.id
        
    if bird_a and bird_a.sex == 'female':
        mother_id = bird_a.id
    elif bird_b and bird_b.sex == 'female':
        mother_id = bird_b.id
        
    if bird_a:
        category_id = bird_a.category_id
    elif bird_b:
        category_id = bird_b.category_id
        
    new_bird = Bird(
        ring_id=chick.ring_id,
        name=None,
        mutation=chick.mutation,
        sex=chick.sex,
        father_id=father_id,
        mother_id=mother_id,
        status='in_stock',
        category_id=category_id
    )
    
    session.add(new_bird)
    session.commit()
    session.refresh(new_bird)
    
    chick.status = 'added_to_stock'
    chick.promoted_bird_id = new_bird.id
    session.add(chick)
    session.commit()
    session.refresh(chick)
    
    return new_bird

# ANALYTICS FUNCTION
def get_breeding_analytics(session: Session, category_id: int | None = None):
    pairings = session.exec(select(Pairing)).all()
    
    total_pairings = 0
    total_clutches = 0
    total_eggs = 0
    total_chicks_hatched = 0
    total_chicks_fledged = 0
    total_promoted_to_stock = 0
    total_deceased = 0
    
    pair_stats = []
    
    for p in pairings:
        bird_a = session.get(Bird, p.bird_a_id)
        bird_b = session.get(Bird, p.bird_b_id)
        
        # If category_id is provided, check if either bird belongs to it
        if category_id is not None:
            a_cat = bird_a.category_id if bird_a else None
            b_cat = bird_b.category_id if bird_b else None
            if a_cat != category_id and b_cat != category_id:
                continue
                
        if p.end_date is None:
            total_pairings += 1
            
        clutches = session.exec(select(Clutch).where(Clutch.pairing_id == p.id)).all()
        total_clutches += len(clutches)
        
        total_pair_eggs = sum(c.total_eggs for c in clutches)
        total_eggs += total_pair_eggs
        
        total_pair_chicks = 0
        fledged_promoted_count = 0
        
        for c in clutches:
            chicks = session.exec(select(Chick).where(Chick.clutch_id == c.id)).all()
            total_pair_chicks += len(chicks)
            total_chicks_hatched += len(chicks)
            
            for ch in chicks:
                if ch.status in ['fledged', 'added_to_stock']:
                    fledged_promoted_count += 1
                    total_chicks_fledged += 1
                if ch.status == 'added_to_stock':
                    total_promoted_to_stock += 1
                if ch.status == 'deceased':
                    total_deceased += 1
            
        pair_stats.append({
            **p.model_dump(),
            "bird_a": bird_a.model_dump() if bird_a else None,
            "bird_b": bird_b.model_dump() if bird_b else None,
            "total_clutches": len(clutches),
            "total_eggs": total_pair_eggs,
            "total_chicks": total_pair_chicks,
            "chicks_fledged": fledged_promoted_count,
        })
        
    best_pairs = sorted(pair_stats, key=lambda x: x["chicks_fledged"], reverse=True)[:5]
    
    return {
        "total_pairings": total_pairings,
        "total_clutches": total_clutches,
        "total_eggs": total_eggs,
        "total_chicks_hatched": total_chicks_hatched,
        "total_chicks_fledged": total_chicks_fledged,
        "total_promoted_to_stock": total_promoted_to_stock,
        "total_deceased": total_deceased,
        "best_pairs": best_pairs
    }
