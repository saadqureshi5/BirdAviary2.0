import os

base_dir = r"c:\Users\saadq\Desktop\BirdAviary2.0\backend"

dirs = [
    "models",
    "routers",
    "services",
    "migrations"
]

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

files = {}

files["pyproject.toml"] = """[project]
name = "bird-aviary-backend"
version = "0.1.0"
description = "FastAPI backend for Bird Aviary Management"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "sqlmodel",
    "pydantic",
    "python-multipart",
    "aiofiles"
]
"""

files["main.py"] = """from __future__ import annotations
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import birds, categories
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Bird Aviary API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(birds.router, prefix="/api/birds", tags=["birds"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8008, help="Port to run the server on")
    args = parser.parse_args()
    uvicorn.run("backend.main:app", host="0.0.0.0", port=args.port, reload=True)
"""

files["database.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
import os

sqlite_file_name = "aviary.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
"""

files["models/__init__.py"] = """from __future__ import annotations
from .category import Category
from .bird import Bird, BirdRead, BirdCreate, BirdUpdate
from .pairing import Pairing
from .clutch import Clutch
from .chick import Chick
from .sale import Sale
from .dna_record import DNARecord
from .reminder import Reminder
from .soft_food import SoftFoodLog
from .expense import Expense
from .sync_log import SyncLog
from .audit_log import AuditLog
"""

files["models/category.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
"""

files["models/bird.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class BirdBase(SQLModel):
    ring_id: Optional[str] = Field(default=None, unique=True, index=True)
    name: Optional[str] = Field(default=None, index=True)
    mutation: Optional[str] = None
    sex: str = Field(default='unknown')
    photo_url: Optional[str] = None
    cage_number: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key='category.id')
    father_id: Optional[int] = Field(default=None, foreign_key='bird.id')
    mother_id: Optional[int] = Field(default=None, foreign_key='bird.id')
    status: str = Field(default='in_stock')
    notes: Optional[str] = None

class Bird(BirdBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BirdCreate(BirdBase):
    pass

class BirdUpdate(SQLModel):
    ring_id: Optional[str] = None
    name: Optional[str] = None
    mutation: Optional[str] = None
    sex: Optional[str] = None
    photo_url: Optional[str] = None
    cage_number: Optional[str] = None
    category_id: Optional[int] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class BirdRead(BirdBase):
    id: int
    created_at: datetime
    updated_at: datetime
"""

files["models/pairing.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Pairing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bird_a_id: int = Field(foreign_key='bird.id')
    bird_b_id: int = Field(foreign_key='bird.id')
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    cage_number: Optional[str] = None
"""

files["models/clutch.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Clutch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pairing_id: int = Field(foreign_key='pairing.id')
    clutch_date: datetime = Field(default_factory=datetime.utcnow)
    total_eggs: int = Field(default=0)
    fertile_eggs: int = Field(default=0)
    eggs_lost: int = Field(default=0)
    loss_reason: Optional[str] = None
"""

files["models/chick.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Chick(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    clutch_id: int = Field(foreign_key='clutch.id')
    ring_id: Optional[str] = None
    mutation: Optional[str] = None
    status: str = Field(default='hatched') # hatched, fledged, deceased, added_to_stock
    mortality_reason: Optional[str] = None
    promoted_bird_id: Optional[int] = Field(default=None, foreign_key='bird.id')
    hatch_date: Optional[datetime] = None
    fledge_date: Optional[datetime] = None
"""

files["models/sale.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Sale(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bird_id: int = Field(foreign_key='bird.id')
    date_sold: datetime = Field(default_factory=datetime.utcnow)
    sale_price: float = Field(default=0.0)
    buyer_name: Optional[str] = None
"""

files["models/dna_record.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from typing import Optional

class DNARecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bird_id: int = Field(foreign_key='bird.id')
    file_path: str
    file_type: str # image/pdf
"""

files["models/reminder.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    due_date: datetime
    recurrence_pattern: Optional[str] = None
    is_active: bool = Field(default=True)
    notification_sent: bool = Field(default=False)
"""

files["models/soft_food.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from typing import Optional

class SoftFoodLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    season: str
    recipe_name: str
    ingredients: str
    supplements: Optional[str] = None
    results: Optional[str] = None
"""

files["models/expense.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import date
from typing import Optional

class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    month: int
    date: date
    description: str
    amount: float
"""

files["models/sync_log.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class SyncLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str
    table_name: str
    record_id: int
    action: str
    payload: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    synced: bool = Field(default=False)
"""

files["models/audit_log.py"] = """from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    table_name: str
    record_id: int
    action: str
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
"""

files["services/__init__.py"] = """"""

files["services/bird_service.py"] = """from __future__ import annotations
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
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()

def get_bird_by_id(session: Session, bird_id: int):
    bird = session.get(Bird, bird_id)
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    # Fetch category name and parents if needed
    return bird

def create_bird(session: Session, bird_data: BirdCreate):
    if bird_data.ring_id:
        existing = session.exec(select(Bird).where(Bird.ring_id == bird_data.ring_id)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ring ID already exists")
    bird = Bird.model_validate(bird_data)
    session.add(bird)
    session.commit()
    session.refresh(bird)
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
        count = len(session.exec(select(Bird).where(Bird.category_id == cat.id)).all())
        stats.append({"category_id": cat.id, "name": cat.name, "count": count})
    return stats
"""

files["services/search_service.py"] = """from __future__ import annotations
from sqlmodel import Session, select, or_
from models.bird import Bird
from models.category import Category

def fuzzy_search_birds(session: Session, query: str, limit: int = 20):
    if not query:
        return []
    
    # Create wildcard string like '%q%u%e%r%y%'
    wildcard_query = f"%{'%'.join(list(query))}%"
    
    statement = select(Bird).join(Category, isouter=True).where(
        or_(
            Bird.ring_id.like(wildcard_query),
            Bird.name.like(wildcard_query),
            Category.name.like(wildcard_query)
        )
    ).limit(limit)
    
    return session.exec(statement).all()
"""

files["services/genealogy_service.py"] = """from __future__ import annotations
from sqlmodel import Session
from sqlalchemy import text
from typing import List, Dict

def get_ancestors(session: Session, bird_id: int, max_depth: int = 5):
    sql = f\"\"\"
    WITH RECURSIVE ancestors AS (
        SELECT id, name, ring_id, father_id, mother_id, 0 as depth
        FROM bird
        WHERE id = :bird_id
        
        UNION ALL
        
        SELECT b.id, b.name, b.ring_id, b.father_id, b.mother_id, a.depth + 1
        FROM bird b
        JOIN ancestors a ON b.id = a.father_id OR b.id = a.mother_id
        WHERE a.depth < :max_depth
    )
    SELECT * FROM ancestors WHERE id != :bird_id;
    \"\"\"
    result = session.exec(text(sql), params={"bird_id": bird_id, "max_depth": max_depth}).mappings().all()
    return [dict(row) for row in result]

def get_descendants(session: Session, bird_id: int, max_depth: int = 5):
    sql = f\"\"\"
    WITH RECURSIVE descendants AS (
        SELECT id, name, ring_id, father_id, mother_id, 0 as depth
        FROM bird
        WHERE id = :bird_id
        
        UNION ALL
        
        SELECT b.id, b.name, b.ring_id, b.father_id, b.mother_id, d.depth + 1
        FROM bird b
        JOIN descendants d ON b.father_id = d.id OR b.mother_id = d.id
        WHERE d.depth < :max_depth
    )
    SELECT * FROM descendants WHERE id != :bird_id;
    \"\"\"
    result = session.exec(text(sql), params={"bird_id": bird_id, "max_depth": max_depth}).mappings().all()
    return [dict(row) for row in result]
"""

files["routers/__init__.py"] = """"""

files["routers/birds.py"] = """from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from typing import List, Optional
import os
import shutil

from database import get_session
from models.bird import BirdRead, BirdCreate, BirdUpdate
from services import bird_service, search_service, genealogy_service

router = APIRouter()

@router.get("", response_model=List[BirdRead])
def get_birds(category_id: Optional[int] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return bird_service.get_all_birds(session, category_id, status, skip, limit)

@router.get("/search", response_model=List[BirdRead])
def search_birds(q: str, session: Session = Depends(get_session)):
    return search_service.fuzzy_search_birds(session, q)

@router.get("/stats")
def get_bird_stats(session: Session = Depends(get_session)):
    return bird_service.get_bird_count_by_category(session)

@router.get("/{bird_id}", response_model=BirdRead)
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
def get_ancestry(bird_id: int, session: Session = Depends(get_session)):
    return genealogy_service.get_ancestors(session, bird_id)

@router.get("/{bird_id}/descendants")
def get_descendants(bird_id: int, session: Session = Depends(get_session)):
    return genealogy_service.get_descendants(session, bird_id)

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
"""

files["routers/categories.py"] = """from __future__ import annotations
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
        count = len(session.exec(select(Bird).where(Bird.category_id == cat.id)).all())
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
"""

files["migrations/init_schema.sql"] = """-- This serves as reference since SQLModel creates tables automatically
-- Refer to Python models for the exact schema
"""

for fname, content in files.items():
    path = os.path.join(base_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Files created successfully.")
