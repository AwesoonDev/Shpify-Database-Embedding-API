
from dataclasses import dataclass
from typing import List

@dataclass
class Doc:
    document: str
    embedding: List[float]
    doc_type: str
    doc_identifier: str
    hash: str
