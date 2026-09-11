import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleActivity = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  if (method === 'GET') {
    // Basic mock implementation for activity on mobile
    return [];
  }
  return null;
};
