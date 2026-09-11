from __future__ import annotations
from sqlmodel import Session, select, func, col
from models.bird import Bird
from models.category import Category
from models.sale import Sale, SaleCreate, SaleUpdate
from models.audit_log import AuditLog
from fastapi import HTTPException
import json
from datetime import datetime


def create_sale(session: Session, sale_data: SaleCreate):
    """Create a sale record and mark the bird as 'sold'."""
    bird = session.get(Bird, sale_data.bird_id)
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    if bird.status != "in_stock":
        raise HTTPException(
            status_code=400,
            detail=f"Bird cannot be sold (current status: '{bird.status}')"
        )

    # Create the sale record
    sale_dict = sale_data.model_dump(exclude_unset=True)
    sale = Sale.model_validate(sale_dict)
    session.add(sale)

    # Audit log for sale creation
    audit_sale = AuditLog(
        table_name="sale",
        record_id=0,  # Will be updated after flush
        action="INSERT",
        old_values=None,
        new_values=json.dumps(sale_dict, default=str),
    )
    session.add(audit_sale)

    # Update bird status to 'sold'
    old_bird_values = bird.model_dump()
    bird.status = "sold"
    bird.updated_at = datetime.utcnow()
    session.add(bird)

    audit_bird = AuditLog(
        table_name="bird",
        record_id=bird.id,
        action="UPDATE",
        old_values=json.dumps(old_bird_values, default=str),
        new_values=json.dumps(bird.model_dump(), default=str),
    )
    session.add(audit_bird)

    session.commit()
    session.refresh(sale)

    # Patch the sale audit log with the real record_id
    audit_sale.record_id = sale.id
    session.add(audit_sale)
    session.commit()

    return sale


def get_all_sales(session: Session, skip: int = 0, limit: int = 100):
    """Return all sales with bird details and pagination."""
    query = select(Sale).order_by(col(Sale.date_sold).desc()).offset(skip).limit(limit)
    sales = session.exec(query).all()
    results = []
    for sale in sales:
        sale_dict = sale.model_dump()
        bird = session.get(Bird, sale.bird_id)
        sale_dict["bird"] = bird.model_dump() if bird else None
        results.append(sale_dict)
    return results


def search_sales(session: Session, query: str):
    """Search sales by bird ring_id, bird name, or buyer_name."""
    pattern = f"%{query}%"
    statement = (
        select(Sale)
        .join(Bird, Sale.bird_id == Bird.id)
        .where(
            (col(Bird.ring_id).ilike(pattern))
            | (col(Bird.name).ilike(pattern))
            | (col(Sale.buyer_name).ilike(pattern))
        )
        .order_by(col(Sale.date_sold).desc())
    )
    sales = session.exec(statement).all()
    results = []
    for sale in sales:
        sale_dict = sale.model_dump()
        bird = session.get(Bird, sale.bird_id)
        sale_dict["bird"] = bird.model_dump() if bird else None
        results.append(sale_dict)
    return results


def update_sale(session: Session, sale_id: int, sale_data: SaleUpdate):
    """Update sale details. Creates an AuditLog entry."""
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    old_values = sale.model_dump()
    new_data = sale_data.model_dump(exclude_unset=True)

    for key, value in new_data.items():
        setattr(sale, key, value)

    session.add(sale)

    audit = AuditLog(
        table_name="sale",
        record_id=sale.id,
        action="UPDATE",
        old_values=json.dumps(old_values, default=str),
        new_values=json.dumps(sale.model_dump(), default=str),
    )
    session.add(audit)

    session.commit()
    session.refresh(sale)
    return sale


def get_sales_analytics(session: Session):
    """Return total_sales, total_revenue, sales_by_month, and sales_by_category."""

    # Total sales count and revenue
    total_sales = session.exec(select(func.count(Sale.id))).one()
    total_revenue = session.exec(select(func.coalesce(func.sum(Sale.sale_price), 0))).one()

    # Sales by month — extract year/month via SQLite strftime

    by_month_stmt = (
        select(
            func.strftime("%Y", Sale.date_sold).label("year"),
            func.strftime("%m", Sale.date_sold).label("month"),
            func.count(Sale.id).label("count"),
            func.coalesce(func.sum(Sale.sale_price), 0).label("revenue"),
        )
        .group_by(
            func.strftime("%Y", Sale.date_sold),
            func.strftime("%m", Sale.date_sold),
        )
        .order_by(
            func.strftime("%Y", Sale.date_sold).desc(),
            func.strftime("%m", Sale.date_sold).desc(),
        )
    )
    rows = session.exec(by_month_stmt).all()
    sales_by_month = [
        {"year": int(r[0]), "month": int(r[1]), "count": r[2], "revenue": float(r[3])}
        for r in rows
    ]

    # Sales by category
    by_cat_stmt = (
        select(
            Category.name.label("category_name"),
            func.count(Sale.id).label("count"),
            func.coalesce(func.sum(Sale.sale_price), 0).label("revenue"),
        )
        .join(Bird, Sale.bird_id == Bird.id)
        .join(Category, Bird.category_id == Category.id)
        .group_by(Category.name)
        .order_by(func.sum(Sale.sale_price).desc())
    )
    cat_rows = session.exec(by_cat_stmt).all()
    sales_by_category = [
        {"category_name": r[0], "count": r[1], "revenue": float(r[2])}
        for r in cat_rows
    ]

    return {
        "total_sales": total_sales,
        "total_revenue": float(total_revenue),
        "sales_by_month": sales_by_month,
        "sales_by_category": sales_by_category,
    }


def delete_sale(session: Session, sale_id: int):
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
        
    bird = session.get(Bird, sale.bird_id)
    if bird:
        old_bird_values = bird.model_dump()
        bird.status = "in_stock"
        session.add(bird)
        
        audit_bird = AuditLog(
            table_name="bird",
            record_id=bird.id,
            action="UPDATE",
            old_values=json.dumps(old_bird_values, default=str),
            new_values=json.dumps(bird.model_dump(), default=str),
        )
        session.add(audit_bird)
        
    session.delete(sale)
    
    audit = AuditLog(
        table_name="sale",
        record_id=sale.id,
        action="DELETE",
        old_values=json.dumps(sale.model_dump(), default=str),
        new_values=None,
    )
    session.add(audit)
    
    session.commit()
    return {"message": "Sale deleted successfully"}
