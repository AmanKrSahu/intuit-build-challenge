from dataclasses import dataclass
from datetime import date


@dataclass
class Order:
    order_id: str
    customer_name: str
    product_name: str
    quantity: int
    unit_price: float
    order_date: date


@dataclass
class CustomerSummary:
    customer_name: str
    number_of_orders: int = 0
    total_items_purchased: int = 0
    gross_total: float = 0.0
    discount_amount: float = 0.0
    net_total: float = 0.0
