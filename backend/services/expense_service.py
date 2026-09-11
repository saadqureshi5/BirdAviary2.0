from __future__ import annotations
from sqlmodel import Session, select
from fastapi import HTTPException
from models.expense import Expense, ExpenseCreate, ExpenseUpdate
from models.audit_log import AuditLog
from datetime import datetime

def create_expense(session: Session, data: ExpenseCreate) -> Expense:
    expense = Expense.model_validate(data)
    session.add(expense)
    session.commit()
    session.refresh(expense)
    
    audit = AuditLog(
        table_name="expense",
        record_id=expense.id,
        action="INSERT",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    
    return expense

def get_all_expenses(session: Session, year: int | None = None, month: int | None = None) -> list[Expense]:
    query = select(Expense)
    if year is not None:
        query = query.where(Expense.year == year)
    if month is not None:
        query = query.where(Expense.month == month)
    return session.exec(query).all()

def get_expense(session: Session, id: int) -> Expense:
    expense = session.get(Expense, id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

def update_expense(session: Session, id: int, data: ExpenseUpdate) -> Expense:
    expense = get_expense(session, id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)
    expense.updated_at = datetime.utcnow()
    
    session.add(expense)
    session.commit()
    session.refresh(expense)
    
    audit = AuditLog(
        table_name="expense",
        record_id=expense.id,
        action="UPDATE",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    
    return expense

def delete_expense(session: Session, id: int):
    expense = get_expense(session, id)
    session.delete(expense)
    session.commit()
    
    audit = AuditLog(
        table_name="expense",
        record_id=id,
        action="DELETE",
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()

def get_expense_analytics(session: Session) -> dict:
    expenses = session.exec(select(Expense)).all()
    
    total = sum(e.amount for e in expenses)
    
    monthly = {}
    yearly = {}
    
    for e in expenses:
        month_key = f"{e.year}-{e.month:02d}"
        monthly[month_key] = monthly.get(month_key, 0) + e.amount
        
        yearly[e.year] = yearly.get(e.year, 0) + e.amount
        
    monthly_totals = [{"year": int(k.split('-')[0]), "month": int(k.split('-')[1]), "total": v} for k, v in monthly.items()]
    yearly_totals = [{"year": k, "total": v} for k, v in yearly.items()]
    
    return {
        "total_expenses": total,
        "monthly_totals": monthly_totals,
        "yearly_totals": yearly_totals
    }
