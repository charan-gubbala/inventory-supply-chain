import React, { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, RefreshCw, Filter, AlertCircle } from 'lucide-react';
import { mitigationApi, shortageApi } from '../services/api';

export default function MitigationPage() {
  const [mitigations, setMitigations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [strategyFilter, setStrategyFilter] = useState('');
  const [feasibleOnly, setFeasibleOnly] = useState(false);

  const fetchMitigations = async () => {
    try {
      setLoading(true);
      // Fetch shortages, then aggregate top mitigations
      const shortages = await shortageApi.list({ limit: 50 });
      let allOpts = [];
      for (const s of shortages.slice(0, 20)) {
        const opts = await shortageApi.getMitigations(s.shortage_id);
        allOpts = allOpts.concat(opts);
      }
      setMitigations(allOpts);
    } catch (err) {
      console.error('Error fetching mitigations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMitigations();
  }, []);

  const handleApprove = async (mitId) => {
    try {
      await mitigationApi.approve(mitId);
      setMitigations(prev => prev.map(m => m.mitigation_id === mitId ? { ...m, approval_status: 'APPROVED' } : m));
    } catch (err) {
      alert(err.response?.data?.detail || 'Approval failed');
    }
  };

  const handleReject = async (mitId) => {
    const reason = prompt('Rejection reason:') || 'Planner override';
    try {
      await mitigationApi.reject(mitId, reason);
      setMitigations(prev => prev.map(m => m.mitigation_id === mitId ? { ...m, approval_status: 'REJECTED' } : m));
    } catch (err) {
      alert(err.response?.data?.detail || 'Rejection failed');
    }
  };

  const filteredMitigations = mitigations.filter(m => {
    if (strategyFilter && m.strategy_type !== strategyFilter) return false;
    if (feasibleOnly && !m.is_feasible) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Mitigation Recommendation Engine</h1>
          <p className="text-xs text-slate-500 mt-0.5">Automated multi-strategy solutions prioritized by cost, feasibility, lead time, and customer impact</p>
        </div>
        <button
          onClick={fetchMitigations}
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
          Refresh Options
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between text-xs">
        <div className="flex items-center space-x-3">
          <select
            value={strategyFilter}
            onChange={(e) => setStrategyFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All Strategies</option>
            <option value="SUPPLIER_PURCHASE">Supplier Purchase</option>
            <option value="WAREHOUSE_TRANSFER">Warehouse Stock Transfer</option>
            <option value="ADDITIONAL_PRODUCTION">Additional Production</option>
            <option value="APPROVED_SUBSTITUTE">Approved Substitute SKU</option>
          </select>

          <label className="inline-flex items-center space-x-2 text-xs font-medium text-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={feasibleOnly}
              onChange={(e) => setFeasibleOnly(e.target.checked)}
              className="rounded border-slate-300 text-sky-600 focus:ring-sky-500"
            />
            <span>Feasible Only</span>
          </label>
        </div>
      </div>

      {/* Grid of Mitigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-3 text-center py-12 text-slate-400 text-xs">Evaluating supply chain options...</div>
        ) : filteredMitigations.length === 0 ? (
          <div className="col-span-3 text-center py-12 text-slate-400 text-xs">No mitigation options matching filters.</div>
        ) : (
          filteredMitigations.map((opt) => (
            <div
              key={opt.mitigation_id}
              className={`p-5 rounded-xl border flex flex-col justify-between text-xs transition-all ${
                opt.approval_status === 'APPROVED'
                  ? 'bg-emerald-50/60 border-emerald-300 shadow-sm'
                  : (!opt.is_feasible ? 'bg-slate-50/70 border-slate-200 opacity-80' : 'bg-white border-slate-200 shadow-sm hover:shadow-md')
              }`}
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <span className="font-mono text-[10px] text-slate-400 font-semibold">{opt.mitigation_id}</span>
                    <h3 className="font-bold text-slate-900 text-sm">{opt.strategy_type.replace(/_/g, ' ')}</h3>
                    <span className="text-[11px] font-mono text-sky-700 block font-semibold">{opt.shortage_id}</span>
                  </div>
                  <div className="text-right">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-50 text-sky-700 border border-sky-200">
                      Score: {opt.recommendation_score}
                    </span>
                    <span className={`block mt-1 text-[10px] font-semibold ${opt.is_feasible ? 'text-emerald-700' : 'text-rose-600'}`}>
                      {opt.is_feasible ? '● Feasible' : '✕ Infeasible'}
                    </span>
                  </div>
                </div>

                <p className="mt-3 text-slate-600 text-xs leading-relaxed">{opt.explanation}</p>

                {opt.rejection_reason && (
                  <div className="mt-2 text-[11px] text-rose-700 bg-rose-50 p-2 rounded border border-rose-200">
                    {opt.rejection_reason}
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5 text-[11px] text-slate-600">
                  <div className="flex justify-between">
                    <span>Proposed Qty:</span>
                    <strong className="text-slate-900">{opt.proposed_quantity} units</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Est. Cost:</span>
                    <strong className="text-slate-900">${opt.estimated_cost.toLocaleString()}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Est. Arrival:</span>
                    <strong className="text-slate-900">{opt.expected_arrival_date}</strong>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                    opt.approval_status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' : (opt.approval_status === 'REJECTED' ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-700')
                  }`}>
                    {opt.approval_status}
                  </span>
                </div>

                <div className="flex space-x-2">
                  {opt.approval_status === 'PROPOSED' && opt.is_feasible && (
                    <>
                      <button
                        onClick={() => handleReject(opt.mitigation_id)}
                        className="px-2.5 py-1 text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 rounded font-semibold text-[11px]"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApprove(opt.mitigation_id)}
                        className="px-2.5 py-1 text-white bg-emerald-600 hover:bg-emerald-700 rounded font-semibold text-[11px] shadow-sm"
                      >
                        Approve
                      </button>
                    </>
                  )}
                  {opt.approval_status === 'APPROVED' && (
                    <span className="text-emerald-700 font-bold text-xs flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                      Approved
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
