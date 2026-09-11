import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleReminders = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const id = pathParts.length > 1 ? pathParts[1] : null;

  if (method === 'GET') {
    const res = await db.query('SELECT * FROM reminder');
    return res.values || [];
  } else if (method === 'POST') {
    const res = await db.run(
      'INSERT INTO reminder (title, description, due_date, recurrence_pattern, is_active, notification_sent) VALUES (?, ?, ?, ?, ?, ?)',
      [payload.title, payload.description, payload.due_date, payload.recurrence_pattern, payload.is_active ? 1 : 0, payload.notification_sent ? 1 : 0]
    );
    const newReminder = await db.query('SELECT * FROM reminder WHERE id = ?', [res.changes?.lastId]);
    return newReminder.values?.[0] || null;
  } else if (method === 'PUT' && id) {
    await db.run(
      'UPDATE reminder SET title = ?, description = ?, due_date = ?, recurrence_pattern = ?, is_active = ?, notification_sent = ? WHERE id = ?',
      [payload.title, payload.description, payload.due_date, payload.recurrence_pattern, payload.is_active ? 1 : 0, payload.notification_sent ? 1 : 0, id]
    );
    const updated = await db.query('SELECT * FROM reminder WHERE id = ?', [id]);
    return updated.values?.[0] || null;
  } else if (method === 'DELETE' && id) {
    await db.run('DELETE FROM reminder WHERE id = ?', [id]);
    return { success: true };
  }
  return null;
};
