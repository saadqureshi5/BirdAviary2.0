import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleCategories = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const id = pathParts.length > 1 ? pathParts[1] : null;

  if (method === 'GET') {
    if (id) {
      const res = await db.query('SELECT * FROM categories WHERE id = ?', [id]);
      return res.values?.[0] || null;
    } else {
      const res = await db.query('SELECT * FROM categories');
      return res.values || [];
    }
  } else if (method === 'POST') {
    const res = await db.run(
      'INSERT INTO categories (name, description) VALUES (?, ?)',
      [payload.name, payload.description]
    );
    const newCat = await db.query('SELECT * FROM categories WHERE id = ?', [res.changes?.lastId]);
    return newCat.values?.[0] || null;
  } else if (method === 'PUT') {
    if (id) {
      await db.run('UPDATE categories SET name = ?, description = ? WHERE id = ?', [payload.name, payload.description, id]);
      const updated = await db.query('SELECT * FROM categories WHERE id = ?', [id]);
      return updated.values?.[0] || null;
    }
  } else if (method === 'DELETE') {
    if (id) {
      await db.run('DELETE FROM categories WHERE id = ?', [id]);
      return { success: true };
    }
  }
  return null;
};
