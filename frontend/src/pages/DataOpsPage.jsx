import React, { useState, useEffect } from 'react';
import { Database, CheckCircle2, AlertTriangle, Download, RefreshCw, FileText, Cpu, ShieldCheck } from 'lucide-react';
import { validationApi, dataGenApi } from '../services/api';

export default function DataOpsPage() {
  const [valReport, setValReport] = useState(null);
  const [valLoading, setValLoading] = useState(false);
  const [genStatus, setGenStatus] = useState(null);
  const [genMode, setGenMode] = useState('starter');
  const [seed, setSeed] = useState(20261022);
  const [manifest, setManifest] = useState(null);

  const fetchStatusAndReport = async () => {
    try {
      const [resVal, resStatus, resMan] = await Promise.all([
        validationApi.getResults(),
        dataGenApi.getStatus(),
        dataGenApi.getReport()
      ]);
      setValReport(resVal);
      setGenStatus(resStatus);
      setManifest(resMan);
    } catch (err) {
      console.error('Error fetching data ops status:', err);
    }
  };

  useEffect(() => {
    fetchStatusAndReport();
  }, []);

  const handleRunValidation = async () => {
    try {
      setValLoading(true);
      const res = await validationApi.run();
      setValReport(res);
    } catch (err) {
      alert('Validation run failed');
    } finally {
      setValLoading(false);
    }
  };

  const handleTriggerGeneration = async () => {
    if (genMode === 'full') {
      const confirmed = window.confirm(
        'Full Mode generates 3,000 SKUs, 50 locations, 500 suppliers, and 52 weeks of demand combinations. Proceed with chunked bulk generation?'
      );
      if (!confirmed) return;
    }

    try {
      await dataGenApi.run(genMode, seed);
      alert(`Generation started in ${genMode} mode with seed ${seed}.`);
      fetchStatusAndReport();
    } catch (err) {
      alert(err.response?.data?.detail || 'Generation failed');
    }
  };

  return (
    <div className="space-y-6 text-xs">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Data Operations, Validation & Reproducibility</h1>
          <p className="text-xs text-slate-500 mt-0.5">Control data generation engine, execute 15-point validation suite, and export reproducible artifacts</p>
        </div>
      </div>

      {/* Control Panels Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Synthetic Data Generation Engine */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-sky-700 font-bold text-sm mb-2">
              <Cpu className="w-4 h-4 text-sky-600" />
              <span>Synthetic Generation Engine</span>
            </div>
            <p className="text-slate-500 mb-4">
              Configurable pseudo-random generator with fixed seed ensuring bitwise reproducible supply chain records.
            </p>

            <div className="space-y-3 bg-slate-50 p-4 rounded-lg border border-slate-200">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">Volume Mode</label>
                  <select
                    value={genMode}
                    onChange={(e) => setGenMode(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="starter">Starter Mode (10 SKUs, 4 Wks)</option>
                    <option value="full">Full Mode (3,000 SKUs, 52 Wks)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">Deterministic Seed</label>
                  <input
                    type="number"
                    value={seed}
                    onChange={(e) => setSeed(parseInt(e.target.value) || 20261022)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white"
                  />
                </div>
              </div>

              <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-200">
                Current Engine Status: <strong className="text-slate-900">{genStatus?.status || 'IDLE'}</strong> — {genStatus?.message || 'Ready'}
              </div>
            </div>
          </div>

          <div className="mt-5 pt-3 border-t border-slate-100 flex justify-between items-center">
            <span className="text-[11px] text-slate-400 font-mono">Seed: {seed}</span>
            <button
              onClick={handleTriggerGeneration}
              className="px-4 py-2 bg-sky-600 text-white font-semibold rounded-lg hover:bg-sky-700 shadow-sm"
            >
              Start {genMode.toUpperCase()} Generation
            </button>
          </div>
        </div>

        {/* 15-Point Validation Suite */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-emerald-700 font-bold text-sm mb-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>15-Point Automated Data Validation Suite</span>
            </div>
            <p className="text-slate-500 mb-4">
              Comprehensive arithmetic reconciliation, referential integrity, capacity boundaries, and enum verification.
            </p>

            <div className="grid grid-cols-3 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
              <div>
                <span className="text-[10px] text-slate-400 block uppercase font-bold">Records Checked</span>
                <span className="text-lg font-bold text-slate-900">{valReport?.total_records_checked?.toLocaleString() || 0}</span>
              </div>
              <div>
                <span className="text-[10px] text-emerald-600 block uppercase font-bold">Checks Passed</span>
                <span className="text-lg font-bold text-emerald-700">{valReport?.passed_checks || 0} / 15</span>
              </div>
              <div>
                <span className="text-[10px] text-amber-600 block uppercase font-bold">Warnings / Anom.</span>
                <span className="text-lg font-bold text-amber-600">{valReport?.warning_count || 0}</span>
              </div>
            </div>

            {valReport?.anomalies_detected?.length > 0 && (
              <div className="mt-3 p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-[11px] text-amber-900">
                <strong>Anomalies Detected: </strong>
                {valReport.anomalies_detected.map(a => `${a.type} (${a.count})`).join(', ')}
              </div>
            )}
          </div>

          <div className="mt-5 pt-3 border-t border-slate-100 flex justify-between items-center">
            <span className="text-[11px] text-slate-400">Non-destructive evaluation</span>
            <button
              onClick={handleRunValidation}
              disabled={valLoading}
              className="px-4 py-2 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 shadow-sm disabled:opacity-50"
            >
              {valLoading ? 'Validating...' : 'Execute Validation Suite'}
            </button>
          </div>
        </div>
      </div>

      {/* Dataset Exports Bar */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-2 text-slate-800 font-bold text-sm mb-1">
          <Download className="w-4 h-4 text-sky-600" />
          <span>Export Artifacts & Reproducibility Datasets</span>
        </div>
        <p className="text-slate-500 mb-4">Download structured CSV tables, JSON exports, ground-truth labels, and SQL seeds.</p>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
          {[
            { name: 'SKUs Catalog', file: 'skus' },
            { name: 'Facility Locations', file: 'locations' },
            { name: 'Forecast Demand', file: 'forecast_demands' },
            { name: 'Inventory Balances', file: 'inventory_balances' },
            { name: 'Purchase Orders', file: 'purchase_orders' },
            { name: 'Detected Shortages', file: 'shortages' },
          ].map((item) => (
            <a
              key={item.file}
              href={`/api/exports/csv?table_name=${item.file}`}
              target="_blank"
              rel="noreferrer"
              className="p-3 bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 text-center flex flex-col items-center justify-center transition-colors group"
            >
              <FileText className="w-4 h-4 text-slate-400 group-hover:text-sky-600 mb-1" />
              <span className="font-semibold text-slate-700 text-[11px]">{item.name}</span>
              <span className="text-[9px] font-mono text-slate-400">.CSV</span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
