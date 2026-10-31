import React, { useState, useEffect } from 'react';
import {
  Boxes,
  TrendingUp,
  AlertTriangle,
  Truck,
  CheckCircle2,
  Clock,
  Layers,
  MapPin,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { dashboardApi } from '../services/api';

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [inventoryTrend, setInventoryTrend] = useState([]);
  const [shortageTrend, setShortageTrend] = useState([]);
  const [supplierPerf, setSupplierPerf] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [sumRes, invRes, shortRes, supRes] = await Promise.all([
        dashboardApi.getSummary(),
        dashboardApi.getInventoryTrend(),
        dashboardApi.getShortageTrend(),
        dashboardApi.getSupplierPerformance()
      ]);
      setSummary(sumRes);
      setInventoryTrend(invRes);
      setShortageTrend(shortRes);
      setSupplierPerf(supRes);
      setError(null);
    } catch (err) {
      console.error('Dashboard load error:', err);
      setError('Failed to load dashboard metrics. Ensure backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <RefreshCw className="w-8 h-8 text-sky-600 animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Computing live supply chain metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-rose-600" />
          <h3 className="font-semibold text-sm">System Error</h3>
        </div>
        <p className="text-xs mt-2">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-4 px-3 py-1.5 bg-rose-600 text-white text-xs font-semibold rounded-lg hover:bg-rose-700"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Supply Chain Operations Overview</h1>
          <p className="text-xs text-slate-500 mt-0.5">Real-time demand vs. supply reconciliation and shortage diagnostics</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
          Refresh Metrics
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Total Available Stock</span>
            <Boxes className="w-4 h-4 text-sky-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{summary?.total_inventory?.toLocaleString() || 0}</span>
            <span className="text-[11px] font-medium text-slate-400">Units</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Across {summary?.total_locations} Locations</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Forecast Demand</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{summary?.total_forecast_demand?.toLocaleString() || 0}</span>
            <span className="text-[11px] font-medium text-slate-400">Demand</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">{summary?.total_skus} Active SKUs</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Active Shortages</span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-rose-600">{summary?.total_shortages || 0}</span>
            <span className="text-[11px] font-semibold text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded">
              {summary?.critical_shortages || 0} Critical
            </span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Projected stockouts</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Supplier Capacity Util.</span>
            <Truck className="w-4 h-4 text-amber-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{summary?.supplier_capacity_utilization_pct || 0}%</span>
            <span className="text-[11px] font-medium text-slate-400">Utilized</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">{summary?.total_suppliers} Active Vendors</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Mitigation Rate</span>
            <CheckCircle2 className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-indigo-600">{summary?.mitigation_success_rate_pct || 0}%</span>
            <span className="text-[11px] font-medium text-slate-400">Approved</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">{summary?.pending_purchase_orders} Pending Inbound POs</div>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Demand vs Inventory Balance Trend */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">Time-Phased Inventory vs. Demand</h3>
              <p className="text-[11px] text-slate-500">Comparison of aggregate weekly demand and physical available stock</p>
            </div>
            <span className="text-xs font-medium px-2 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200">Weekly</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={inventoryTrend}>
                <defs>
                  <linearGradient id="colorInv" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorDem" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="iso_week" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="total_inventory" name="Available Stock" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorInv)" strokeWidth={2} />
                <Area type="monotone" dataKey="total_demand" name="Forecast Demand" stroke="#ef4444" fillOpacity={1} fill="url(#colorDem)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Shortages by Week */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">Shortage Deficit Volumes</h3>
              <p className="text-[11px] text-slate-500">Unmet quantity volume and critical shortage occurrences</p>
            </div>
            <span className="text-xs font-medium px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">Deficit</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={shortageTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="iso_week" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="total_shortage_quantity" name="Deficit Quantity" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="critical_count" name="Critical Incidents" fill="#881337" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Supplier Performance Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-800">Supplier Reliability & Capacity Utilization</h3>
            <p className="text-[11px] text-slate-500">Track vendor delivery reliability and contracted volume utilization</p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Supplier ID</th>
                <th className="px-4 py-3">Company Name</th>
                <th className="px-4 py-3">Rating</th>
                <th className="px-4 py-3">On-Time Delivery</th>
                <th className="px-4 py-3">Allocated / Max Capacity</th>
                <th className="px-4 py-3">Utilization</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {supplierPerf.map((sup) => (
                <tr key={sup.supplier_id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-4 py-3 font-mono font-medium text-slate-900">{sup.supplier_id}</td>
                  <td className="px-4 py-3 font-medium text-slate-800">{sup.supplier_name}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center font-semibold text-amber-600">
                      ★ {sup.rating.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                      sup.on_time_delivery_rate >= 95 ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                    }`}>
                      {sup.on_time_delivery_rate.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {sup.allocated_capacity.toLocaleString()} / {sup.max_capacity.toLocaleString()} units
                  </td>
                  <td className="px-4 py-3 w-48">
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-slate-200 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            sup.utilization_pct > 90 ? 'bg-rose-500' : (sup.utilization_pct > 70 ? 'bg-amber-500' : 'bg-sky-500')
                          }`}
                          style={{ width: `${Math.min(100, sup.utilization_pct)}%` }}
                        />
                      </div>
                      <span className="text-[11px] font-medium text-slate-600 w-10 text-right">{sup.utilization_pct}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
