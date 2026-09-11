from __future__ import annotations
from sqlmodel import Session
from sqlalchemy import text
from typing import List, Dict, Optional, Any


def get_ancestors(session: Session, bird_id: int, max_depth: int = 5) -> List[Dict]:
    """Returns a flat list of all ancestors up to max_depth generations."""
    sql = """
    WITH RECURSIVE ancestors AS (
        SELECT id, name, ring_id, mutation, sex, photo_url, father_id, mother_id, 0 as depth
        FROM bird
        WHERE id = :bird_id

        UNION ALL

        SELECT b.id, b.name, b.ring_id, b.mutation, b.sex, b.photo_url, b.father_id, b.mother_id, a.depth + 1
        FROM bird b
        JOIN ancestors a ON b.id = a.father_id OR b.id = a.mother_id
        WHERE a.depth < :max_depth
    )
    SELECT * FROM ancestors WHERE id != :bird_id;
    """
    result = session.exec(
        text(sql), params={"bird_id": bird_id, "max_depth": max_depth}
    ).mappings().all()
    return [dict(row) for row in result]


def get_descendants(session: Session, bird_id: int, max_depth: int = 5) -> List[Dict]:
    """Returns a flat list of all descendants up to max_depth generations."""
    sql = """
    WITH RECURSIVE descendants AS (
        SELECT id, name, ring_id, mutation, sex, photo_url, father_id, mother_id, 0 as depth
        FROM bird
        WHERE id = :bird_id

        UNION ALL

        SELECT b.id, b.name, b.ring_id, b.mutation, b.sex, b.photo_url, b.father_id, b.mother_id, d.depth + 1
        FROM bird b
        JOIN descendants d ON b.father_id = d.id OR b.mother_id = d.id
        WHERE d.depth < :max_depth
    )
    SELECT * FROM descendants WHERE id != :bird_id;
    """
    result = session.exec(
        text(sql), params={"bird_id": bird_id, "max_depth": max_depth}
    ).mappings().all()
    return [dict(row) for row in result]


def get_ancestry_tree(session: Session, bird_id: int, max_depth: int = 5) -> Optional[Dict[str, Any]]:
    """Returns a nested tree structure for pedigree visualization.

    Response shape:
    {
        id, ring_id, name, mutation, sex, photo_url,
        father: { ...same shape... } | null,
        mother: { ...same shape... } | null,
    }
    """
    # Fetch the root bird and all ancestors in a single recursive query
    sql = """
    WITH RECURSIVE ancestors AS (
        SELECT id, name, ring_id, mutation, sex, photo_url, father_id, mother_id, 0 as depth
        FROM bird
        WHERE id = :bird_id

        UNION ALL

        SELECT b.id, b.name, b.ring_id, b.mutation, b.sex, b.photo_url, b.father_id, b.mother_id, a.depth + 1
        FROM bird b
        JOIN ancestors a ON b.id = a.father_id OR b.id = a.mother_id
        WHERE a.depth < :max_depth
    )
    SELECT DISTINCT id, name, ring_id, mutation, sex, photo_url, father_id, mother_id
    FROM ancestors;
    """
    result = session.exec(
        text(sql), params={"bird_id": bird_id, "max_depth": max_depth}
    ).mappings().all()

    if not result:
        return None

    # Build a lookup map keyed by bird id
    birds_map: Dict[int, Dict] = {}
    for row in result:
        birds_map[row["id"]] = dict(row)

    # Recursively construct the nested tree from the flat lookup
    def build_node(bid: Optional[int], current_depth: int = 0) -> Optional[Dict[str, Any]]:
        if bid is None or bid not in birds_map or current_depth > max_depth:
            return None
        bird = birds_map[bid]
        return {
            "id": bird["id"],
            "ring_id": bird["ring_id"],
            "name": bird["name"],
            "mutation": bird["mutation"],
            "sex": bird["sex"],
            "photo_url": bird["photo_url"],
            "father": build_node(bird["father_id"], current_depth + 1),
            "mother": build_node(bird["mother_id"], current_depth + 1),
        }

    return build_node(bird_id)


