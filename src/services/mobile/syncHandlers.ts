import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleSync = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  if (method === 'GET') {
    return { status: 'mocked sync implementation' };
  } else if (method === 'POST') {
    return { status: 'mocked sync implementation' };
  }
  return null;
};
