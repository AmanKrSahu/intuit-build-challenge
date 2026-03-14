from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SaleRecord:
    """
    Immutable representation of a single sales transaction.
    """
    transactionId: str
    date: datetime
    region: str
    salesperson: str
    productCategory: str
    quantity: int
    unitPrice: float
    totalAmount: float

    @classmethod
    def from_csv_row(cls, row: dict) -> 'SaleRecord':
        try:
            qty = int(row['quantity'])
            price = float(row['unit_price'])
            return cls(
                transactionId=row['transaction_id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                region=row['region'],
                salesperson=row['salesperson'],
                productCategory=row['product_category'],
                quantity=qty,
                unitPrice=price,
                totalAmount=qty * price
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Malformed CSV data: {e}")
