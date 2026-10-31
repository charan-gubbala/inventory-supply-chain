import React, { useState, useEffect } from 'react';
import { Package, Search, Filter, Plus, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';
import { skuApi } from '../services/api';

export default function SKUPage() {
  const [skus, setSkus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [selectedSku, setSelectedSku] = useState(null);
  const [substitutes, setSubstitutes] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchSkus = async () => {
    try {
      setLoading(true);
      const data = await skuApi.list({
        category: categoryFilter || undefined,
        status: statusFilter || undefined,
        search: search || undefined,
        limit: 100
      });
      setSkus(data);
    } catch (err) {
      console.error('Error fetching SKUs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkus();
  }, [categoryFilter, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchSkus();
  };

  const openSubstitutes = async (sku) => {
    setSelectedSku(sku);
    try {
      const subs = await skuApi.getSubstitutes(sku.sku_id);
      setSubstitutes(subs);
      setModalOpen(true);
    } catch (err) {
      console.error('Error loading substitutes:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">SKU Catalog & Master Items</h1>
          <p className="text-xs text-slate-500 mt-0.5">Manage products, standard costs, safety stocks, and substitute mappings</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
        <form onSubmit={handleSearchSubmit} className="flex items-center w-full md:w-80 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3" />
          <input
            type="text"
            placeholder="Search SKU ID or product name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
          >
            <option value="">All Categories</option>
            <option value="ELECTRONICS">Electronics</option>
            <option value="APPAREL">Apparel</option>
            <option value="INDUSTRIAL">Industrial</option>
            <option value="PHARMA">Pharma</option>
            <option value="PACKAGING">Packaging</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="DISCONTINUED">Discontinued</option>
          </select>

          <button
            onClick={fetchSkus}
            className="p-1.5 text-slate-500 hover:text-slate-800 border border-slate-300 rounded-lg"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">SKU ID</th>
                <th className="px-4 py-3">Product Name</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">UOM</th>
                <th className="px-4 py-3 text-right">Standard Cost</th>
                <th className="px-4 py-3 text-right">Unit Price</th>
                <th className="px-4 py-3 text-right">Safety Stock</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-center">Substitutes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan="9" className="text-center py-10 text-slate-400">Loading catalog...</td>
                </tr>
              ) : skus.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-10 text-slate-400">No SKUs matching search criteria.</td>
                </tr>
              ) : (
                skus.map((sku) => (
                  <tr key={sku.sku_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3 font-mono font-semibold text-slate-900">{sku.sku_id}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{sku.name}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-700">
                        {sku.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{sku.unit_of_measure}</td>
                    <td className="px-4 py-3 text-right font-mono">${sku.cost_per_unit.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-slate-900">${sku.price_per_unit.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right font-mono">{sku.safety_stock_quantity} units</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        sku.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {sku.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => openSubstitutes(sku)}
                        className="inline-flex items-center px-2 py-1 bg-sky-50 text-sky-700 hover:bg-sky-100 rounded text-[11px] font-medium transition-colors"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                        Mappings
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Substitutes Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-semibold text-sm text-slate-900">Approved & Candidate Substitutes</h3>
                <p className="text-xs text-slate-500">Mappable alternate products for {selectedSku?.sku_id} ({selectedSku?.name})</p>
              </div>
              <button onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-slate-600 text-lg leading-none">✕</button>
            </div>
            <div className="py-4 space-y-3">
              {substitutes.length === 0 ? (
                <p className="text-xs text-slate-500 py-4 text-center">No substitute relationships registered for this SKU.</p>
              ) : (
                substitutes.map((sub) => (
                  <div key={sub.substitute_id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between text-xs">
                    <div>
                      <div className="font-mono font-semibold text-slate-800">{sub.substitute_sku_id}</div>
                      <div className="text-[11px] text-slate-500">Conversion Rate: {sub.conversion_rate}x</div>
                      <div className="text-[10px] text-slate-400">Valid: {sub.effective_from} to {sub.effective_to}</div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      sub.approval_status === 'APPROVED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}>
                      {sub.approval_status}
                    </span>
                  </div>
                ))
              )}
            </div>
            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-1.5 bg-slate-800 text-white text-xs font-semibold rounded-lg hover:bg-slate-900"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
