
from dataclasses import asdict, dataclass
from typing import List
from awesoon.core.models import BaseDataClass
from awesoon.core.models.doc_type_enums import StorageStatus


@dataclass
class Doc(BaseDataClass):
    document: str = None
    doc_type: str = None
    doc_identifier: str = None
    hash: str = None
    embedding: List[float] = None
    storage_status: StorageStatus = StorageStatus.IGNORE
    id: str = None

    meta_keys = ["storage_status", "id"]

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if k not in self.meta_keys}
