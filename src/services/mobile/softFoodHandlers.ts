import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleSoftFood = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const id = pathParts.length > 1 ? pathParts[1] : null;

  if (method === 'GET') {
    const res = await db.query('SELECT * FROM soft_food_logs');
    return res.values || [];
  } else if (method === 'POST') {
    const res = await db.run(
      'INSERT INTO soft_food_logs (year, season, recipe_name, ingredients, supplements, results) VALUES (?, ?, ?, ?, ?, ?)',
      [payload.year, payload.season, payload.recipe_name, payload.ingredients, payload.supplements, payload.results]
    );
    const newLog = await db.query('SELECT * FROM soft_food_logs WHERE id = ?', [res.changes?.lastId]);
    return newLog.values?.[0] || null;
  } else if (method === 'PUT' && id) {
    await db.run(
      'UPDATE soft_food_logs SET year = ?, season = ?, recipe_name = ?, ingredients = ?, supplements = ?, results = ? WHERE id = ?',
      [payload.year, payload.season, payload.recipe_name, payload.ingredients, payload.supplements, payload.results, id]
    );
    const updated = await db.query('SELECT * FROM soft_food_logs WHERE id = ?', [id]);
    return updated.values?.[0] || null;
  } else if (method === 'DELETE' && id) {
    await db.run('DELETE FROM soft_food_logs WHERE id = ?', [id]);
    return { success: true };
  }
  return null;
};