def get_descendants_tree(session: Session, bird_id: int, max_depth: int = 5) -> Optional[Dict[str, Any]]:
    """Returns a nested tree structure of descendants, grouped by partner.

    Response shape:
    {
        id, ring_id, name, mutation, sex, photo_url,
        pairings: [
            {
                partner: { id, ring_id, name, mutation, sex, photo_url } | null,
                children: [ { ...same shape... } ]
            }
        ]
    }
    """
    # Fetch the root bird
    root_result = session.exec(
        text("SELECT id, name, ring_id, mutation, sex, photo_url FROM bird WHERE id = :bird_id"),
        params={"bird_id": bird_id},
    ).mappings().first()

    if not root_result:
        return None

    root = dict(root_result)

    # Fetch all descendants via recursive CTE
    sql = """
    WITH RECURSIVE desc_tree AS (
        SELECT id, name, ring_id, mutation, sex, photo_url, father_id, mother_id, 0 as depth
        FROM bird
        WHERE father_id = :bird_id OR mother_id = :bird_id

        UNION ALL

        SELECT b.id, b.name, b.ring_id, b.mutation, b.sex, b.photo_url, b.father_id, b.mother_id, d.depth + 1
        FROM bird b
        JOIN desc_tree d ON b.father_id = d.id OR b.mother_id = d.id
        WHERE d.depth < :max_depth
    )
    SELECT DISTINCT id, name, ring_id, mutation, sex, photo_url, father_id, mother_id
    FROM desc_tree;
    """
    result = session.exec(
        text(sql), params={"bird_id": bird_id, "max_depth": max_depth}
    ).mappings().all()

    all_descendants = {row["id"]: dict(row) for row in result}

    # Cache for partner bird lookups
    partner_cache: Dict[int, Optional[Dict]] = {}

    def get_partner_info(partner_id: Optional[int]) -> Optional[Dict]:
        if partner_id is None:
            return None
        if partner_id in partner_cache:
            return partner_cache[partner_id]
        # Check if partner is in descendants (unlikely but possible)
        if partner_id in all_descendants:
            p = all_descendants[partner_id]
            info = {
                "id": p["id"], "ring_id": p["ring_id"], "name": p["name"],
                "mutation": p["mutation"], "sex": p["sex"], "photo_url": p["photo_url"],
            }
            partner_cache[partner_id] = info
            return info
        # Otherwise fetch from DB
        p_result = session.exec(
            text("SELECT id, name, ring_id, mutation, sex, photo_url FROM bird WHERE id = :pid"),
            params={"pid": partner_id},
        ).mappings().first()
        info = dict(p_result) if p_result else None
        partner_cache[partner_id] = info
        return info

    def get_children_grouped(parent_id: int, current_depth: int = 0) -> List[Dict]:
        """Group children by their other parent (partner)."""
        if current_depth >= max_depth:
            return []

        # Collect children of this parent
        children_by_partner: Dict[Optional[int], List[Dict]] = {}
        for child in all_descendants.values():
            if child["father_id"] == parent_id:
                partner_id = child["mother_id"]
            elif child["mother_id"] == parent_id:
                partner_id = child["father_id"]
            else:
                continue

            if partner_id not in children_by_partner:
                children_by_partner[partner_id] = []
            children_by_partner[partner_id].append({
                "id": child["id"],
                "ring_id": child["ring_id"],
                "name": child["name"],
                "mutation": child["mutation"],
                "sex": child["sex"],
                "photo_url": child["photo_url"],
                "pairings": get_children_grouped(child["id"], current_depth + 1),
            })

        pairings = []
        for partner_id, children in children_by_partner.items():
            pairings.append({
                "partner": get_partner_info(partner_id),
                "children": children,
            })
        return pairings

    return {
        **root,
        "pairings": get_children_grouped(bird_id),
    }
