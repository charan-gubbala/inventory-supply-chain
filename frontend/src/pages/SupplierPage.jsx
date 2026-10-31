import React, { useState, useEffect } from 'react';
import { Truck, Star, Clock, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import { supplierApi } from '../services/api';

export default function SupplierPage() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [capacities, setCapacities] = useState([]);
  const [leadTimes, setLeadTimes] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      const data = await supplierApi.list({ limit: 50 });
      setSuppliers(data);
    } catch (err) {
      console.error('Error fetching suppliers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const openSupplierDrawer = async (sup) => {
    setSelectedSupplier(sup);
    try {
      const [caps, lts] = await Promise.all([
        supplierApi.getCapacities(sup.supplier_id),
        supplierApi.getLeadTimes(sup.supplier_id)
      ]);
      setCapacities(caps);
      setLeadTimes(lts);
      setDrawerOpen(true);
    } catch (err) {
      console.error('Error loading supplier details:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Supplier Network & Sourcing Capabilities</h1>
          <p className="text-xs text-slate-500 mt-0.5">Vendor capacity constraints, contracted lead times, minimum order quantities, and ratings</p>
        </div>
        <button
          onClick={fetchSuppliers}
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
          Refresh Network
        </button>
      </div>

      {/* Supplier Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-3 text-center py-12 text-slate-400 text-xs">Loading suppliers...</div>
        ) : suppliers.map((sup) => (
          <div key={sup.supplier_id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-xs text-slate-400 font-semibold">{sup.supplier_id}</span>
                  <h3 className="text-sm font-bold text-slate-800 mt-0.5">{sup.name}</h3>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {sup.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-slate-100 text-xs">
                <div>
                  <span className="text-[11px] text-slate-500">Quality Rating:</span>
                  <div className="flex items-center space-x-1 mt-0.5 font-bold text-amber-600">
                    <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
                    <span>{sup.rating.toFixed(1)} / 5.0</span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] text-slate-500">On-Time Delivery:</span>
                  <div className="mt-0.5 font-bold text-emerald-700">
                    {sup.on_time_delivery_rate.toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="mt-3 text-[11px] text-slate-500 truncate">
                {sup.contact_email || 'procurement@partner.com'}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100">
              <button
                onClick={() => openSupplierDrawer(sup)}
                className="w-full py-1.5 bg-slate-50 hover:bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold border border-slate-200 transition-colors"
              >
                Inspect Capacities & Lead Times
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Details Drawer */}
      {drawerOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex justify-end z-50">
          <div className="bg-white w-full max-w-xl h-full shadow-2xl p-6 overflow-y-auto flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div>
                  <span className="font-mono text-xs text-sky-600 font-semibold">{selectedSupplier?.supplier_id}</span>
                  <h2 className="text-base font-bold text-slate-900">{selectedSupplier?.name}</h2>
                </div>
                <button onClick={() => setDrawerOpen(false)} className="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
              </div>

              {/* Capacities Section */}
              <div className="mt-6">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Weekly SKU Production Capacity</h4>
                <div className="mt-3 space-y-2.5">
                  {capacities.length === 0 ? (
                    <p className="text-xs text-slate-400">No active capacity limits configured.</p>
                  ) : capacities.map((cap) => (
                    <div key={cap.capacity_id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                      <div className="flex justify-between font-semibold">
                        <span className="font-mono text-slate-900">{cap.sku_id}</span>
                        <span className="text-slate-600">{cap.available_capacity} units available</span>
                      </div>
                      <div className="mt-1 flex justify-between text-[11px] text-slate-500">
                        <span>Max: {cap.max_capacity_per_week} units/wk</span>
                        <span>Allocated: {cap.allocated_capacity} units</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Lead Times Section */}
              <div className="mt-6">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Lead Times & Minimum Order Quantities (MOQ)</h4>
                <div className="mt-3 space-y-2.5">
                  {leadTimes.length === 0 ? (
                    <p className="text-xs text-slate-400">No lead-time lanes active.</p>
                  ) : leadTimes.map((lt) => (
                    <div key={lt.lead_time_id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs flex justify-between items-center">
                      <div>
                        <div className="font-mono font-semibold text-slate-800">{lt.sku_id} → {lt.location_id}</div>
                        <div className="text-[11px] text-slate-500">Base Lead Time: {lt.base_lead_time_days} days</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-slate-900">MOQ: {lt.min_order_quantity}</div>
                        <div className="text-[11px] text-slate-500">${lt.cost_per_unit}/unit</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200">
              <button
                onClick={() => setDrawerOpen(false)}
                className="w-full py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-900"
              >
                Close Profile
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
