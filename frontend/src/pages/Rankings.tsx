import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse } from '../types';

const FILTERS = [
  { key: 'gainers', label: '涨幅榜' },
  { key: 'losers', label: '跌幅榜' },
  { key: 'volume', label: '成交量' },
  { key: 'market_cap', label: '总市值' },
  { key: 'hot', label: '热度榜' },
  { key: 'arbitrage', label: '挂刀收益' },
];

export default function Rankings() {
  const [filter, setFilter] = useState('gainers');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['rankings', filter, page],
    queryFn: () => api.get<ApiResponse<{ items: any[]; total?: number }>>(
      `/rankings/list?page=${page}&page_size=50&filter=${filter}`
    ),
  });

  const items = data?.data?.items ?? data?.data ?? [];
  const itemsList = Array.isArray(items) ? items : [];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">排行榜</h1>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 mb-6">
        {FILTERS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => { setFilter(key); setPage(1); }}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{
              backgroundColor: filter === key ? 'var(--accent-green)' : 'var(--bg-card)',
              color: filter === key ? '#000' : 'var(--text-secondary)',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ backgroundColor: 'var(--bg-hover)' }}>
              <th className="text-left py-3 px-4">#</th>
              <th className="text-left py-3 px-4">名称</th>
              <th className="text-right py-3 px-4">价格</th>
              <th className="text-right py-3 px-4">涨跌幅</th>
              <th className="text-right py-3 px-4 hidden md:table-cell">成交量</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={5} className="text-center py-8" style={{ color: 'var(--text-muted)' }}>加载中...</td></tr>
            ) : itemsList.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-8" style={{ color: 'var(--text-muted)' }}>暂无数据</td></tr>
            ) : (
              itemsList.map((item: any, idx: number) => (
                <tr key={item.good_id ?? idx} className="border-t hover:bg-opacity-50 cursor-pointer"
                    style={{ borderColor: 'var(--border-color)' }}
                    onClick={() => window.location.href = `/items/${item.good_id}`}>
                  <td className="py-3 px-4" style={{ color: 'var(--text-muted)' }}>{(page - 1) * 50 + idx + 1}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      {item.image_url && <img src={item.image_url} alt="" className="w-8 h-8 object-contain rounded" />}
                      <span className="truncate max-w-[200px]">{item.name ?? 'N/A'}</span>
                    </div>
                  </td>
                  <td className="text-right py-3 px-4">¥{item.price?.toFixed(2) ?? 'N/A'}</td>
                  <td className={`text-right py-3 px-4 ${item.change_pct >= 0 ? 'price-up' : 'price-down'}`}>
                    {item.change_pct != null ? `${item.change_pct >= 0 ? '+' : ''}${item.change_pct}%` : 'N/A'}
                  </td>
                  <td className="text-right py-3 px-4 hidden md:table-cell" style={{ color: 'var(--text-secondary)' }}>
                    {item.volume?.toLocaleString() ?? 'N/A'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-center items-center gap-4 mt-6">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-4 py-2 rounded-lg text-sm disabled:opacity-30"
          style={{ backgroundColor: 'var(--bg-card)' }}
        >
          上一页
        </button>
        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>第 {page} 页</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          className="px-4 py-2 rounded-lg text-sm"
          style={{ backgroundColor: 'var(--bg-card)' }}
        >
          下一页
        </button>
      </div>
    </div>
  );
}
