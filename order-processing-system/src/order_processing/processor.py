import logging
import os
from datetime import datetime
from typing import List, Dict
from src.order_processing.models import Order, CustomerSummary


class OrderProcessor:
    def __init__(self, error_log_path: str = "output/error.log"):
        self.error_log_path = error_log_path
        dirname = os.path.dirname(self.error_log_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # Setup specific file logger for errors
        self.error_logger = logging.getLogger("ErrorLogger")
        self.error_logger.setLevel(logging.ERROR)

        # Clear existing handlers if any to avoid duplicates
        if self.error_logger.hasHandlers():
            self.error_logger.handlers.clear()

        fh = logging.FileHandler(
            self.error_log_path, mode="w", encoding="utf-8")
        fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.error_logger.addHandler(fh)

    def parse_file(self, file_path: str) -> List[Order]:
        orders = []
        if not os.path.exists(file_path):
            self.error_logger.error(f"Input file not found: {file_path}")
            return orders

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            self.error_logger.error(f"Input file is empty: {file_path}")
            return orders

        # Assuming first line is header: OrderID|CustomerName|ProductName|Quantity|UnitPrice|OrderDate
        for i, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) != 6:
                self.error_logger.error(
                    f"Line {i} - Malformed record (expected 6 columns, got {len(parts)}): {line}")
                continue

            order_id, customer_name, product_name, qty_str, price_str, date_str = parts

            try:
                quantity = int(qty_str)
                if quantity < 0:
                    self.error_logger.error(
                        f"Line {i} - Negative quantity: {line}")
                    continue

                unit_price = float(price_str)
                if unit_price < 0:
                    self.error_logger.error(
                        f"Line {i} - Negative unit price: {line}")
                    continue

                order_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                orders.append(Order(
                    order_id=order_id,
                    customer_name=customer_name,
                    product_name=product_name,
                    quantity=quantity,
                    unit_price=unit_price,
                    order_date=order_date
                ))
            except ValueError as e:
                self.error_logger.error(
                    f"Line {i} - Data type parsing error ({e}): {line}")

        return orders

    def generate_summaries(self, orders: List[Order]) -> List[CustomerSummary]:
        summary_map: Dict[str, CustomerSummary] = {}

        for order in orders:
            # Business Logic: Line Total
            line_total = order.quantity * order.unit_price

            # Business Logic: 10% discount for orders > $500
            discount = 0.0
            if line_total > 500.0:
                discount = line_total * 0.10

            net_total = line_total - discount

            if order.customer_name not in summary_map:
                summary_map[order.customer_name] = CustomerSummary(
                    customer_name=order.customer_name)

            summary = summary_map[order.customer_name]
            summary.number_of_orders += 1
            summary.total_items_purchased += order.quantity
            summary.gross_total += line_total
            summary.discount_amount += discount
            summary.net_total += net_total

        return list(summary_map.values())
