import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleDna = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const id = pathParts.length > 1 ? pathParts[1] : null;

  if (method === 'GET') {
    if (pathParts[1] === 'bird' && pathParts[2]) {
      const res = await db.query('SELECT * FROM dnarecord WHERE bird_id = ?', [pathParts[2]]);
      return res.values || [];
    }
    const res = await db.query('SELECT * FROM dnarecord');
    return res.values || [];
  } else if (method === 'POST') {
    // Note: the file itself is saved by the store via capacitor filesystem
    const res = await db.run(
      'INSERT INTO dnarecord (bird_id, file_path, file_type) VALUES (?, ?, ?)',
      [payload.bird_id, payload.file_path, payload.file_type]
    );
    const newRecord = await db.query('SELECT * FROM dnarecord WHERE id = ?', [res.changes?.lastId]);
    return newRecord.values?.[0] || null;
  } else if (method === 'DELETE' && id) {
    await db.run('DELETE FROM dnarecord WHERE id = ?', [id]);
    return { success: true };
  }
  return null;
};
