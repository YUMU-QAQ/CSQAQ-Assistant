import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse } from '../types';
import ReactECharts from 'echarts-for-react';

export default function ItemDetail() {
  const { goodId } = useParams<{ goodId: string }>();
  const navigate = useNavigate();

  const { data: detailData, isLoading } = useQuery({
    queryKey: ['item', goodId],
    queryFn: () => api.get<ApiResponse<Record<string, unknown>>>(`/items/${goodId}`),
    enabled: !!goodId,
  });

  const { data: chartData } = useQuery({
    queryKey: ['item', goodId, 'chart'],
    queryFn: () => api.get<ApiResponse<{ date: string; value: number }[]>>(`/items/${goodId}/chart?platform=1&period=30&key=sell_price`),
    enabled: !!goodId,
  });

  const item = detailData?.data as Record<string, unknown> | null;

  if (isLoading) {
    return <p className="text-muted-text">加载中...</p>;
  }

  if (!item) {
    return <p className="text-muted-text">物品未找到</p>;
  }

  // Build chart option
  const chartPoints = chartData?.data ?? [];
  const chartOption = {
    tooltip: { trigger: 'axis' as const },
    grid: { left: 60, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category' as const,
      data: chartPoints.map((p: any) => p.date ?? ''),
      axisLabel: { color: '#8b95a8', fontSize: 10 },
    },
    yAxis: {
      type: 'value' as const,
      axisLabel: { color: '#8b95a8' },
      splitLine: { lineStyle: { color: '#2a3040' } },
    },
    series: [{
      type: 'line',
      data: chartPoints.map((p: any) => p.value ?? 0),
      smooth: true,
      lineStyle: { color: '#00d4aa', width: 2 },
      itemStyle: { color: '#00d4aa' },
      areaStyle: { color: 'rgba(0, 212, 170, 0.1)' },
      showSymbol: false,
    }],
  };

  const prices = (item.prices as Record<string, { sell_price?: number }>) ?? {};
  const priceEntries = Object.entries(prices);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate('/items')}
          className="px-3 py-1.5 rounded-lg text-sm bg-card text-secondary-text hover:bg-hover transition-all duration-200"
        >
          ← 返回
        </button>
        <div>
          <h1 className="text-2xl font-bold">{item.name as string}</h1>
          <p className="text-muted-text">{item.market_hash_name as string}</p>
        </div>
      </div>

      {/* Price Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {priceEntries.map(([platform, p]) => (
          <div key={platform} className="rounded-xl p-4 bg-card">
            <p className="text-sm text-secondary-text">{platform}</p>
            <p className="text-2xl font-bold mt-1">¥{p.sell_price?.toFixed(2) ?? 'N/A'}</p>
          </div>
        ))}
      </div>

      {/* Price Chart */}
      <div className="rounded-xl p-4 mb-6 bg-card">
        <h2 className="text-lg font-semibold mb-4">价格走势 (30天)</h2>
        {chartPoints.length > 0 ? (
          <ReactECharts option={chartOption} style={{ height: 350 }} />
        ) : (
          <p className="text-muted-text">暂无图表数据</p>
        )}
      </div>

      {/* Stats */}
      {(item.circulation != null || item.market_cap != null) && (
        <div className="rounded-xl p-4 bg-card">
          <h2 className="text-lg font-semibold mb-3">市场数据</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {item.circulation != null && (
              <div><span className="text-muted-text">存世量: </span>{Number(item.circulation).toLocaleString()}</div>
            )}
            {item.market_cap != null && (
              <div><span className="text-muted-text">总市值: </span>¥{Number(item.market_cap).toLocaleString()}</div>
            )}
            {item.change_pct_24h != null && (
              <div>
                <span className="text-muted-text">24h涨跌: </span>
                <span className={Number(item.change_pct_24h) >= 0 ? 'price-up' : 'price-down'}>
                  {Number(item.change_pct_24h) >= 0 ? '+' : ''}{Number(item.change_pct_24h).toFixed(2)}%
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
