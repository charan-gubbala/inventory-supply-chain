import React, { useState, useEffect } from 'react';
import { Boxes, Filter, RefreshCw, AlertCircle } from 'lucide-react';
import { inventoryApi, skuApi, locationApi } from '../services/api';

export default function InventoryPage() {
  const [inventories, setInventories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [skuFilter, setSkuFilter] = useState('');
  const [locFilter, setLocFilter] = useState('');
  const [shortageOnly, setShortageOnly] = useState(false);
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

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const data = await inventoryApi.list({
        sku_id: skuFilter || undefined,
        location_id: locFilter || undefined,
        shortage_only: shortageOnly || undefined,
        limit: 200
      });
      setInventories(data);
    } catch (err) {
      console.error('Error fetching inventory balances:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, [skuFilter, locFilter, shortageOnly]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Time-Phased Inventory Balances</h1>
          <p className="text-xs text-slate-500 mt-0.5">Week-by-week stock reconciliation, incoming pipeline, and projected available balances</p>
        </div>
        <button
          onClick={fetchInventory}
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
          Reconcile Now
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <select
            value={skuFilter}
            onChange={(e) => setSkuFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All SKUs</option>
            {skus.map(s => <option key={s.sku_id} value={s.sku_id}>{s.sku_id} - {s.name}</option>)}
          </select>

          <select
            value={locFilter}
            onChange={(e) => setLocFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All Locations</option>
            {locations.map(l => <option key={l.location_id} value={l.location_id}>{l.location_id} - {l.name}</option>)}
          </select>

          <label className="inline-flex items-center space-x-2 text-xs font-medium text-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={shortageOnly}
              onChange={(e) => setShortageOnly(e.target.checked)}
              className="rounded border-slate-300 text-rose-600 focus:ring-rose-500"
            />
            <span className="text-rose-700 font-semibold">Negative Balances Only (PAB &lt; 0)</span>
          </label>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Inventory Record</th>
                <th className="px-4 py-3">SKU ID</th>
                <th className="px-4 py-3">Facility</th>
                <th className="px-4 py-3">Week</th>
                <th className="px-4 py-3 text-right">Opening</th>
                <th className="px-4 py-3 text-right">Received</th>
                <th className="px-4 py-3 text-right">Reserved</th>
                <th className="px-4 py-3 text-right">Available</th>
                <th className="px-4 py-3 text-right">Incoming</th>
                <th className="px-4 py-3 text-right">Closing</th>
                <th className="px-4 py-3 text-right">Projected Balance (PAB)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan="11" className="text-center py-10 text-slate-400">Reconciling inventory balances...</td>
                </tr>
              ) : inventories.length === 0 ? (
                <tr>
                  <td colSpan="11" className="text-center py-10 text-slate-400">No inventory balances found.</td>
                </tr>
              ) : (
                inventories.map((inv) => {
                  const isNegative = inv.projected_available_balance < 0;
                  return (
                    <tr key={inv.inventory_id} className={`hover:bg-slate-50/60 transition-colors ${isNegative ? 'bg-rose-50/30' : ''}`}>
                      <td className="px-4 py-3 font-mono text-[11px] text-slate-400">{inv.inventory_id}</td>
                      <td className="px-4 py-3 font-mono font-semibold text-slate-900">{inv.sku_id}</td>
                      <td className="px-4 py-3 font-medium text-slate-800">{inv.location_id}</td>
                      <td className="px-4 py-3 font-mono text-sky-700 font-semibold">{inv.iso_week}</td>
                      <td className="px-4 py-3 text-right font-mono">{inv.opening_stock}</td>
                      <td className="px-4 py-3 text-right font-mono text-emerald-600 font-medium">+{inv.received_stock}</td>
                      <td className="px-4 py-3 text-right font-mono text-amber-600">-{inv.reserved_stock}</td>
                      <td className="px-4 py-3 text-right font-mono font-semibold text-slate-800">{inv.available_stock}</td>
                      <td className="px-4 py-3 text-right font-mono text-sky-600 font-medium">+{inv.incoming_stock}</td>
                      <td className="px-4 py-3 text-right font-mono font-semibold">{inv.closing_stock}</td>
                      <td className="px-4 py-3 text-right font-mono">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded font-bold text-xs ${
                          isNegative ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-50 text-emerald-800'
                        }`}>
                          {isNegative && <AlertCircle className="w-3.5 h-3.5 mr-1 text-rose-600" />}
                          {inv.projected_available_balance}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
