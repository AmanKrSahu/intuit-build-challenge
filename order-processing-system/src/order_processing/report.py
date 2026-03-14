import os
from typing import List
from src.order_processing.models import CustomerSummary


class ReportGenerator:
    def __init__(self, output_path: str = "output/summary_report.txt"):
        self.output_path = output_path
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def write_report(self, summaries: List[CustomerSummary]) -> None:
        grand_gross = 0.0
        grand_discount = 0.0
        grand_net = 0.0

        # Determine column widths for formatting
        col_name = 20
        col_orders = 10
        col_items = 10
        col_gross = 15
        col_discount = 15
        col_net = 15

        header = (f"{'Customer Name':<{col_name}} | {'Orders':<{col_orders}} | {'Items':<{col_items}} | "
                  f"{'Gross Total':<{col_gross}} | {'Discount':<{col_discount}} | {'Net Total':<{col_net}}")
        separator = "-" * len(header)

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("Order Processing Summary Report\n")
            f.write("===============================\n\n")
            f.write(header + "\n")
            f.write(separator + "\n")

            # Sort alphabetically by customer name for consistency
            for summary in sorted(summaries, key=lambda x: x.customer_name):
                row = (f"{summary.customer_name:<{col_name}} | "
                       f"{summary.number_of_orders:<{col_orders}} | "
                       f"{summary.total_items_purchased:<{col_items}} | "
                       f"${summary.gross_total:<{col_gross-1}.2f} | "
                       f"${summary.discount_amount:<{col_discount-1}.2f} | "
                       f"${summary.net_total:<{col_net-1}.2f}")
                f.write(row + "\n")

                grand_gross += summary.gross_total
                grand_discount += summary.discount_amount
                grand_net += summary.net_total

            f.write(separator + "\n")
            # Grand Total Row
            summary_label = "GRAND TOTAL"
            grand_row = (f"{summary_label:<{col_name}} | "
                         f"{'':<{col_orders}} | "
                         f"{'':<{col_items}} | "
                         f"${grand_gross:<{col_gross-1}.2f} | "
                         f"${grand_discount:<{col_discount-1}.2f} | "
                         f"${grand_net:<{col_net-1}.2f}")
            f.write(grand_row + "\n")
