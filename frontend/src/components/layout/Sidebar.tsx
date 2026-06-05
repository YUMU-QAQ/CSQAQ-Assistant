import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Search, TrendingUp, Star, Wallet, Bell, ArrowLeftRight, Box, Bot } from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: '数据看板' },
  { to: '/items', icon: Search, label: '饰品搜索' },
  { to: '/rankings', icon: TrendingUp, label: '排行榜' },
  { to: '/watchlist', icon: Star, label: '关注列表' },
  { to: '/portfolio', icon: Wallet, label: '持仓管理' },
  { to: '/alerts', icon: Bell, label: '价格提醒' },
  { to: '/arbitrage', icon: ArrowLeftRight, label: '挂刀分析' },
  { to: '/cases', icon: Box, label: '武器箱' },
  { to: '/ai', icon: Bot, label: 'AI 助手' },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-56 flex flex-col border-r z-40" style={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }}>
      {/* Logo */}
      <div className="h-14 flex items-center px-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
        <span className="text-lg font-bold" style={{ color: 'var(--accent-green)' }}>CSQAQ</span>
        <span className="text-sm ml-2" style={{ color: 'var(--text-secondary)' }}>Assistant</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'font-medium'
                  : 'hover:bg-opacity-50'
              }`
            }
            style={({ isActive }) => ({
              backgroundColor: isActive ? 'var(--bg-hover)' : 'transparent',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
            })}
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
