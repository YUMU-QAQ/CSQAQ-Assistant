import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, ArbitrageOverview } from '../types';

export default function Arbitrage() {
  const { data: overviewData } = useQuery({
    queryKey: ['arbitrage', 'overview'],
    queryFn: () => api.get<ApiResponse<ArbitrageOverview>>('/arbitrage/overview'),
  });

  const { data: oppData } = useQuery({
    queryKey: ['arbitrage', 'opportunities'],
    queryFn: () => api.get<ApiResponse<any[]>>('/arbitrage/opportunities?min_profit=0.05&sort=profit_desc'),
  });

  const overview = overviewData?.data;
  const opportunities = oppData?.data ?? [];
  const opps = Array.isArray(opportunities) ? opportunities : [];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">挂刀分析</h1>

      {/* Exchange Rate Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="rounded-xl p-5 bg-card">
          <p className="text-sm text-secondary-text">BUFF/Steam 汇率</p>
          <p className="text-2xl font-bold mt-1">{overview?.buff_steam_ratio?.toFixed(4) ?? 'N/A'}</p>
        </div>
        <div className="rounded-xl p-5 bg-card">
          <p className="text-sm text-secondary-text">UUYP/Steam 汇率</p>
          <p className="text-2xl font-bold mt-1">{overview?.uuyp_steam_ratio?.toFixed(4) ?? 'N/A'}</p>
        </div>
        <div className="rounded-xl p-5 bg-card">
          <p className="text-sm text-secondary-text">平台数量</p>
          <p className="text-2xl font-bold mt-1">{overview?.platforms?.length ?? 'N/A'}</p>
        </div>
      </div>

      {/* Opportunities Table */}
      {opps.length > 0 && (
        <div className="rounded-xl overflow-hidden bg-card">
          <h2 className="text-lg font-semibold p-4 pb-0">套利机会</h2>
          <table className="w-full text-sm mt-4">
            <thead>
              <tr className="bg-hover">
                <th className="text-left py-3 px-4">#</th>
                <th className="text-left py-3 px-4">饰品</th>
                <th className="text-right py-3 px-4">买入价</th>
                <th className="text-right py-3 px-4 hidden md:table-cell">卖出价</th>
                <th className="text-right py-3 px-4">利润率</th>
              </tr>
            </thead>
            <tbody>
              {opps.map((item: any, idx: number) => (
                <tr key={item.good_id ?? idx} className="border-t border-border">
                  <td className="py-3 px-4 text-muted-text">{idx + 1}</td>
                  <td className="py-3 px-4 truncate max-w-[200px]">{item.name ?? 'N/A'}</td>
                  <td className="text-right py-3 px-4">¥{item.buy_price?.toFixed(2) ?? 'N/A'}</td>
                  <td className="text-right py-3 px-4 hidden md:table-cell">¥{item.sell_price?.toFixed(2) ?? 'N/A'}</td>
                  <td className="text-right py-3 px-4 price-up">
                    {item.profit_margin != null ? `${item.profit_margin}%` : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
