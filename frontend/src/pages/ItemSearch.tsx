import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, ItemSearchResult } from '../types';
import { useNavigate } from 'react-router-dom';

export default function ItemSearch() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounce search input by 300ms
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  const { data, isLoading } = useQuery({
    queryKey: ['items', 'search', debouncedQuery],
    queryFn: () => api.get<ApiResponse<ItemSearchResult[]>>(`/items/search?q=${encodeURIComponent(debouncedQuery)}&limit=20`),
    enabled: debouncedQuery.length > 0,
  });

  const items = data?.data ?? [];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">饰品搜索</h1>

      {/* Search Input */}
      <div className="mb-6">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索饰品名称，如 AK-47, AWP, M4A1-S, 爪子刀..."
          className="w-full max-w-xl px-4 py-3 rounded-xl text-base outline-none border border-border bg-card text-text placeholder-muted-text focus:border-brand focus:ring-1 focus:ring-brand transition-all duration-200"
          autoFocus
        />
      </div>

      {/* Results */}
      {isLoading && <p className="text-muted-text">搜索中...</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {items.map((item) => (
          <div
            key={item.good_id}
            onClick={() => navigate(`/items/${item.good_id}`)}
            className="flex items-center gap-3 rounded-lg p-3 bg-card cursor-pointer hover:bg-hover transition-all duration-200"
          >
            {item.image_url && (
              <img src={item.image_url} alt={item.name} className="w-16 h-16 object-contain rounded" loading="lazy" />
            )}
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{item.name}</p>
              <p className="text-xs truncate text-muted-text">{item.market_hash_name}</p>
            </div>
          </div>
        ))}
      </div>

      {!isLoading && debouncedQuery && items.length === 0 && (
        <p className="text-muted-text">没有找到匹配的饰品</p>
      )}
    </div>
  );
}
