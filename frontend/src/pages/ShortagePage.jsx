import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldCheck, RefreshCw, Eye, CheckCircle2, XCircle } from 'lucide-react';
import { shortageApi, mitigationApi } from '../services/api';

export default function ShortagePage() {
  const [shortages, setShortages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');
  const [selectedShortage, setSelectedShortage] = useState(null);
  const [mitigations, setMitigations] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [detecting, setDetecting] = useState(false);

  const fetchShortages = async () => {
    try {
      setLoading(true);
      const data = await shortageApi.list({
        severity: severityFilter || undefined,
        limit: 100
      });
      setShortages(data);
    } catch (err) {
      console.error('Error fetching shortages:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShortages();
  }, [severityFilter]);

  const handleRunDetection = async () => {
    try {
      setDetecting(true);
      await shortageApi.runDetection();
      await fetchShortages();
    } catch (err) {
      alert('Error triggering shortage detection');
    } finally {
      setDetecting(false);
    }
  };

  const openMitigations = async (s) => {
    setSelectedShortage(s);
    try {
      const data = await shortageApi.getMitigations(s.shortage_id);
      setMitigations(data);
      setDrawerOpen(true);
    } catch (err) {
      console.error('Error loading mitigations:', err);
    }
  };

  const handleApproveMitigation = async (mitId) => {
    try {
      await mitigationApi.approve(mitId);
      // Refresh current mitigations and shortages
      const data = await shortageApi.getMitigations(selectedShortage.shortage_id);
      setMitigations(data);
      fetchShortages();
    } catch (err) {
      alert(err.response?.data?.detail || 'Approval failed');
    }
  };

  const handleRejectMitigation = async (mitId) => {
    const reason = prompt('Enter rejection reason:') || 'Rejected by planner';
    try {
      await mitigationApi.reject(mitId, reason);
      const data = await shortageApi.getMitigations(selectedShortage.shortage_id);
      setMitigations(data);
      fetchShortages();
    } catch (err) {
      alert(err.response?.data?.detail || 'Rejection failed');
    }
  };

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-300">CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">HIGH</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-600">LOW</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Shortage Control & Root Cause Attribution</h1>
          <p className="text-xs text-slate-500 mt-0.5">Automated detection when Projected Available Balance (PAB) &lt; 0 with explainable diagnostic causes</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleRunDetection}
            disabled={detecting}
            className="inline-flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-rose-600 rounded-lg shadow-sm hover:bg-rose-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${detecting ? 'animate-spin' : ''}`} />
            Run Shortage Detection Engine
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between text-xs">
        <div className="flex items-center space-x-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical Severities</option>
            <option value="HIGH">High Severities</option>
            <option value="MEDIUM">Medium Severities</option>
            <option value="LOW">Low Severities</option>
          </select>
        </div>
        <button onClick={fetchShortages} className="p-1.5 text-slate-500 hover:text-slate-800 border border-slate-300 rounded-lg">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Shortages Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Shortage ID</th>
                <th className="px-4 py-3">SKU ID</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Week</th>
                <th className="px-4 py-3 text-right">Shortage Quantity</th>
                <th className="px-4 py-3">Expected Shortage Date</th>
                <th className="px-4 py-3">Root Cause</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-center">Mitigations</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan="10" className="text-center py-10 text-slate-400">Scanning shortages...</td>
                </tr>
              ) : shortages.length === 0 ? (
                <tr>
                  <td colSpan="10" className="text-center py-10 text-emerald-600 font-medium">No shortages detected! All demands covered by available and incoming stock.</td>
                </tr>
              ) : (
                shortages.map((s) => (
                  <tr key={s.shortage_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3 font-mono font-semibold text-slate-900">{s.shortage_id}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-sky-800">{s.sku_id}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{s.location_id}</td>
                    <td className="px-4 py-3 font-mono text-sky-700 font-semibold">{s.iso_week}</td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-rose-600">
                      -{s.shortage_quantity.toLocaleString()} units
                    </td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{s.expected_shortage_date}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">
                        {s.root_cause.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">{getSeverityBadge(s.severity)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        s.status === 'MITIGATED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700'
                      }`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => openMitigations(s)}
                        className="inline-flex items-center px-2.5 py-1 bg-sky-50 text-sky-700 hover:bg-sky-100 rounded text-[11px] font-semibold border border-sky-200 transition-colors"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                        Mitigate
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mitigation Drawer */}
      {drawerOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex justify-end z-50">
          <div className="bg-white w-full max-w-2xl h-full shadow-2xl p-6 overflow-y-auto flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs text-rose-600 font-bold">{selectedShortage?.shortage_id}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">{selectedShortage?.sku_id}</span>
                  </div>
                  <h2 className="text-base font-bold text-slate-900 mt-1">
                    Mitigation Options for Deficit of {selectedShortage?.shortage_quantity} Units
                  </h2>
                  <p className="text-xs text-slate-500">Root Cause: {selectedShortage?.root_cause.replace(/_/g, ' ')}</p>
                </div>
                <button onClick={() => setDrawerOpen(false)} className="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
              </div>

              {/* Options list */}
              <div className="mt-6 space-y-4">
                {mitigations.length === 0 ? (
                  <p className="text-xs text-slate-400 py-6 text-center">No mitigation strategies available.</p>
                ) : (
                  mitigations.map((opt) => (
                    <div
                      key={opt.mitigation_id}
                      className={`p-4 rounded-xl border text-xs transition-all ${
                        opt.approval_status === 'APPROVED'
                          ? 'bg-emerald-50/50 border-emerald-300'
                          : (!opt.is_feasible ? 'bg-slate-50/80 border-slate-200 opacity-75' : 'bg-white border-slate-200 shadow-sm')
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center font-bold text-[11px] text-slate-700">
                            #{opt.rank}
                          </span>
                          <span className="font-bold text-slate-900">{opt.strategy_type.replace(/_/g, ' ')}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            opt.is_feasible ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}>
                            {opt.is_feasible ? 'Feasible' : 'Infeasible'}
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-[11px] text-slate-400 block">Score</span>
                          <span className="font-bold text-sm text-sky-700">{opt.recommendation_score} / 100</span>
                        </div>
                      </div>

                      <p className="text-slate-600 mt-2 text-xs leading-relaxed">{opt.explanation}</p>

                      {opt.rejection_reason && (
                        <div className="mt-2 text-[11px] text-rose-600 bg-rose-50 p-2 rounded border border-rose-100 font-medium">
                          Constraint Violated: {opt.rejection_reason}
                        </div>
                      )}

                      <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-100 text-[11px] text-slate-500">
                        <div>
                          <span>Proposed Qty: </span>
                          <strong className="text-slate-800">{opt.proposed_quantity} units</strong>
                        </div>
                        <div>
                          <span>Estimated Cost: </span>
                          <strong className="text-slate-800">${opt.estimated_cost.toLocaleString()}</strong>
                        </div>
                        <div>
                          <span>Arrival: </span>
                          <strong className="text-slate-800">{opt.expected_arrival_date}</strong>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="mt-3 flex items-center justify-end space-x-2 pt-2">
                        {opt.approval_status === 'PROPOSED' && opt.is_feasible && (
                          <>
                            <button
                              onClick={() => handleRejectMitigation(opt.mitigation_id)}
                              className="px-3 py-1 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded border border-slate-300 text-xs"
                            >
                              Reject
                            </button>
                            <button
                              onClick={() => handleApproveMitigation(opt.mitigation_id)}
                              className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded text-xs shadow-sm"
                            >
                              Approve Mitigation
                            </button>
                          </>
                        )}
                        {opt.approval_status === 'APPROVED' && (
                          <span className="text-emerald-700 font-bold text-xs flex items-center">
                            <CheckCircle2 className="w-4 h-4 mr-1 text-emerald-600" />
                            Approved & Scheduled
                          </span>
                        )}
                        {opt.approval_status === 'REJECTED' && (
                          <span className="text-slate-400 font-semibold text-xs flex items-center">
                            <XCircle className="w-4 h-4 mr-1 text-slate-400" />
                            Rejected
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200">
              <button
                onClick={() => setDrawerOpen(false)}
                className="w-full py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-900"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
