from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, desc
from typing import List
import json

from database import get_session
from models.audit_log import AuditLog
from models.bird import Bird
from models.category import Category

router = APIRouter()

def _build_activity_item(log: AuditLog, session: Session) -> dict:
    """Convert an AuditLog entry into a human-readable activity item."""
    icon = "update"
    title = f"{log.table_name.title()} Updated"
    description = ""

    new_vals = json.loads(log.new_values) if log.new_values else {}
    old_vals = json.loads(log.old_values) if log.old_values else {}

    if log.table_name == "bird":
        bird_name = new_vals.get("name") or new_vals.get("ring_id") or f"Bird #{log.record_id}"
        if log.action == "INSERT":
            icon = "add"
            title = "New Bird Added"
            cat_name = None
            cat_id = new_vals.get("category_id")
            if cat_id:
                cat = session.get(Category, int(cat_id))
                if cat:
                    cat_name = cat.name
            description = f"{bird_name} added" + (f" to {cat_name}" if cat_name else "")
        elif log.action == "UPDATE":
            # Check if status changed to sold
            old_status = old_vals.get("status")
            new_status = new_vals.get("status")
            if old_status != "sold" and new_status == "sold":
                icon = "sale"
                title = "Bird Sold"
                description = f"{bird_name} was sold"
            elif old_status != "deceased" and new_status == "deceased":
                icon = "remove"
                title = "Bird Removed"
                description = f"{bird_name} marked as deceased"
            else:
                icon = "update"
                title = "Bird Updated"
                description = f"{bird_name} was updated"
    elif log.table_name == "sale":
        if log.action == "INSERT":
            icon = "sale"
            title = "Sale Recorded"
            bird_id = new_vals.get("bird_id")
            buyer = new_vals.get("buyer_name", "Unknown")
            price = new_vals.get("sale_price", 0)
            bird_name = f"Bird #{bird_id}"
            if bird_id:
                bird = session.get(Bird, int(bird_id))
                if bird:
                    bird_name = bird.name or bird.ring_id or bird_name
            description = f"{bird_name} sold to {buyer} for ${price}"
        else:
            icon = "sale"
            title = "Sale Updated"
            description = f"Sale #{log.record_id} was updated"
    elif log.table_name == "pairing":
        icon = "pair"
        if log.action == "INSERT":
            title = "New Pair Created"
        else:
            title = "Pair Updated"
        description = f"Pairing #{log.record_id}"
    elif log.table_name == "clutch":
        icon = "egg"
        if log.action == "INSERT":
            title = "New Clutch"
            eggs = new_vals.get("total_eggs", 0)
            description = f"{eggs} egg{'s' if eggs != 1 else ''} laid"
        else:
            title = "Clutch Updated"
            description = f"Clutch #{log.record_id} updated"
    elif log.table_name == "chick":
        icon = "chick"
        if log.action == "INSERT":
            title = "Chick Hatched"
            description = f"New chick in clutch #{new_vals.get('clutch_id', '?')}"
        else:
            title = "Chick Updated"
            description = f"Chick #{log.record_id} updated"
    elif log.table_name == "dna_record":
        icon = "dna"
        if log.action == "INSERT":
            title = "DNA Record Added"
        else:
            title = "DNA Record Updated"
        bird_id = new_vals.get("bird_id")
        if bird_id:
            bird = session.get(Bird, int(bird_id))
            if bird:
                description = f"DNA for {bird.name or bird.ring_id or f'Bird #{bird_id}'}"
        if not description:
            description = f"DNA record #{log.record_id}"
    elif log.table_name == "reminder":
        icon = "reminder"
        title = "Reminder" + (" Created" if log.action == "INSERT" else " Updated")
        description = new_vals.get("title", f"Reminder #{log.record_id}")
    elif log.table_name == "expense":
        icon = "expense"
        title = "Expense" + (" Added" if log.action == "INSERT" else " Updated")
        amt = new_vals.get("amount", 0)
        desc_text = new_vals.get("description", "")
        description = f"${amt}" + (f" - {desc_text}" if desc_text else "")
    elif log.table_name == "soft_food_log":
        icon = "food"
        title = "Soft Food" + (" Logged" if log.action == "INSERT" else " Updated")
        description = new_vals.get("recipe_name", f"Log #{log.record_id}")
    else:
        description = f"{log.table_name} #{log.record_id} {log.action.lower()}"

    return {
        "id": log.id,
        "icon": icon,
        "title": title,
        "description": description,
        "timestamp": log.timestamp.isoformat(),
        "table_name": log.table_name,
        "action": log.action,
    }


@router.get("")
def get_recent_activity(limit: int = Query(default=10, ge=1, le=50), session: Session = Depends(get_session)):
    logs = session.exec(
        select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
    ).all()
    return [_build_activity_item(log, session) for log in logs]
