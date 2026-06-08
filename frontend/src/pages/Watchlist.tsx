import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { useNavigate } from 'react-router-dom';
import type { ApiResponse, WatchlistItem } from '../types';
import { Plus, Trash2, RefreshCw } from 'lucide-react';

export default function Watchlist() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const { data, isLoading } = useQuery({
    queryKey: ['watchlist'],
    queryFn: () => api.get<ApiResponse<WatchlistItem[]>>('/watchlist'),
    refetchInterval: 60000,
  });

  const items = data?.data ?? [];

  // Search items to add
  const handleSearch = async () => {
    if (!searchQuery) return;
    const res = await api.get<ApiResponse<any[]>>(`/items/search?q=${encodeURIComponent(searchQuery)}&limit=10`);
    setSearchResults(res.data ?? []);
  };

  const addMutation = useMutation({
    mutationFn: (item: any) => api.post('/watchlist', {
      good_id: String(item.good_id),
      market_hash_name: item.market_hash_name,
      item_name: item.name,
      image_url: item.image_url,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
      setShowAddModal(false);
      setSearchQuery('');
      setSearchResults([]);
    },
  });

  const removeMutation = useMutation({
    mutationFn: (goodId: string) => api.delete(`/watchlist/${goodId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlist'] }),
  });

  const refreshMutation = useMutation({
    mutationFn: () => api.post('/watchlist/refresh'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlist'] }),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">关注列表</h1>
        <div className="flex gap-2">
          <button
            onClick={() => refreshMutation.mutate()}
            className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm bg-card hover:bg-hover transition-all duration-200"
          >
            <RefreshCw size={14} /> 刷新
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium bg-brand text-black hover:opacity-90 transition-all duration-200"
          >
            <Plus size={14} /> 添加
          </button>
        </div>
      </div>

      {/* Grid */}
      {isLoading ? (
        <p className="text-muted-text">加载中...</p>
      ) : items.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-muted-text mb-2">还没有关注任何饰品</p>
          <button onClick={() => setShowAddModal(true)} className="font-medium text-brand hover:opacity-80 transition-opacity">
            添加第一个关注
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="rounded-lg p-4 bg-card relative group cursor-pointer hover:bg-hover transition-all duration-200"
              onClick={() => navigate(`/items/${item.good_id}`)}
            >
              <div className="flex items-center gap-3">
                {item.image_url && (
                  <img src={item.image_url} alt={item.item_name ?? ''} className="w-14 h-14 object-contain rounded" />
                )}
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate">{item.item_name || item.market_hash_name}</p>
                  <p className="text-lg font-bold mt-1">
                    ¥{item.last_price?.toFixed(2) ?? 'N/A'}
                  </p>
                  {item.change_pct_24h != null && (
                    <span className={`text-xs ${item.change_pct_24h >= 0 ? 'price-up' : 'price-down'}`}>
                      {item.change_pct_24h >= 0 ? '+' : ''}{item.change_pct_24h}%
                    </span>
                  )}
                </div>
              </div>
              {/* Remove button */}
              <button
                onClick={(e) => { e.stopPropagation(); removeMutation.mutate(item.good_id); }}
                className="absolute top-2 right-2 p-1.5 rounded bg-hover opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-danger/20"
                aria-label="删除关注"
              >
                <Trash2 size={14} className="text-danger" />
              </button>
              {/* Tags */}
              {item.tags.length > 0 && (
                <div className="flex gap-1 mt-2 flex-wrap">
                  {item.tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 rounded text-xs bg-hover text-info">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={() => setShowAddModal(false)}>
          <div className="w-full max-w-md rounded-xl p-6 bg-secondary shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold mb-4">添加关注</h2>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="搜索饰品..."
                className="flex-1 px-3 py-2 rounded-lg text-sm outline-none border border-border bg-card text-text placeholder-muted-text focus:border-brand focus:ring-1 focus:ring-brand transition-all duration-200"
              />
              <button onClick={handleSearch} className="px-4 py-2 rounded-lg text-sm bg-brand text-black hover:opacity-90 transition-all duration-200">
                搜索
              </button>
            </div>
            <div className="max-h-60 overflow-y-auto space-y-1">
              {searchResults.map((r) => (
                <div
                  key={r.good_id}
                  onClick={() => addMutation.mutate(r)}
                  className="flex items-center gap-2 p-2 rounded bg-card cursor-pointer hover:bg-hover transition-all duration-200"
                >
                  {r.image_url && <img src={r.image_url} alt="" className="w-8 h-8 object-contain rounded" />}
                  <span className="text-sm truncate">{r.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
