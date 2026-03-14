from dataclasses import dataclass, field
from typing import Dict
from datetime import date


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    isAvailable: bool = True


@dataclass
class Member:
    memberId: str
    name: str
    # Maps ISBN to checkout date
    borrowedBooks: Dict[str, date] = field(default_factory=dict)
    fineBalance: float = 0.0
