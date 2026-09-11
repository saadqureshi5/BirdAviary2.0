export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface Bird {
  id: string;
  ring_id: string;
  name: string | null;
  mutation: string | null;
  sex: 'male' | 'female' | 'unknown';
  category_id: string | null;
  cage_number: string | null;
  photo_url: string | null;
  father_id: string | null;
  mother_id: string | null;
  status: 'in_stock' | 'sold' | 'deceased' | 'external';
  notes: string | null;
  created_at: string;
  updated_at: string;
  category?: Category;
  father?: Bird;
  mother?: Bird;
}

export interface BirdCreate {
  ring_id: string;
  name?: string;
  mutation?: string;
  sex?: 'male' | 'female' | 'unknown';
  category_id?: string;
  cage_number?: string;
  photo_url?: string;
  father_id?: string;
  mother_id?: string;
  status?: 'in_stock' | 'sold' | 'deceased' | 'external';
  notes?: string;
}

export interface BirdUpdate extends Partial<BirdCreate> {}

export interface Category {
  id: string;
  name: string;
  description: string | null;
}

export interface CategoryWithCount extends Category {
  bird_count: number;
}

export interface Pairing {
  id: number
  bird_a_id: number
  bird_b_id: number
  start_date: string
  end_date: string | null
  cage_number: string | null
  notes: string | null
  created_at: string
}

export interface PairingWithStats extends Pairing {
  bird_a: Bird
  bird_b: Bird
  total_clutches: number
  total_eggs: number
  total_chicks: number
  chicks_fledged: number
  chicks_added_to_stock: number
}

export interface PairingDetail extends Pairing {
  bird_a: Bird
  bird_b: Bird
  clutches: ClutchDetail[]
}

export interface PairingCreate {
  bird_a_id: number
  bird_b_id: number
  start_date: string
  cage_number?: string
  notes?: string
}

export interface Clutch {
  id: number
  pairing_id: number
  clutch_date: string
  total_eggs: number
  fertile_eggs: number
  eggs_lost: number
  loss_reason: string | null
  notes: string | null
  created_at: string
}

export interface ClutchDetail extends Clutch {
  chicks: Chick[]
}

export interface ClutchCreate {
  clutch_date: string
  total_eggs: number
  fertile_eggs?: number
  eggs_lost?: number
  loss_reason?: string
  notes?: string
}

export interface Chick {
  id: number
  clutch_id: number
  ring_id: string | null
  mutation: string | null
  sex: string
  status: 'hatched' | 'fledged' | 'deceased' | 'added_to_stock'
  mortality_reason: string | null
  promoted_bird_id: number | null
  hatch_date: string | null
  fledge_date: string | null
  created_at: string
}

export interface ChickCreate {
  ring_id?: string
  mutation?: string
  sex?: string
  hatch_date?: string
}

export interface BreedingAnalytics {
  total_pairings: number
  total_clutches: number
  total_eggs: number
  total_chicks_hatched: number
  total_chicks_fledged: number
  total_promoted_to_stock: number
  total_deceased: number
  best_pairs: PairingWithStats[]
}

