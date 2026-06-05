import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, MarketOverview } from '../types';

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['market', 'overview'],
    queryFn: () => api.get<ApiResponse<MarketOverview>>('/market/overview'),
  });

  const overview = data?.data;

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">数据看板</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="饰品指数"
          value={overview?.index?.index_value}
          change={overview?.index?.index_change_pct}
          suffix=""
        />
        <StatCard
          title="24h 成交量"
          value={overview?.volume_24h}
          suffix="件"
        />
        <StatCard
          title="总市值"
          value={overview?.total_market_cap}
          suffix=""
        />
        <StatCard
          title="在线玩家"
          value={overview?.index?.online_players}
          suffix="人"
        />
      </div>

      {/* Hot Items */}
      <Section title="热门饰品">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          {overview?.hot_items?.slice(0, 8).map((item) => (
            <div
              key={item.good_id}
              className="rounded-lg p-3 cursor-pointer hover:opacity-80 transition-opacity"
              style={{ backgroundColor: 'var(--bg-card)' }}
            >
              {item.image_url && (
                <img src={item.image_url} alt={item.name} className="w-full h-24 object-contain mb-2" loading="lazy" />
              )}
              <p className="text-xs truncate" style={{ color: 'var(--text-secondary)' }}>{item.name}</p>
              <p className="text-sm font-medium">¥{item.price?.toFixed(2) ?? 'N/A'}</p>
              {item.change_pct != null && (
                <span className={`text-xs ${item.change_pct >= 0 ? 'price-up' : 'price-down'}`}>
                  {item.change_pct >= 0 ? '+' : ''}{item.change_pct}%
                </span>
              )}
            </div>
          ))}
        </div>
      </Section>

      {/* Top Gainers & Losers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RankingTable title="涨幅榜" items={overview?.top_gainers ?? []} color="price-up" />
        <RankingTable title="跌幅榜" items={overview?.top_losers ?? []} color="price-down" />
      </div>
    </div>
  );
}

// Sub-components

function StatCard({ title, value, change, suffix = '' }: {
  title: string; value?: number | null; change?: number | null; suffix?: string;
}) {
  return (
    <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-card)' }}>
      <p className="text-sm mb-1" style={{ color: 'var(--text-secondary)' }}>{title}</p>
      <p className="text-2xl font-bold">
        {value != null ? `${value.toLocaleString()}${suffix}` : 'N/A'}
      </p>
      {change != null && (
        <span className={`text-sm ${change >= 0 ? 'price-up' : 'price-down'}`}>
          {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(2)}%
        </span>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <h2 className="text-lg font-semibold mb-3">{title}</h2>
      {children}
    </div>
  );
}

function RankingTable({ title, items, color }: { title: string; items: any[]; color: string }) {
  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--bg-card)' }}>
      <h2 className="text-lg font-semibold mb-3">{title}</h2>
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: 'var(--text-muted)' }}>
            <th className="text-left pb-2">#</th>
            <th className="text-left pb-2">名称</th>
            <th className="text-right pb-2">价格</th>
            <th className="text-right pb-2">涨跌幅</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item: any, idx: number) => (
            <tr key={item.good_id ?? idx} className="border-t" style={{ borderColor: 'var(--border-color)' }}>
              <td className="py-2" style={{ color: 'var(--text-muted)' }}>{idx + 1}</td>
              <td className="py-2 truncate max-w-[120px]">{item.name ?? 'N/A'}</td>
              <td className="py-2 text-right">¥{item.price?.toFixed(2) ?? 'N/A'}</td>
              <td className={`py-2 text-right ${color}`}>
                {item.change_pct != null ? `${item.change_pct >= 0 ? '+' : ''}${item.change_pct}%` : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-8 w-32 rounded mb-6" style={{ backgroundColor: 'var(--bg-card)' }} />
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-24 rounded-xl" style={{ backgroundColor: 'var(--bg-card)' }} />
        ))}
      </div>
    </div>
  );
}
