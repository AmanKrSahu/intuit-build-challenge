import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Item:
    """
    Represents a discrete unit of work/data transferred between threads.

    Attributes:
        id (int): A unique identifier for the item.
        data (Any): The actual payload or data content being transferred.
        timestamp (float): The creation time of the item, useful for tracking latency.
    """
    id: int
    data: Any
    timestamp: float = field(default_factory=time.time)

    def __str__(self):
        """Returns a human-readable string representation of the Item."""
        return f"Item(id={self.id}, data={self.data})"
