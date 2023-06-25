
from dataclasses import dataclass
from typing import List

@dataclass
class doc:
    document: str
    embedding: List[float]
    docs_version: str
    type: str
    identifier: str
    hash: str
