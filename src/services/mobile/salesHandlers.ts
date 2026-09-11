import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleSales = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const id = pathParts.length > 1 ? pathParts[1] : null;

  if (method === 'GET') {
    if (id) {
      const res = await db.query('SELECT * FROM sale WHERE id = ?', [id]);
      return res.values?.[0] || null;
    } else {
      const res = await db.query('SELECT * FROM sale');
      return res.values || [];
    }
  } else if (method === 'POST') {
    const res = await db.run(
      'INSERT INTO sale (bird_id, sale_price, buyer_name, notes, date_sold) VALUES (?, ?, ?, ?, ?)',
      [payload.bird_id, payload.sale_price, payload.buyer_name, payload.notes, payload.date_sold]
    );
    // Update bird status
    await db.run("UPDATE birds SET status = 'sold' WHERE id = ?", [payload.bird_id]);
    
    const newSale = await db.query('SELECT * FROM sale WHERE id = ?', [res.changes?.lastId]);
    return newSale.values?.[0] || null;
  } else if (method === 'PUT' && id) {
    await db.run(
      'UPDATE sale SET sale_price = ?, buyer_name = ?, notes = ?, date_sold = ? WHERE id = ?',
      [payload.sale_price, payload.buyer_name, payload.notes, payload.date_sold, id]
    );
    const updated = await db.query('SELECT * FROM sale WHERE id = ?', [id]);
    return updated.values?.[0] || null;
  } else if (method === 'DELETE' && id) {
    await db.run('DELETE FROM sale WHERE id = ?', [id]);
    return { success: true };
  }
  return null;
};
