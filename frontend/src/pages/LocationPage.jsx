import React, { useState, useEffect } from 'react';
import { MapPin, Building2, Factory, Warehouse, RefreshCw } from 'lucide-react';
import { locationApi } from '../services/api';

export default function LocationPage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('');

  const fetchLocations = async () => {
    try {
      setLoading(true);
      const data = await locationApi.list({ type: typeFilter || undefined });
      setLocations(data);
    } catch (err) {
      console.error('Error fetching locations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocations();
  }, [typeFilter]);

  const getLocationIcon = (type) => {
    if (type === 'PLANT') return <Factory className="w-5 h-5 text-indigo-600" />;
    if (type === 'DISTRIBUTION_CENTER') return <Building2 className="w-5 h-5 text-sky-600" />;
    return <Warehouse className="w-5 h-5 text-emerald-600" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Facility Network & Storage Locations</h1>
          <p className="text-xs text-slate-500 mt-0.5">Physical manufacturing plants, distribution hubs, and warehouses</p>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All Facility Types</option>
            <option value="PLANT">Manufacturing Plants</option>
            <option value="DISTRIBUTION_CENTER">Distribution Centers</option>
            <option value="WAREHOUSE">Warehouses</option>
          </select>
          <button
            onClick={fetchLocations}
            className="p-1.5 text-slate-500 hover:text-slate-800 border border-slate-300 rounded-lg bg-white"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Grid of Locations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-3 text-center py-12 text-slate-400 text-xs">Loading facilities...</div>
        ) : locations.map((loc) => (
          <div key={loc.location_id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between">
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  {getLocationIcon(loc.type)}
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {loc.status}
                </span>
              </div>
              <div className="mt-3">
                <span className="font-mono text-xs text-slate-400 font-semibold">{loc.location_id}</span>
                <h3 className="text-sm font-bold text-slate-800 mt-0.5">{loc.name}</h3>
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">{loc.type.replace('_', ' ')}</span>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Storage Capacity:</span>
                  <span className="font-mono font-semibold text-slate-900">{loc.capacity_units.toLocaleString()} units</span>
                </div>
                <div className="text-[11px] text-slate-400 truncate">
                  {loc.address || 'Standard fulfillment territory'}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
