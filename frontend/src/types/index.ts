// Common API response
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

// Market types
export interface IndexData {
  index_value: number | null;
  index_change_pct: number | null;
  online_players: number | null;
}

export interface MarketOverview {
  index: IndexData | null;
  total_market_cap: number | null;
  volume_24h: number | null;
  top_gainers: RankingItem[];
  top_losers: RankingItem[];
  hot_items: HotItem[];
}

export interface HotItem {
  good_id: string;
  name: string;
  market_hash_name: string;
  image_url?: string;
  price?: number;
  change_pct?: number;
}

// Item types
export interface ItemSearchResult {
  good_id: string;
  name: string;
  market_hash_name: string;
  image_url?: string;
}

export interface ItemDetail {
  good_id: string;
  name: string;
  market_hash_name: string;
  image_url?: string;
  category?: string;
  prices: Record<string, { sell_price?: number; buy_price?: number }>;
  volume?: Record<string, unknown>;
  circulation?: number;
  market_cap?: number;
  change_pct_24h?: number;
  change_pct_7d?: number;
}

export interface ChartDataPoint {
  date: string;
  value: number;
}

// Ranking types
export interface RankingItem {
  rank: number;
  good_id: string;
  name: string;
  market_hash_name: string;
  image_url?: string;
  price?: number;
  change_pct?: number;
  volume?: number;
  market_cap?: number;
}

// Watchlist types
export interface WatchlistItem {
  id: number;
  good_id: string;
  market_hash_name: string;
  item_name?: string;
  image_url?: string;
  category?: string;
  tags: string[];
  notes?: string;
  added_at: string;
  last_price?: number;
  change_pct_24h?: number;
  last_updated_at?: string;
}

// Portfolio types
export interface PortfolioHolding {
  id: number;
  good_id: string;
  market_hash_name: string;
  item_name?: string;
  image_url?: string;
  quantity: number;
  purchase_price: number;
  current_price?: number;
  cost_basis: number;
  current_value?: number;
  pnl?: number;
  pnl_pct?: number;
  purchase_date: string;
  purchase_platform: string;
  wear?: string;
  notes?: string;
}

export interface PortfolioSummary {
  total_cost: number;
  total_value: number | null;
  total_pnl: number | null;
  total_pnl_pct: number | null;
  holding_count: number;
  diversification: Record<string, number>;
}

// Alert types
export interface PriceAlert {
  id: number;
  good_id: string;
  market_hash_name: string;
  alert_type: 'price_above' | 'price_below' | 'pct_change_up' | 'pct_change_down';
  threshold_value: number;
  platform: string;
  is_active: number;
  triggered_at?: string;
  last_notified_price?: number;
  created_at: string;
}

// Arbitrage types
export interface ArbitrageOverview {
  buff_steam_ratio?: number;
  uuyp_steam_ratio?: number;
  platforms: Record<string, unknown>[];
}

// Case types
export interface CaseListItem {
  case_id: string;
  name: string;
  image_url?: string;
  price?: number;
  roi_pct?: number;
  expected_value?: number;
  open_count_24h?: number;
}

export interface CaseDetail {
  case_id: string;
  name?: string;
  roi_chart: unknown[];
  open_history: unknown[];
  contents: unknown[];
}

// AI types
export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface AIMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  context_json?: string;
  created_at: string;
}

export interface ChatRequest {
  conversation_id?: number;
  message: string;
  context_hints?: {
    item_ids?: string[];
    include_portfolio?: boolean;
    include_market?: boolean;
  };
}
