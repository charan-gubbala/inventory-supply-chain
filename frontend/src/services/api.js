import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary').then(res => res.data),
  getInventoryTrend: () => api.get('/dashboard/inventory-trend').then(res => res.data),
  getShortageTrend: () => api.get('/dashboard/shortage-trend').then(res => res.data),
  getSupplierPerformance: () => api.get('/dashboard/supplier-performance').then(res => res.data),
};

export const skuApi = {
  list: (params) => api.get('/skus', { params }).then(res => res.data),
  get: (skuId) => api.get(`/skus/${skuId}`).then(res => res.data),
  getSubstitutes: (skuId) => api.get(`/skus/${skuId}/substitutes`).then(res => res.data),
  create: (data) => api.post('/skus', data).then(res => res.data),
};

export const locationApi = {
  list: (params) => api.get('/locations', { params }).then(res => res.data),
  get: (locationId) => api.get(`/locations/${locationId}`).then(res => res.data),
};

export const demandApi = {
  list: (params) => api.get('/demand', { params }).then(res => res.data),
};

export const inventoryApi = {
  list: (params) => api.get('/inventory', { params }).then(res => res.data),
  getLane: (skuId, locationId) => api.get(`/inventory/${skuId}/${locationId}`).then(res => res.data),
};

export const supplierApi = {
  list: (params) => api.get('/suppliers', { params }).then(res => res.data),
  get: (supplierId) => api.get(`/suppliers/${supplierId}`).then(res => res.data),
  getCapacities: (supplierId) => api.get(`/suppliers/${supplierId}/capacities`).then(res => res.data),
  getLeadTimes: (supplierId) => api.get(`/suppliers/${supplierId}/lead-times`).then(res => res.data),
};

export const poApi = {
  list: (params) => api.get('/purchase-orders', { params }).then(res => res.data),
  create: (data) => api.post('/purchase-orders', data).then(res => res.data),
  updateStatus: (poId, status) => api.patch(`/purchase-orders/${poId}/status`, { status }).then(res => res.data),
};

export const productionApi = {
  list: (params) => api.get('/production-plans', { params }).then(res => res.data),
  create: (data) => api.post('/production-plans', data).then(res => res.data),
};

export const shortageApi = {
  list: (params) => api.get('/shortages', { params }).then(res => res.data),
  get: (shortageId) => api.get(`/shortages/${shortageId}`).then(res => res.data),
  runDetection: (isoWeek) => api.post('/shortages/run-detection', null, { params: { iso_week: isoWeek } }).then(res => res.data),
  getMitigations: (shortageId) => api.get(`/shortages/${shortageId}/mitigations`).then(res => res.data),
};

export const mitigationApi = {
  approve: (mitigationId) => api.post(`/mitigations/${mitigationId}/approve`).then(res => res.data),
  reject: (mitigationId, reason) => api.post(`/mitigations/${mitigationId}/reject`, { reason }).then(res => res.data),
};

export const validationApi = {
  run: () => api.post('/validation/run').then(res => res.data),
  getResults: () => api.get('/validation/results').then(res => res.data),
};

export const dataGenApi = {
  run: (mode, seed) => api.post('/data-generation/run', { mode, seed }).then(res => res.data),
  getStatus: () => api.get('/data-generation/status').then(res => res.data),
  getReport: () => api.get('/data-generation/report').then(res => res.data),
};

export const exceptionsApi = {
  list: () => api.get('/exceptions').then(res => res.data),
  getOverview: () => api.get('/exceptions/scenarios-overview').then(res => res.data),
};

export default api;
