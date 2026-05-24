from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductRecord:
    source: str
    keyword: str
    title: str
    url: str
    price: Optional[float]
    currency: Optional[str]
    watchers: Optional[int]
    sold: Optional[int]