export interface Sale {
  id: number;
  bird_id: number;
  date_sold: string;
  sale_price: number;
  buyer_name: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface SaleWithBird extends Sale {
  bird: Bird | null;
}

export interface SaleCreate {
  bird_id: number;
  date_sold: string;
  sale_price: number;
  buyer_name?: string;
  notes?: string;
}

export interface SaleUpdate {
  date_sold?: string;
  sale_price?: number;
  buyer_name?: string;
  notes?: string;
}

export interface SaleAnalytics {
  total_sales: number;
  total_revenue: number;
  sales_by_month: { year: number; month: number; count: number; revenue: number }[];
  sales_by_category: { category_name: string; count: number; revenue: number }[];
}

export interface DnaRecord {
  id: number;
  bird_id: number;
  file_path: string;
  file_type: 'image' | 'pdf';
  created_at: string;
  bird?: Bird;
}

export interface DnaRecordCreate {
  bird_id: number;
  file_path: string;
  file_type: 'image' | 'pdf';
}

export interface Reminder {
  id: number;
  title: string;
  description: string | null;
  due_date: string;
  recurrence_pattern: string | null;
  is_active: boolean;
  notification_sent: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReminderCreate {
  title: string;
  description?: string;
  due_date: string;
  recurrence_pattern?: string;
}

export interface ReminderUpdate {
  title?: string;
  description?: string;
  due_date?: string;
  recurrence_pattern?: string;
  is_active?: boolean;
}

export interface SoftFoodLog {
  id: number;
  year: number;
  season: 'spring' | 'summer' | 'autumn' | 'winter';
  recipe_name: string;
  ingredients: string;
  supplements: string | null;
  results: string | null;
  created_at: string;
}

export interface SoftFoodLogCreate {
  year: number;
  season: 'spring' | 'summer' | 'autumn' | 'winter';
  recipe_name: string;
  ingredients: string;
  supplements?: string;
  results?: string;
}

export interface SoftFoodLogUpdate {
  year?: number;
  season?: 'spring' | 'summer' | 'autumn' | 'winter';
  recipe_name?: string;
  ingredients?: string;
  supplements?: string;
  results?: string;
}

export interface Expense {
  id: number;
  year: number;
  month: number;
  date: string;
  description: string;
  amount: number;
  created_at: string;
  updated_at: string;
}

export interface ExpenseCreate {
  year: number;
  month: number;
  date: string;
  description: string;
  amount: number;
}

export interface ExpenseUpdate {
  year?: number;
  month?: number;
  date?: string;
  description?: string;
  amount?: number;
}

export interface ExpenseAnalytics {
  total_expenses: number;
  monthly_totals: { year: number; month: number; total: number }[];
  yearly_totals: { year: number; total: number }[];
}

export interface SearchResult {
  birds: Bird[];
}

export interface AncestryNode {
  bird: Bird;
  father: AncestryNode | null;
  mother: AncestryNode | null;
}

export interface AncestryTreeNode {
  id: number
  ring_id: string | null
  name: string | null
  mutation: string | null
  sex: string | null
  photo_url: string | null
  father: AncestryTreeNode | null
  mother: AncestryTreeNode | null
}

export interface DescendantsTreeNode {
  id: number
  ring_id: string | null
  name: string | null
  mutation: string | null
  sex: string | null
  photo_url: string | null
  children: DescendantsTreeNode[]
}

export interface BirdStats {
  total_birds: number;
  in_stock: number;
  sold: number;
  deceased: number;
  active_pairs: number;
}

export interface ActivityItem {
  id: number;
  icon: string;
  title: string;
  description: string;
  timestamp: string;
  table_name: string;
  action: string;
}

export interface SyncLogEntry {
  id: number
  device_id: string
  table_name: string
  record_id: number
  action: 'INSERT' | 'UPDATE' | 'DELETE'
  payload: string
  timestamp: string
  synced: boolean
}

export interface SyncStatus {
  total_entries: number
  unsynced_count: number
  last_sync_timestamp: string | null
}

export interface GoogleDriveTokens {
  access_token: string
  refresh_token?: string
  expires_at: number
  token_type: string
}

export interface SyncState {
  isAuthenticated: boolean
  isSyncing: boolean
  lastSyncTime: string | null
  pendingCount: number
  error: string | null
  autoSync: boolean
}

// ── User & License Types ──────────────────────────────────

export interface UserProfile {
  email: string
  name: string
  avatar_url: string
  google_id: string
}

export interface LicenseData {
  valid: boolean
  plan: string
  expires_at: string | null
  license_token: string | null
  cached_at: number
}

export interface UpdateInfo {
  version: string
  download_url: string
  changelog: string
  force_update: boolean
}
