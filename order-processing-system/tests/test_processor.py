import pytest
import os
from datetime import date
from src.order_processing.processor import OrderProcessor
from src.order_processing.models import Order
from src.order_processing.report import ReportGenerator


def test_parse_file_empty(tmp_path):
    f = tmp_path / "empty.txt"
    f.touch()

    processor = OrderProcessor(error_log_path=str(tmp_path / "error.log"))
    orders = processor.parse_file(str(f))
    assert len(orders) == 0


def test_parse_file_malformed(tmp_path):
    f = tmp_path / "orders.txt"
    f.write_text("OrderID|CustomerName|ProductName|Quantity|UnitPrice|OrderDate\n"
                 "BAD|ROW|DATA\n"
                 "ORD1|Bob|Item|-1|10.0|2024-01-01\n"
                 "ORD2|Bob|Item|1|10.0|2024-01-01")

    error_log = tmp_path / "error.log"
    processor = OrderProcessor(error_log_path=str(error_log))
    orders = processor.parse_file(str(f))

    assert len(orders) == 1
    assert orders[0].order_id == "ORD2"

    # Verify error logging
    errors = error_log.read_text()
    assert "Malformed record" in errors
    assert "Negative quantity" in errors


def test_generate_summaries_discount_logic(tmp_path):
    log_file = tmp_path / "dummy.log"
    processor = OrderProcessor(error_log_path=str(log_file))

    # Create manual orders
    orders = [
        # Total 600 -> Discount 60
        Order("1", "Alice", "Laptop", 2, 300.0, date.today()),
        # Total 50 -> No Discount
        Order("2", "Bob", "Mouse", 1, 50.0, date.today()),
        Order("3", "Alice", "Keyboard", 1, 100.0,
              date.today())  # Total 100 -> No Discount
    ]

    summaries = processor.generate_summaries(orders)
    assert len(summaries) == 2

    # Alice: (2 * 300) = 600 -> applies 10% = 60. Net = 540.
    # Alice: (1 * 100) = 100 -> applies 10% = 0. Net = 100.
    # Total Alice: Gross 700, Discount 60, Net 640.
    alice = next(s for s in summaries if s.customer_name == "Alice")
    assert alice.gross_total == 700.0
    assert alice.discount_amount == 60.0
    assert alice.net_total == 640.0
    assert alice.number_of_orders == 2
    assert alice.total_items_purchased == 3

    bob = next(s for s in summaries if s.customer_name == "Bob")
    assert bob.gross_total == 50.0
    assert bob.discount_amount == 0.0
    assert bob.net_total == 50.0


def test_report_generation(tmp_path):
    summary_file = tmp_path / "summary.txt"
    generator = ReportGenerator(output_path=str(summary_file))

    processor = OrderProcessor(error_log_path=str(tmp_path / "dummy.log"))
    orders = [Order("1", "Alice", "Item", 1, 500.0, date.today())]
    summaries = processor.generate_summaries(orders)

    generator.write_report(summaries)
    content = summary_file.read_text()

    assert "Order Processing Summary Report" in content
    assert "Alice" in content
    assert "GRAND TOTAL" in content
