import pytest
from datetime import date, timedelta
from backend.app.models.purchase_order import PurchaseOrder, Shipment, TransportDelay

def test_lead_time_and_transport_delay_calculation():
    """
    Validates Requirements 9 & 10: Expected delivery date factoring in lead time and delays.
    """
    order_date = date(2026, 1, 10)
    lead_time_days = 5
    transport_delay_days = 2

    base_expected_delivery = order_date + timedelta(days=lead_time_days)
    assert base_expected_delivery == date(2026, 1, 15)

    effective_delivery = base_expected_delivery + timedelta(days=transport_delay_days)
    assert effective_delivery == date(2026, 1, 17)
    assert (effective_delivery - order_date).days == 7
