import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function MainLayout() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="ml-56 flex-1 p-6 overflow-auto" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <Outlet />
      </main>
    </div>
  );
}
