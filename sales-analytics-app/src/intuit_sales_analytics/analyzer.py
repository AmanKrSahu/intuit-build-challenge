from functools import reduce
from itertools import groupby
from typing import List, Dict, Tuple
from datetime import date

from .models import SaleRecord


class SalesAnalyzer:
    """
    Provides analytical methods over Sales data using functional programming
    (map, filter, reduce, groupby) inspired by Java's Streams API.
    """

    def __init__(self, records: List[SaleRecord]):
        self.records = records

    def get_total_sales_by_region(self) -> List[Tuple[str, float]]:
        # Sort is required before groupby
        sorted_records = sorted(self.records, key=lambda r: r.region)

        return list(map(
            lambda group: (
                group[0],
                reduce(lambda acc, record: acc +
                       record.totalAmount, group[1], 0.0)
            ),
            groupby(sorted_records, key=lambda r: r.region)
        ))

    def get_average_sale_by_category(self) -> List[Tuple[str, float]]:
        sorted_records = sorted(self.records, key=lambda r: r.productCategory)

        def calculate_avg(group_iter):
            items = list(group_iter)
            total = reduce(lambda acc, record: acc +
                           record.totalAmount, items, 0.0)
            return total / len(items) if items else 0.0

        return list(map(
            lambda group: (group[0], calculate_avg(group[1])),
            groupby(sorted_records, key=lambda r: r.productCategory)
        ))

    def get_top_salespersons(self, n: int) -> List[Tuple[str, float]]:
        sorted_records = sorted(self.records, key=lambda r: r.salesperson)

        salesperson_totals = list(map(
            lambda group: (
                group[0],
                reduce(lambda acc, record: acc +
                       record.totalAmount, group[1], 0.0)
            ),
            groupby(sorted_records, key=lambda r: r.salesperson)
        ))

        return sorted(salesperson_totals, key=lambda x: x[1], reverse=True)[:n]

    def get_monthly_sales_trend(self) -> List[Tuple[str, float]]:
        # Map date to YYYY-MM
        records_with_month = map(
            lambda r: {"month": r.date.strftime(
                '%Y-%m'), "amount": r.totalAmount},
            self.records
        )

        sorted_records = sorted(records_with_month, key=lambda r: r["month"])

        return list(map(
            lambda group: (
                group[0],
                reduce(lambda acc, r: acc + r["amount"], group[1], 0.0)
            ),
            groupby(sorted_records, key=lambda r: r["month"])
        ))

    def get_sales_by_date_range(self, start_date: date, end_date: date) -> List[SaleRecord]:
        return list(filter(
            lambda r: start_date <= r.date <= end_date,
            self.records
        ))

    def generate_summary_report(self) -> Dict[str, float]:
        if not self.records:
            return {}

        total_sales = reduce(lambda acc, r: acc +
                             r.totalAmount, self.records, 0.0)
        total_quantity = reduce(lambda acc, r: acc +
                                r.quantity, self.records, 0)

        amounts = list(map(lambda r: r.totalAmount, self.records))
        min_sale = reduce(lambda a, b: min(a, b), amounts)
        max_sale = reduce(lambda a, b: max(a, b), amounts)

        return {
            "total_records": len(self.records),
            "total_sales": total_sales,
            "total_quantity": total_quantity,
            "average_sale": total_sales / len(self.records),
            "min_sale_amount": min_sale,
            "max_sale_amount": max_sale
        }
