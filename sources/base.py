from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class SignalDoc:
    source: str
    title: str
    text: str
    url: str
    published_at: datetime | None
    meta: Dict[str, Any]

class SignalSource(ABC):
    name: str

    @abstractmethod
    def fetch(self, queries: List[str], recency_days: int) -> List[SignalDoc]:
        ...
