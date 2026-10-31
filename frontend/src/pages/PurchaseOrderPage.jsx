import React, { useState, useEffect } from 'react';
import { ShoppingCart, CheckCircle, Truck, PackageCheck, Plus, RefreshCw, AlertCircle } from 'lucide-react';
import { poApi, supplierApi, skuApi, locationApi } from '../services/api';

export default function PurchaseOrderPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [suppliers, setSuppliers] = useState([]);
  const [skus, setSkus] = useState([]);
  const [locations, setLocations] = useState([]);

  // New PO form
  const [formData, setFormData] = useState({
    supplier_id: '',
    sku_id: '',
    location_id: '',
    order_quantity: 100,
    unit_cost: 25.0,
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery_date: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0]
  });

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await poApi.list({ status: statusFilter || undefined, limit: 100 });
      setOrders(data);
    } catch (err) {
      console.error('Error fetching purchase orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
    Promise.all([supplierApi.list({ limit: 50 }), skuApi.list({ limit: 100 }), locationApi.list({ limit: 50 })])
      .then(([supData, skuData, locData]) => {
        setSuppliers(supData);
        setSkus(skuData);
        setLocations(locData);
        if (supData.length > 0 && skuData.length > 0 && locData.length > 0) {
          setFormData(prev => ({
            ...prev,
            supplier_id: supData[0].supplier_id,
            sku_id: skuData[0].sku_id,
            location_id: locData[0].location_id
          }));
        }
      })
      .catch(console.error);
  }, [statusFilter]);

  const handleStatusUpdate = async (poId, nextStatus) => {
    try {
      await poApi.updateStatus(poId, nextStatus);
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update order status');
    }
  };

  const handleCreatePO = async (e) => {
    e.preventDefault();
    try {
      await poApi.create(formData);
      setModalOpen(false);
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create purchase order');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'CREATED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">CREATED</span>;
      case 'APPROVED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-50 text-sky-700 border border-sky-200">APPROVED</span>;
      case 'SHIPPED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">SHIPPED</span>;
      case 'RECEIVED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">RECEIVED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700">{status}</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Purchase Orders & Inbound Supply</h1>
          <p className="text-xs text-slate-500 mt-0.5">Track procurement order lifecycle: Created → Approved → Shipped → Received</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setModalOpen(true)}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-sky-600 rounded-lg shadow-sm hover:bg-sky-700"
          >
            <Plus className="w-3.5 h-3.5 mr-1" />
            Issue Purchase Order
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between text-xs">
        <div className="flex items-center space-x-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg bg-white text-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="CREATED">Created</option>
            <option value="APPROVED">Approved</option>
            <option value="SHIPPED">Shipped (In-Transit)</option>
            <option value="RECEIVED">Received</option>
          </select>
        </div>
        <button onClick={fetchOrders} className="p-1.5 text-slate-500 hover:text-slate-800 border border-slate-300 rounded-lg">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">PO Number</th>
                <th className="px-4 py-3">Supplier</th>
                <th className="px-4 py-3">Item SKU</th>
                <th className="px-4 py-3">Destination Facility</th>
                <th className="px-4 py-3 text-right">Order Quantity</th>
                <th className="px-4 py-3 text-right">Total Amount</th>
                <th className="px-4 py-3">Order Date</th>
                <th className="px-4 py-3">Expected Delivery</th>
                <th className="px-4 py-3">Lifecycle Status</th>
                <th className="px-4 py-3 text-center">Transition Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan="10" className="text-center py-10 text-slate-400">Loading purchase orders...</td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan="10" className="text-center py-10 text-slate-400">No purchase orders found.</td>
                </tr>
              ) : (
                orders.map((po) => (
                  <tr key={po.po_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3 font-mono font-semibold text-slate-900">{po.po_id}</td>
                    <td className="px-4 py-3 font-mono text-slate-800">{po.supplier_id}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-sky-800">{po.sku_id}</td>
                    <td className="px-4 py-3 font-medium text-slate-700">{po.location_id}</td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-slate-900">{po.order_quantity.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono font-medium">${po.total_amount.toLocaleString()}</td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{po.order_date}</td>
                    <td className="px-4 py-3 font-mono text-[11px] font-semibold text-slate-800">{po.expected_delivery_date}</td>
                    <td className="px-4 py-3">{getStatusBadge(po.status)}</td>
                    <td className="px-4 py-3 text-center">
                      {po.status === 'CREATED' && (
                        <button
                          onClick={() => handleStatusUpdate(po.po_id, 'APPROVED')}
                          className="px-2.5 py-1 bg-sky-50 text-sky-700 hover:bg-sky-100 rounded text-[11px] font-semibold border border-sky-200"
                        >
                          Approve PO
                        </button>
                      )}
                      {po.status === 'APPROVED' && (
                        <button
                          onClick={() => handleStatusUpdate(po.po_id, 'SHIPPED')}
                          className="px-2.5 py-1 bg-amber-50 text-amber-700 hover:bg-amber-100 rounded text-[11px] font-semibold border border-amber-200"
                        >
                          Mark Shipped
                        </button>
                      )}
                      {po.status === 'SHIPPED' && (
                        <button
                          onClick={() => handleStatusUpdate(po.po_id, 'RECEIVED')}
                          className="px-2.5 py-1 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 rounded text-[11px] font-semibold border border-emerald-200"
                        >
                          Confirm Receipt
                        </button>
                      )}
                      {po.status === 'RECEIVED' && (
                        <span className="text-[11px] text-emerald-600 font-medium flex items-center justify-center">
                          <CheckCircle className="w-3.5 h-3.5 mr-1" />
                          Received
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreatePO} className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200 text-xs">
            <h3 className="font-bold text-sm text-slate-900 mb-4">Create Inbound Purchase Order</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Supplier</label>
                <select
                  value={formData.supplier_id}
                  onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                  className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white"
                  required
                >
                  {suppliers.map(s => <option key={s.supplier_id} value={s.supplier_id}>{s.supplier_id} - {s.name}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">SKU</label>
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
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Destination Location</label>
                <select
                  value={formData.location_id}
                  onChange={(e) => setFormData({ ...formData, location_id: e.target.value })}
                  className="w-full px-3 py-1.5 border border-slate-300 rounded-lg bg-white"
                  required
                >
                  {locations.map(l => <option key={l.location_id} value={l.location_id}>{l.location_id} - {l.name}</option>)}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Quantity</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.order_quantity}
                    onChange={(e) => setFormData({ ...formData, order_quantity: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Unit Cost ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.unit_cost}
                    onChange={(e) => setFormData({ ...formData, unit_cost: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Order Date</label>
                  <input
                    type="date"
                    value={formData.order_date}
                    onChange={(e) => setFormData({ ...formData, order_date: e.target.value })}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-500 mb-1">Expected Delivery</label>
                  <input
                    type="date"
                    value={formData.expected_delivery_date}
                    onChange={(e) => setFormData({ ...formData, expected_delivery_date: e.target.value })}
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
                Create Order
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
