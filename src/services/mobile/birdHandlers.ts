import { getDb } from '../sqliteService';
import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleBirds = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const id = pathParts.length > 1 && pathParts[1] !== 'search' && pathParts[1] !== 'stats' ? pathParts[1] : null;

  if (method === 'GET') {
    if (pathParts[1] === 'search') {
      const q = payload?.q || '';
      const res = await db.query(`SELECT * FROM birds WHERE name LIKE ? OR ring_id LIKE ?`, [`%${q}%`, `%${q}%`]);
      return res.values || [];
    } else if (pathParts[1] === 'stats' && pathParts[2] === 'summary') {
      const total = await db.query('SELECT COUNT(*) as count FROM birds');
      const inStock = await db.query("SELECT COUNT(*) as count FROM birds WHERE status = 'in_stock'");
      return { total: total.values?.[0]?.count || 0, inStock: inStock.values?.[0]?.count || 0 };
    } else if (id) {
      if (pathParts[2] === 'siblings') {
        const res = await db.query(`
          SELECT b.* FROM birds b 
          JOIN birds t ON b.father_id = t.father_id OR b.mother_id = t.mother_id 
          WHERE t.id = ? AND b.id != ?`, [id, id]);
        return res.values || [];
      } else if (pathParts[2] === 'pairings') {
        const res = await db.query('SELECT * FROM pairing WHERE bird_a_id = ? OR bird_b_id = ?', [id, id]);
        return res.values || [];
      } else if (pathParts[2] === 'ancestry' && pathParts[3] === 'tree') {
        const res = await db.query(`
          WITH RECURSIVE ancestor_tree AS (
            SELECT id, name, ring_id, father_id, mother_id, mutation, sex, 0 as level 
            FROM birds WHERE id = ?
            UNION ALL
            SELECT b.id, b.name, b.ring_id, b.father_id, b.mother_id, b.mutation, b.sex, a.level + 1
            FROM birds b
            JOIN ancestor_tree a ON b.id = a.father_id OR b.id = a.mother_id
            WHERE a.level < 5
          )
          SELECT * FROM ancestor_tree
        `, [id]);
        if (!res.values || res.values.length === 0) return null;
        const buildAncestryTree = (nodeId: number, level: number): any => {
          if (level > 5) return null;
          const node = res.values!.find(b => b.id === nodeId && b.level === level);
          if (!node) return null;
          return {
            id: node.id,
            ring_id: node.ring_id,
            name: node.name,
            mutation: node.mutation,
            sex: node.sex,
            photo_url: null,
            father: node.father_id ? buildAncestryTree(node.father_id, level + 1) : null,
            mother: node.mother_id ? buildAncestryTree(node.mother_id, level + 1) : null
          };
        };
        return buildAncestryTree(Number(id), 0);
      } else if (pathParts[2] === 'descendants' && pathParts[3] === 'tree') {
        const res = await db.query(`
          WITH RECURSIVE descendant_tree AS (
            SELECT id, name, ring_id, father_id, mother_id, mutation, sex, 0 as level 
            FROM birds WHERE id = ?
            UNION ALL
            SELECT b.id, b.name, b.ring_id, b.father_id, b.mother_id, b.mutation, b.sex, d.level + 1
            FROM birds b
            JOIN descendant_tree d ON b.father_id = d.id OR b.mother_id = d.id
            WHERE d.level < 5
          )
          SELECT * FROM descendant_tree
        `, [id]);
        if (!res.values || res.values.length === 0) return null;
        const buildDescendantTree = (nodeId: number, level: number): any => {
          if (level > 5) return null;
          const node = res.values!.find(b => b.id === nodeId && b.level === level);
          if (!node) return null;
          const childrenNodes = res.values!.filter(b => (b.father_id === nodeId || b.mother_id === nodeId) && b.level === level + 1);
          return {
            id: node.id,
            ring_id: node.ring_id,
            name: node.name,
            mutation: node.mutation,
            sex: node.sex,
            photo_url: null,
            children: childrenNodes.map(c => buildDescendantTree(c.id, level + 1)).filter(Boolean)
          };
        };
        return buildDescendantTree(Number(id), 0);
      }
      const res = await db.query('SELECT * FROM birds WHERE id = ?', [id]);
      return res.values?.[0] || null;
    } else {
      const res = await db.query('SELECT * FROM birds');
      return res.values || [];
    }
  } else if (method === 'POST') {
    if (id && pathParts[2] === 'photo') {
      return { status: 'ok' }; // handled by filesystem in views/stores directly
    }
    const res = await db.run(
      'INSERT INTO birds (ring_id, name, mutation, sex, cage_number, category_id, father_id, mother_id, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [payload.ring_id, payload.name, payload.mutation, payload.sex, payload.cage_number, payload.category_id, payload.father_id, payload.mother_id, payload.status, payload.notes]
    );
    const newBird = await db.query('SELECT * FROM birds WHERE id = ?', [res.changes?.lastId]);
    return newBird.values?.[0] || null;
  } else if (method === 'PUT') {
    if (id) {
      const sets = [];
      const values = [];
      for (const [key, value] of Object.entries(payload)) {
        sets.push(`${key} = ?`);
        values.push(value);
      }
      values.push(id);
      await db.run(`UPDATE birds SET ${sets.join(', ')} WHERE id = ?`, values);
      const updated = await db.query('SELECT * FROM birds WHERE id = ?', [id]);
      return updated.values?.[0] || null;
    }
  } else if (method === 'DELETE') {
    if (id) {
      await db.run('DELETE FROM birds WHERE id = ?', [id]);
      return { success: true };
    }
  }
  return null;
};
