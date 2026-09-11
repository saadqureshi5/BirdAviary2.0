import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleExpenses = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const id = pathParts.length > 1 ? pathParts[1] : null;

  if (method === 'GET') {
    const res = await db.query('SELECT * FROM expenses');
    return res.values || [];
  } else if (method === 'POST') {
    const res = await db.run(
      'INSERT INTO expenses (year, month, date, description, amount) VALUES (?, ?, ?, ?, ?)',
      [payload.year, payload.month, payload.date, payload.description, payload.amount]
    );
    const newExpense = await db.query('SELECT * FROM expenses WHERE id = ?', [res.changes?.lastId]);
    return newExpense.values?.[0] || null;
  } else if (method === 'PUT' && id) {
    await db.run(
      'UPDATE expenses SET year = ?, month = ?, date = ?, description = ?, amount = ? WHERE id = ?',
      [payload.year, payload.month, payload.date, payload.description, payload.amount, id]
    );
    const updated = await db.query('SELECT * FROM expenses WHERE id = ?', [id]);
    return updated.values?.[0] || null;
  } else if (method === 'DELETE' && id) {
    await db.run('DELETE FROM expenses WHERE id = ?', [id]);
    return { success: true };
  }
  return null;
};
