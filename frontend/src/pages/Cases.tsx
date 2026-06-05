import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, CaseListItem } from '../types';

export default function Cases() {
  const { data, isLoading } = useQuery({
    queryKey: ['cases', 'list'],
    queryFn: () => api.get<ApiResponse<CaseListItem[]>>('/cases/list?sort=roi'),
  });

  const cases = data?.data ?? [];
  const casesList = Array.isArray(cases) ? cases : [];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">武器箱分析</h1>

      {isLoading ? (
        <p style={{ color: 'var(--text-muted)' }}>加载中...</p>
      ) : (
        <div className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-hover)' }}>
                <th className="text-left py-3 px-4">名称</th>
                <th className="text-right py-3 px-4">箱子价格</th>
                <th className="text-right py-3 px-4">期望值</th>
                <th className="text-right py-3 px-4">ROI</th>
                <th className="text-right py-3 px-4 hidden md:table-cell">24h开箱数</th>
              </tr>
            </thead>
            <tbody>
              {casesList.map((c: any) => (
                <tr
                  key={c.case_id ?? c.name}
                  className="border-t cursor-pointer hover:bg-opacity-50"
                  style={{ borderColor: 'var(--border-color)' }}
                  onClick={() => window.location.href = `/items/${c.case_id}`}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      {c.image_url && <img src={c.image_url} alt="" className="w-8 h-8 object-contain rounded" />}
                      <span>{c.name ?? 'N/A'}</span>
                    </div>
                  </td>
                  <td className="text-right py-3 px-4">¥{c.price?.toFixed(2) ?? 'N/A'}</td>
                  <td className="text-right py-3 px-4">¥{c.expected_value?.toFixed(2) ?? 'N/A'}</td>
                  <td className={`text-right py-3 px-4 font-medium ${c.roi_pct >= 0 ? 'price-up' : 'price-down'}`}>
                    {c.roi_pct != null ? `${c.roi_pct >= 0 ? '+' : ''}${c.roi_pct}%` : 'N/A'}
                  </td>
                  <td className="text-right py-3 px-4 hidden md:table-cell" style={{ color: 'var(--text-secondary)' }}>
                    {c.open_count_24h?.toLocaleString() ?? 'N/A'}
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
