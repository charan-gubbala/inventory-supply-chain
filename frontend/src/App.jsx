import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import SKUPage from './pages/SKUPage';
import LocationPage from './pages/LocationPage';
import DemandPage from './pages/DemandPage';
import InventoryPage from './pages/InventoryPage';
import SupplierPage from './pages/SupplierPage';
import PurchaseOrderPage from './pages/PurchaseOrderPage';
import ProductionPage from './pages/ProductionPage';
import ShortagePage from './pages/ShortagePage';
import MitigationPage from './pages/MitigationPage';
import ExceptionsPage from './pages/ExceptionsPage';
import DataOpsPage from './pages/DataOpsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="skus" element={<SKUPage />} />
        <Route path="locations" element={<LocationPage />} />
        <Route path="demand" element={<DemandPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="suppliers" element={<SupplierPage />} />
        <Route path="purchase-orders" element={<PurchaseOrderPage />} />
        <Route path="production" element={<ProductionPage />} />
        <Route path="shortages" element={<ShortagePage />} />
        <Route path="mitigations" element={<MitigationPage />} />
        <Route path="exceptions" element={<ExceptionsPage />} />
        <Route path="data-ops" element={<DataOpsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
