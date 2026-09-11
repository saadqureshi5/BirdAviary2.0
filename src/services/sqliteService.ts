import { Capacitor } from '@capacitor/core';
import { CapacitorSQLite, SQLiteConnection, SQLiteDBConnection } from '@capacitor-community/sqlite';

const sqlite: SQLiteConnection = new SQLiteConnection(CapacitorSQLite);
let db: SQLiteDBConnection | null = null;

export const initDb = async () => {
  if (!Capacitor.isNativePlatform()) return;

  try {
    const ret = await sqlite.checkConnectionsConsistency();
    const isConn = (await sqlite.isConnection('birdaviary', false)).result;

    if (ret.result && isConn) {
      db = await sqlite.retrieveConnection('birdaviary', false);
    } else {
      db = await sqlite.createConnection('birdaviary', false, 'no-encryption', 1, false);
    }

    await db.open();

    // Create tables
    await db.execute(`
      CREATE TABLE IF NOT EXISTS categories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE,
          description TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      
      CREATE TABLE IF NOT EXISTS birds (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ring_id TEXT UNIQUE,
          name TEXT,
          mutation TEXT,
          sex TEXT CHECK(sex IN ('male', 'female', 'unknown')) DEFAULT 'unknown',
          photo_url TEXT,
          cage_number TEXT,
          category_id INTEGER,
          father_id INTEGER,
          mother_id INTEGER,
          status TEXT CHECK(status IN ('in_stock', 'sold', 'deceased')) DEFAULT 'in_stock',
          notes TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL,
          FOREIGN KEY(father_id) REFERENCES birds(id) ON DELETE SET NULL,
          FOREIGN KEY(mother_id) REFERENCES birds(id) ON DELETE SET NULL
      );

      CREATE TABLE IF NOT EXISTS pairing (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          bird_a_id INTEGER NOT NULL,
          bird_b_id INTEGER NOT NULL,
          start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
          end_date DATETIME,
          cage_number TEXT,
          notes TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(bird_a_id) REFERENCES birds(id) ON DELETE CASCADE,
          FOREIGN KEY(bird_b_id) REFERENCES birds(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS clutch (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          pairing_id INTEGER NOT NULL,
          clutch_date DATETIME DEFAULT CURRENT_TIMESTAMP,
          total_eggs INTEGER DEFAULT 0,
          fertile_eggs INTEGER DEFAULT 0,
          hatched_eggs INTEGER DEFAULT 0,
          eggs_lost INTEGER DEFAULT 0,
          loss_reason TEXT,
          notes TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(pairing_id) REFERENCES pairing(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS chick (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          clutch_id INTEGER NOT NULL,
          ring_id TEXT,
          mutation TEXT,
          sex TEXT DEFAULT 'unknown',
          status TEXT DEFAULT 'hatched',
          mortality_reason TEXT,
          promoted_bird_id INTEGER,
          hatch_date DATETIME,
          fledge_date DATETIME,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(clutch_id) REFERENCES clutch(id) ON DELETE CASCADE,
          FOREIGN KEY(promoted_bird_id) REFERENCES birds(id) ON DELETE SET NULL
      );

      CREATE TABLE IF NOT EXISTS sale (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          bird_id INTEGER NOT NULL,
          sale_price REAL DEFAULT 0.0,
          buyer_name TEXT,
          notes TEXT,
          date_sold DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(bird_id) REFERENCES birds(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS dnarecord (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          bird_id INTEGER NOT NULL,
          file_path TEXT NOT NULL,
          file_type TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(bird_id) REFERENCES birds(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS reminder (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          description TEXT,
          due_date DATETIME NOT NULL,
          recurrence_pattern TEXT,
          is_active BOOLEAN DEFAULT 1,
          notification_sent BOOLEAN DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS soft_food_logs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          year INTEGER NOT NULL,
          season TEXT NOT NULL,
          recipe_name TEXT NOT NULL,
          ingredients TEXT NOT NULL,
          supplements TEXT,
          results TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS expenses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          year INTEGER NOT NULL,
          month INTEGER NOT NULL,
          date DATE NOT NULL,
          description TEXT NOT NULL,
          amount REAL NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS synclog (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          device_id TEXT NOT NULL,
          table_name TEXT NOT NULL,
          record_id INTEGER NOT NULL,
          action TEXT NOT NULL,
          payload TEXT NOT NULL,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          synced BOOLEAN DEFAULT 0
      );

      CREATE TABLE IF NOT EXISTS auditlog (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          table_name TEXT NOT NULL,
          record_id INTEGER NOT NULL,
          action TEXT NOT NULL,
          old_values TEXT,
          new_values TEXT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log("Database initialized successfully!");
  } catch (error) {
    console.error("Database initialization failed:", error);
    throw error;
  }
};

export const getDb = (): SQLiteDBConnection => {
  if (!db) {
    throw new Error('Database not initialized');
  }
  return db;
};
