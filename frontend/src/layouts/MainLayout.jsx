import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  MapPin,
  TrendingUp,
  Boxes,
  Truck,
  ShoppingCart,
  Factory,
  AlertTriangle,
  ShieldCheck,
  FileWarning,
  Database,
  RefreshCw,
  Layers,
  ChevronRight,
  Activity
} from 'lucide-react';

const navigationItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'SKU Management', path: '/skus', icon: Package },
  { name: 'Location Facilities', path: '/locations', icon: MapPin },
  { name: 'Demand Planning', path: '/demand', icon: TrendingUp },
  { name: 'Inventory Balances', path: '/inventory', icon: Boxes },
  { name: 'Supplier Network', path: '/suppliers', icon: Truck },
  { name: 'Purchase Orders', path: '/purchase-orders', icon: ShoppingCart },
  { name: 'Production Plans', path: '/production', icon: Factory },
  { name: 'Shortage Control', path: '/shortages', icon: AlertTriangle, badge: 'Active' },
  { name: 'Mitigation Engine', path: '/mitigations', icon: ShieldCheck },
  { name: 'Exception Scenarios', path: '/exceptions', icon: FileWarning },
  { name: 'Data Ops & Validation', path: '/data-ops', icon: Database },
];

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const currentNav = navigationItems.find(item => item.path === location.pathname) || { name: 'Overview' };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Sidebar */}
      <aside className={`${collapsed ? 'w-20' : 'w-64'} bg-slate-900 text-slate-300 flex flex-col transition-all duration-200 z-20 shadow-xl border-r border-slate-800`}>
        {/* Brand header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 rounded-lg bg-sky-500 flex items-center justify-center text-white font-bold shrink-0 shadow-md shadow-sky-500/20">
              <Layers className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <div>
                <h1 className="text-sm font-bold tracking-tight text-white leading-none">SupplyChainIQ</h1>
                <span className="text-[11px] text-sky-400 font-medium">Enterprise Planner</span>
              </div>
            )}
          </div>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-sky-600 text-white font-semibold shadow-sm'
                      : 'text-slate-400 hover:bg-slate-800/80 hover:text-slate-200'
                  }`
                }
              >
                <Icon className={`w-4 h-4 shrink-0 ${collapsed ? 'mx-auto' : 'mr-3'}`} />
                {!collapsed && (
                  <span className="flex-1 truncate">{item.name}</span>
                )}
                {!collapsed && item.badge && (
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Sidebar footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-[11px] text-slate-500">
          {!collapsed ? (
            <div className="flex items-center justify-between">
              <span className="truncate">Production Plan v1.0</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
          ) : (
            <div className="flex justify-center">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            </div>
          )}
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-10">
          <div className="flex items-center space-x-3">
            <h2 className="text-base font-semibold text-slate-800">{currentNav.name}</h2>
            <ChevronRight className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-500">Planning Horizon 2026</span>
          </div>

          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              <Activity className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-medium">System Online</span>
            </div>
            <div className="text-slate-500 border-l border-slate-200 pl-4">
              Database: <span className="font-semibold text-slate-700">Connected</span>
            </div>
          </div>
        </header>

        {/* Page Container */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
