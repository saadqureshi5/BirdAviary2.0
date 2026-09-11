from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from database import get_session
from models.sale import SaleRead, SaleCreate, SaleUpdate
from services import sale_service

router = APIRouter()


@router.post("", response_model=SaleRead)
def create_sale(sale: SaleCreate, session: Session = Depends(get_session)):
    return sale_service.create_sale(session, sale)


@router.get("")
def get_sales(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return sale_service.get_all_sales(session, skip, limit)


@router.get("/search")
def search_sales(q: str = Query(..., min_length=1), session: Session = Depends(get_session)):
    return sale_service.search_sales(session, q)


@router.get("/analytics")
def get_sales_analytics(session: Session = Depends(get_session)):
    return sale_service.get_sales_analytics(session)


@router.put("/{sale_id}", response_model=SaleRead)
def update_sale(sale_id: int, sale: SaleUpdate, session: Session = Depends(get_session)):
    return sale_service.update_sale(session, sale_id, sale)


@router.delete("/{sale_id}")
def delete_sale(sale_id: int, session: Session = Depends(get_session)):
    return sale_service.delete_sale(session, sale_id)
