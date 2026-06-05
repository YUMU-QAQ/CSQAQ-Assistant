import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, PortfolioHolding, PortfolioSummary } from '../types';
import ReactECharts from 'echarts-for-react';
import { Plus, Trash2 } from 'lucide-react';

export default function Portfolio() {
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [form, setForm] = useState({
    good_id: '', market_hash_name: '', quantity: 1, purchase_price: 0,
    purchase_date: '', purchase_platform: 'BUFF', wear: '', notes: '',
  });

  const { data: holdings, isLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: () => api.get<ApiResponse<PortfolioHolding[]>>('/portfolio'),
  });

  const { data: summary } = useQuery({
    queryKey: ['portfolio', 'summary'],
    queryFn: () => api.get<ApiResponse<PortfolioSummary>>('/portfolio/summary'),
  });

  const items = holdings?.data ?? [];
  const s = summary?.data;

  const addMutation = useMutation({
    mutationFn: () => api.post('/portfolio', form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      setShowAddModal(false);
    },
  });

  const removeMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/portfolio/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['portfolio'] }),
  });

  // Pie chart for diversification
  const div = s?.diversification ?? {};
  const pieOption = {
    tooltip: { trigger: 'item' as const },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: Object.entries(div).map(([name, value]) => ({ name, value })),
      label: { color: '#8b95a8' },
    }],
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">持仓管理</h1>
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium hover:opacity-80" style={{ backgroundColor: 'var(--accent-green)', color: '#000' }}>
          <Plus size={14} /> 添加持仓
        </button>
      </div>

      {/* Summary Cards */}
      {s && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard label="总成本" value={`¥${s.total_cost?.toLocaleString()}`} />
          <StatCard label="当前市值" value={s.total_value ? `¥${s.total_value.toLocaleString()}` : 'N/A'} />
          <StatCard label="总盈亏" value={s.total_pnl != null ? `¥${s.total_pnl.toLocaleString()}` : 'N/A'} color={s.total_pnl != null ? (s.total_pnl >= 0 ? 'var(--accent-green)' : 'var(--accent-red)') : undefined} />
          <StatCard label="盈亏率" value={s.total_pnl_pct != null ? `${s.total_pnl_pct}%` : 'N/A'} color={s.total_pnl_pct != null ? (s.total_pnl_pct >= 0 ? 'var(--accent-green)' : 'var(--accent-red)') : undefined} />
        </div>
      )}

      {/* Diversification Pie */}
      {Object.keys(div).length > 0 && (
        <div className="rounded-xl p-4 mb-6" style={{ backgroundColor: 'var(--bg-card)' }}>
          <h2 className="text-lg font-semibold mb-3">持仓分布</h2>
          <ReactECharts option={pieOption} style={{ height: 300 }} />
        </div>
      )}

      {/* Holdings Table */}
      {isLoading ? (
        <p style={{ color: 'var(--text-muted)' }}>加载中...</p>
      ) : items.length === 0 ? (
        <div className="text-center py-20">
          <p style={{ color: 'var(--text-muted)' }}>还没有持仓记录</p>
          <button onClick={() => setShowAddModal(true)} className="font-medium mt-2" style={{ color: 'var(--accent-green)' }}>
            添加第一笔持仓
          </button>
        </div>
      ) : (
        <div className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-hover)' }}>
                <th className="text-left py-3 px-4">名称</th>
                <th className="text-right py-3 px-4">数量</th>
                <th className="text-right py-3 px-4 hidden md:table-cell">买入价</th>
                <th className="text-right py-3 px-4">现价</th>
                <th className="text-right py-3 px-4">盈亏</th>
                <th className="py-3 px-4" />
              </tr>
            </thead>
            <tbody>
              {items.map((h) => (
                <tr key={h.id} className="border-t" style={{ borderColor: 'var(--border-color)' }}>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      {h.image_url && <img src={h.image_url} alt="" className="w-8 h-8 object-contain rounded" />}
                      <span className="truncate max-w-[150px]">{h.item_name || h.market_hash_name}</span>
                    </div>
                  </td>
                  <td className="text-right py-3 px-4">{h.quantity}</td>
                  <td className="text-right py-3 px-4 hidden md:table-cell">¥{h.purchase_price.toFixed(2)}</td>
                  <td className="text-right py-3 px-4">¥{h.current_price?.toFixed(2) ?? 'N/A'}</td>
                  <td className={`text-right py-3 px-4 ${h.pnl != null ? (h.pnl >= 0 ? 'price-up' : 'price-down') : ''}`}>
                    {h.pnl != null ? `¥${h.pnl.toFixed(2)}` : 'N/A'}
                  </td>
                  <td className="py-3 px-4">
                    <button onClick={() => removeMutation.mutate(h.id)} className="p-1 rounded hover:opacity-50">
                      <Trash2 size={14} style={{ color: 'var(--accent-red)' }} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ backgroundColor: 'rgba(0,0,0,0.6)' }} onClick={() => setShowAddModal(false)}>
          <div className="w-full max-w-lg rounded-xl p-6 space-y-4" style={{ backgroundColor: 'var(--bg-secondary)' }} onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold">添加持仓</h2>
            <input type="text" placeholder="饰品 market_hash_name" value={form.market_hash_name} onChange={(e) => setForm({...form, market_hash_name: e.target.value})} className="w-full px-3 py-2 rounded-lg text-sm border" style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }} />
            <input type="text" placeholder="good_id" value={form.good_id} onChange={(e) => setForm({...form, good_id: e.target.value})} className="w-full px-3 py-2 rounded-lg text-sm border" style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }} />
            <div className="grid grid-cols-2 gap-3">
              <input type="number" placeholder="数量" value={form.quantity} onChange={(e) => setForm({...form, quantity: +e.target.value})} className="px-3 py-2 rounded-lg text-sm border" style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }} />
              <input type="number" placeholder="买入单价 (¥)" value={form.purchase_price || ''} onChange={(e) => setForm({...form, purchase_price: +e.target.value})} className="px-3 py-2 rounded-lg text-sm border" style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }} />
            </div>
            <input type="text" placeholder="买入日期 (YYYY-MM-DD)" value={form.purchase_date} onChange={(e) => setForm({...form, purchase_date: e.target.value})} className="w-full px-3 py-2 rounded-lg text-sm border" style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }} />
            <button onClick={() => addMutation.mutate()} className="w-full py-2 rounded-lg text-sm font-medium" style={{ backgroundColor: 'var(--accent-green)', color: '#000' }}>确认添加</button>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--bg-card)' }}>
      <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>{label}</p>
      <p className="text-xl font-bold" style={{ color: color ?? 'var(--text-primary)' }}>{value}</p>
    </div>
  );
}
