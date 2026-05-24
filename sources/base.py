from abc import ABC, abstractmethod
from typing import List
from models import ProductRecord

class BaseSource(ABC):
    name: str

    @abstractmethod
    def fetch(self, keyword: str) -> List[ProductRecord]:
        raise NotImplementedError
