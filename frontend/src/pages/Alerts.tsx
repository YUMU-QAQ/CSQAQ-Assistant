import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, PriceAlert } from '../types';
import { Plus, Trash2, BellOff, Bell } from 'lucide-react';

export default function Alerts() {
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ good_id: '', market_hash_name: '', alert_type: 'price_above', threshold_value: 0, platform: 'BUFF' });

  const { data } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.get<ApiResponse<PriceAlert[]>>('/alerts'),
    refetchInterval: 30000,
  });

  const alerts = data?.data ?? [];

  const addMutation = useMutation({
    mutationFn: () => api.post('/alerts', form),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['alerts'] }); setShowAdd(false); },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: number }) =>
      api.patch(`/alerts/${id}`, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  const removeMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/alerts/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  const typeLabels: Record<string, string> = {
    price_above: '价格高于',
    price_below: '价格低于',
    pct_change_up: '涨幅超过',
    pct_change_down: '跌幅超过',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">价格提醒</h1>
        <button onClick={() => setShowAdd(true)} className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium bg-brand text-black hover:opacity-90 transition-all duration-200">
          <Plus size={14} /> 添加提醒
        </button>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-muted-text">还没有价格提醒</p>
          <button onClick={() => setShowAdd(true)} className="font-medium mt-2 text-brand hover:opacity-80 transition-opacity">创建第一个提醒</button>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={alert.id} className="rounded-xl p-4 bg-card flex items-center justify-between hover:bg-hover transition-colors duration-200">
              <div>
                <p className="font-medium">{alert.market_hash_name}</p>
                <p className="text-sm mt-1 text-secondary-text">
                  {typeLabels[alert.alert_type] ?? alert.alert_type} ¥{alert.threshold_value.toFixed(2)}
                  {alert.triggered_at && (
                    <span className="ml-2 px-2 py-0.5 rounded text-xs bg-danger text-white">
                      已触发
                    </span>
                  )}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleMutation.mutate({ id: alert.id, is_active: alert.is_active ? 0 : 1 })}
                  className="p-2 rounded-lg bg-hover hover:opacity-80 transition-opacity"
                  aria-label={alert.is_active ? '禁用提醒' : '启用提醒'}
                >
                  {alert.is_active ? <Bell size={16} className="text-brand" /> : <BellOff size={16} className="text-muted-text" />}
                </button>
                <button
                  onClick={() => removeMutation.mutate(alert.id)}
                  className="p-2 rounded-lg bg-hover hover:opacity-80 transition-opacity"
                  aria-label="删除提醒"
                >
                  <Trash2 size={16} className="text-danger" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={() => setShowAdd(false)}>
          <div className="w-full max-w-md rounded-xl p-6 space-y-4 bg-secondary shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold">添加价格提醒</h2>
            <input type="text" placeholder="饰品 market_hash_name" value={form.market_hash_name} onChange={(e) => setForm({...form, market_hash_name: e.target.value})} className="w-full px-3 py-2 rounded-lg text-sm border border-border bg-card text-text placeholder-muted-text focus:border-brand focus:ring-1 focus:ring-brand transition-all duration-200 outline-none" />
            <input type="text" placeholder="good_id" value={form.good_id} onChange={(e) => setForm({...form, good_id: e.target.value})} className="w-full px-3 py-2 rounded-lg text-sm border border-border bg-card text-text placeholder-muted-text focus:border-brand focus:ring-1 focus:ring-brand transition-all duration-200 outline-none" />
            <select value={form.alert_type} onChange={(e) => setForm({...form, alert_type: e.target.value})} className="w-full px-3 py-2 rounded-lg text-sm border border-border bg-card text-text focus:border-brand focus:ring-1 focus:ring-brand transition-all duration-200 outline-none">
              <option value="price_above">价格高于</option>
              <option value="price_below">价格低于</option>
              <option value="pct_change_up">涨幅超过</option>
              <option value="pct_change_down">跌幅超过</option>
            </select>
            <input type="number" placeholder="阈值" value={form.threshold_value || ''} onChange={(e) => setForm({...form, threshold_value: +e.target.value})} className="w-full px-3 py-2 rounded-lg text-sm border border-border bg-card text-text placeholder-muted-text focus:border-brand focus:ring-1 focus:ring-brand transition-all duration-200 outline-none" />
            <button onClick={() => addMutation.mutate()} className="w-full py-2 rounded-lg text-sm font-medium bg-brand text-black hover:opacity-90 transition-all duration-200">确认添加</button>
          </div>
        </div>
      )}
    </div>
  );
}
