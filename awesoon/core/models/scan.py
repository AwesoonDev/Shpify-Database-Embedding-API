
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
        batch_size = 500
        addition_docs = [doc for doc in self.docs if doc.storage_status == StorageStatus.ADD]
        removal_docs = [doc.id for doc in self.docs if doc.storage_status == StorageStatus.DELETE]
        # Adding docs in batches
        while addition_docs:
            batch = addition_docs[:batch_size]
            addition_docs = addition_docs[batch_size:]
            logging.info(f"Added docs: {[doc.doc_identifier for doc in batch]}")
            DatabaseApiClient.add_docs(self.id, batch)

        # Removing docs in batches
        while removal_docs:
            batch = removal_docs[:batch_size]
            removal_docs = removal_docs[batch_size:]
            logging.info(f"Removed docs: {batch}")
            DatabaseApiClient.remove_docs(batch)

        self.docs = []
