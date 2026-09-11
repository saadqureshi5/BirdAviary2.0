import { getDb } from './sqliteService';
import { handleBirds } from './mobile/birdHandlers';
import { handleCategories } from './mobile/categoryHandlers';
import { handleBreeding } from './mobile/breedingHandlers';
import { handleSales } from './mobile/salesHandlers';
import { handleDna } from './mobile/dnaHandlers';
import { handleReminders } from './mobile/reminderHandlers';
import { handleSoftFood } from './mobile/softFoodHandlers';
import { handleExpenses } from './mobile/expenseHandlers';
import { handleActivity } from './mobile/activityHandlers';
import { handleSync } from './mobile/syncHandlers';

export const processMobileRequest = async (method: string, url: string, body?: any): Promise<any> => {
  const db = getDb();
  console.log(`[Mobile Data Layer] ${method} ${url}`);

  try {
    const pathParts = url.split('/').filter(p => p.length > 0);
    const resource = pathParts[0];

    const payload = typeof body === 'string' ? JSON.parse(body) : body;

    switch (resource) {
      case 'birds':
        return await handleBirds(method, pathParts, payload, db);
      case 'categories':
        return await handleCategories(method, pathParts, payload, db);
      case 'pairings':
      case 'clutches':
      case 'chicks':
      case 'breeding':
        return await handleBreeding(method, pathParts, payload, db);
      case 'sales':
        return await handleSales(method, pathParts, payload, db);
      case 'dna':
        return await handleDna(method, pathParts, payload, db);
      case 'reminders':
        return await handleReminders(method, pathParts, payload, db);
      case 'soft-food':
        return await handleSoftFood(method, pathParts, payload, db);
      case 'expenses':
        return await handleExpenses(method, pathParts, payload, db);
      case 'activity':
        return await handleActivity(method, pathParts, payload, db);
      case 'sync':
        return await handleSync(method, pathParts, payload, db);
      default:
        console.warn(`[Mobile Data Layer] Unimplemented route: ${method} ${url}`);
        return null;
    }
  } catch (err) {
    console.error(`[Mobile Data Layer] Error processing ${method} ${url}:`, err);
    throw err;
  }
};
