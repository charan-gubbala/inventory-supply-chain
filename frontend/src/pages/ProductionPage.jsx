import React, { useState, useEffect } from 'react';
import { Factory, Calendar, Clock, Layers, Plus, RefreshCw } from 'lucide-react';
import { productionApi, skuApi, locationApi } from '../services/api';

export default function ProductionPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [skus, setSkus] = useState([]);
  const [plants, setPlants] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    sku_id: '',
    location_id: '',
    iso_week: '2026W02',
    planned_quantity: 200,
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 5 * 86400000).toISOString().split('T')[0]
  });

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const data = await productionApi.list({ limit: 100 });
      setPlans(data);
    } catch (err) {
      console.error('Error fetching production plans:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
    Promise.all([skuApi.list({ limit: 100 }), locationApi.list({ type: 'PLANT' })])
      .then(([skuData, plantData]) => {
        setSkus(skuData);
        setPlants(plantData);
        if (skuData.length > 0 && plantData.length > 0) {
          setFormData(prev => ({
            ...prev,
            sku_id: skuData[0].sku_id,
            location_id: plantData[0].location_id
          }));
        }
      })
      .catch(console.error);
  }, []);

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    try {
      await productionApi.create(formData);
      setModalOpen(false);
      fetchPlans();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create production plan');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Production Scheduling & BOM Manufacturing</h1>
          <p className="text-xs text-slate-500 mt-0.5">Internal assembly plans, machine hours allocation, and raw material availability</p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-sky-600 rounded-lg shadow-sm hover:bg-sky-700"
        >
          <Plus className="w-3.5 h-3.5 mr-1" />
          Schedule Production
        </button>
      </div>

      {/* Production Plans Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Plan ID</th>
                <th className="px-4 py-3">Manufactured SKU</th>
                <th className="px-4 py-3">Plant Facility</th>
                <th className="px-4 py-3">Target Week</th>
                <th className="px-4 py-3 text-right">Planned Quantity</th>
                <th className="px-4 py-3 text-right">Produced Quantity</th>
                <th className="px-4 py-3">Start Date</th>
                <th className="px-4 py-3">Completion Date</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan="9" className="text-center py-10 text-slate-400">Loading production plans...</td>
                </tr>
              ) : plans.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-10 text-slate-400">No scheduled production plans. Click 'Schedule Production' to create one.</td>
                </tr>
              ) : (
                plans.map((p) => (
                  <tr key={p.plan_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3 font-mono font-semibold text-slate-900">{p.plan_id}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-sky-800">{p.sku_id}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{p.location_id}</td>
                    <td className="px-4 py-3 font-mono text-sky-700 font-semibold">{p.iso_week}</td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-slate-900">{p.planned_quantity.toLocaleString()} units</td>
                    <td className="px-4 py-3 text-right font-mono text-emerald-700">{p.produced_quantity.toLocaleString()} units</td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{p.start_date}</td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{p.end_date}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-50 text-sky-700 border border-sky-200">
                        {p.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreatePlan} className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200 text-xs">
            <h3 className="font-bold text-sm text-slate-900 mb-4">Schedule Production Assembly</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Finished SKU</label>
                <select
                  value={formData.sku_id}
                  onChange={(e) => setFormData({ ...formData, sku_id: e.target.value })}
                  className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white"
                  required
                >
                  {skus.map(s => <option key={s.sku_id} value={s.sku_id}>{s.sku_id} - {s.name}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Manufacturing Plant</label>
                <select
                  value={formData.location_id}
                  onChange={(e) => setFormData({ ...formData, location_id: e.target.value })}
                  className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white"
                  required
                >
                  {plants.map(p => <option key={p.location_id} value={p.location_id}>{p.location_id} - {p.name}</option>)}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Target ISO Week</label>
                  <input
                    type="text"
                    value={formData.iso_week}
                    onChange={(e) => setFormData({ ...formData, iso_week: e.target.value })}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Planned Quantity</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.planned_quantity}
                    onChange={(e) => setFormData({ ...formData, planned_quantity: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Completion Date</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-100 flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="px-3 py-1.5 bg-slate-100 text-slate-700 font-semibold rounded-lg hover:bg-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 bg-sky-600 text-white font-semibold rounded-lg hover:bg-sky-700"
              >
                Save Schedule
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
