import React, { useState, useEffect } from 'react';
import { FileWarning, ShieldAlert, CheckCircle2, AlertTriangle, RefreshCw, Layers } from 'lucide-react';
import { exceptionsApi } from '../services/api';

export default function ExceptionsPage() {
  const [scenarios, setScenarios] = useState([]);
  const [liveIssues, setLiveIssues] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [scData, issueData] = await Promise.all([
        exceptionsApi.getOverview(),
        exceptionsApi.list()
      ]);
      setScenarios(scData);
      setLiveIssues(issueData);
    } catch (err) {
      console.error('Error fetching exceptions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Controlled Exception Scenarios & Quality Audits</h1>
          <p className="text-xs text-slate-500 mt-0.5">Verification of 5 mandatory negative test scenarios against ground-truth evaluation standards</p>
        </div>
        <button
          onClick={fetchData}
          className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
          Refresh Audits
        </button>
      </div>

      {/* 5 Controlled Scenarios Comparison Cards */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs">Auditing exception scenarios...</div>
        ) : scenarios.map((sc, idx) => (
          <div key={sc.scenario_id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-xs">
            <div className="flex items-start justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-3">
                <span className="w-6 h-6 rounded-md bg-slate-900 text-white font-bold flex items-center justify-center text-xs">
                  {idx + 1}
                </span>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">
                    {sc.scenario_id}: {sc.issue_type.replace(/_/g, ' ')}
                  </h3>
                  <span className="font-mono text-[11px] text-slate-500">Target Record: {sc.affected_record_id}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold flex items-center ${
                  sc.detection_status === 'DETECTED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                }`}>
                  <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
                  {sc.detection_status}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                  {sc.severity}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-1">
              <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Ground Truth Expectation
                </span>
                <p className="text-slate-800 font-medium text-xs">{sc.expected_outcome}</p>
                <div className="mt-2 text-[11px] text-slate-500">
                  Expected Decision: <strong className="text-rose-700 font-mono">{sc.expected_decision}</strong>
                </div>
              </div>

              <div className="bg-emerald-50/40 p-3.5 rounded-lg border border-emerald-200">
                <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider block mb-1">
                  Observed Engine Behavior
                </span>
                <p className="text-slate-800 font-medium text-xs">{sc.actual_outcome}</p>
                <div className="mt-2 text-[11px] text-emerald-700 font-semibold">
                  Rule Enforcement: Preserved valid baseline & prevented corruption
                </div>
              </div>
            </div>

            <div className="mt-3 text-[11px] text-slate-500 bg-slate-50/50 p-2.5 rounded border border-slate-100">
              <strong>Domain Explanation: </strong>{sc.explanation}
            </div>
          </div>
        ))}
      </div>

      {/* Live Logged Data Quality Issues Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200">
          <h3 className="text-sm font-semibold text-slate-800">Recorded Data Quality Event Log</h3>
          <p className="text-[11px] text-slate-500">Immutable records registered by validation engine and business constraints</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Issue ID</th>
                <th className="px-4 py-3">Scenario</th>
                <th className="px-4 py-3">Issue Type</th>
                <th className="px-4 py-3">Affected Table</th>
                <th className="px-4 py-3">Record ID</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Detection Status</th>
                <th className="px-4 py-3">Logged Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {liveIssues.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-6 text-slate-400">No data quality issues logged yet.</td>
                </tr>
              ) : (
                liveIssues.map((issue) => (
                  <tr key={issue.issue_id} className="hover:bg-slate-50/60">
                    <td className="px-4 py-3 font-mono text-[11px] font-semibold text-slate-900">{issue.issue_id}</td>
                    <td className="px-4 py-3 font-mono text-sky-700 font-medium">{issue.scenario_id || 'System'}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{issue.issue_type}</td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{issue.affected_table}</td>
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-700">{issue.affected_record_id}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        {issue.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {issue.detection_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono text-[11px]">{issue.created_at.split('T')[0]}</td>
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
