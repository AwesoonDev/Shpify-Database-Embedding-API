
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import List

from awesoon.adapter.db.api_client import DatabaseApiClient
from awesoon.core.models import BaseDataClass
from awesoon.core.models.doc import Doc
from awesoon.core.models.doc_type_enums import StorageStatus
import logging

logger = logging


class ScanStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class TriggerType(enum.Enum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    WEBHOOK = "WEBHOOK"


@dataclass
class Scan(BaseDataClass):
    status: ScanStatus
    trigger_type: TriggerType
    shop_id: int
    id: int = None
    app_name: str = None
    docs: List[Doc] = None

    def to_dict(self):
        return {
            "status": self.status.value,
            "trigger_type": self.trigger_type.value,
            "shop_id": self.shop_id
        }

    def commit(self):
        for doc in self.docs:
            if doc.storage_status == StorageStatus.ADD:
                logging.info(f"Added doc {doc.doc_identifier}")
                DatabaseApiClient.add_doc(self.id, doc)
            elif doc.storage_status == StorageStatus.DELETE:
                logging.info(f"Removed doc {doc.id}")
                DatabaseApiClient.remove_doc(doc.id)
        self.docs = []
