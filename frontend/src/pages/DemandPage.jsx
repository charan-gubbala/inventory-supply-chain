import React, { useState, useEffect } from 'react';
import { TrendingUp, Filter, Search, Calendar, RefreshCw, Zap } from 'lucide-react';
import { demandApi, skuApi, locationApi } from '../services/api';

export default function DemandPage() {
  const [demands, setDemands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [skuFilter, setSkuFilter] = useState('');
  const [locFilter, setLocFilter] = useState('');
  const [weekFilter, setWeekFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [skus, setSkus] = useState([]);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    Promise.all([skuApi.list({ limit: 100 }), locationApi.list({ limit: 50 })])
      .then(([skuData, locData]) => {
        setSkus(skuData);
        setLocations(locData);
      })
      .catch(console.error);
  }, []);

  const fetchDemands = async () => {
    try {
      setLoading(true);
      const data = await demandApi.list({
        sku_id: skuFilter || undefined,
        location_id: locFilter || undefined,
        iso_week: weekFilter || undefined,
        demand_type: typeFilter || undefined,
        limit: 200
      });
      setDemands(data);
    } catch (err) {
      console.error('Error fetching demand:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemands();
  }, [skuFilter, locFilter, weekFilter, typeFilter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Customer Demand Forecasts</h1>
          <p className="text-xs text-slate-500 mt-0.5">Time-phased weekly demand projections per SKU and fulfillment facility</p>
        </div>
        <button
          onClick={fetchDemands}
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
          Refresh Demand
        </button>
      </div>

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1">SKU Filter</label>
          <select
            value={skuFilter}
            onChange={(e) => setSkuFilter(e.target.value)}
            className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All SKUs</option>
            {skus.map(s => <option key={s.sku_id} value={s.sku_id}>{s.sku_id} - {s.name}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1">Location Filter</label>
          <select
            value={locFilter}
            onChange={(e) => setLocFilter(e.target.value)}
            className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All Locations</option>
            {locations.map(l => <option key={l.location_id} value={l.location_id}>{l.location_id} - {l.name}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1">ISO Week</label>
          <input
            type="text"
            placeholder="e.g. 2026W01"
            value={weekFilter}
            onChange={(e) => setWeekFilter(e.target.value)}
            className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs"
          />
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-500 mb-1">Demand Driver Type</label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All Driver Types</option>
            <option value="BASELINE">Baseline Demand</option>
            <option value="SEASONAL">Seasonal Peak</option>
            <option value="SPIKE">Demand Spike</option>
            <option value="PROMOTION">Promotional Lift</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Demand ID</th>
                <th className="px-4 py-3">SKU ID</th>
                <th className="px-4 py-3">Destination Facility</th>
                <th className="px-4 py-3">Planning Week</th>
                <th className="px-4 py-3 text-right">Forecast Quantity</th>
                <th className="px-4 py-3">Demand Pattern</th>
                <th className="px-4 py-3">Forecast Date</th>
                <th className="px-4 py-3 text-right">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">Loading demand forecast...</td>
                </tr>
              ) : demands.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">No demand records found for filters.</td>
                </tr>
              ) : (
                demands.map((d) => (
                  <tr key={d.demand_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-500">{d.demand_id}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-slate-900">{d.sku_id}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{d.location_id}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-sky-700">{d.iso_week}</td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-slate-900">{d.forecast_quantity.toLocaleString()} units</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        d.demand_type === 'SPIKE'
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : (d.demand_type === 'SEASONAL' ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-slate-100 text-slate-700')
                      }`}>
                        {d.demand_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{d.forecast_date}</td>
                    <td className="px-4 py-3 text-right font-mono text-emerald-700 font-semibold">{d.confidence_level}%</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
