
from dataclasses import dataclass
from typing import List

@dataclass
class Doc:
    document: str
    embedding: List[float]
    type: str
    identifier: str
    hash: str
