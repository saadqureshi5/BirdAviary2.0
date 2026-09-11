from __future__ import annotations
from sqlmodel import Session, select, or_
from models.bird import Bird
from models.category import Category

def fuzzy_search_birds(session: Session, query: str, limit: int = 20):
    if not query:
        return []
    
    # Create wildcard string like '%q%u%e%r%y%'
    wildcard_query = f"%{'%'.join(list(query))}%"
    
    statement = select(Bird).join(Category, isouter=True).where(
        Bird.status != 'external',
        or_(
            Bird.ring_id.like(wildcard_query),
            Bird.name.like(wildcard_query),
            Bird.mutation.like(wildcard_query),
            Category.name.like(wildcard_query)
        )
    ).limit(limit)
    
    return session.exec(statement).all()
