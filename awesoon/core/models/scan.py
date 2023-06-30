
from dataclasses import dataclass
import enum
from awesoon.core.db_client import DatabaseApiClient

from awesoon.core.models.doc import Doc


class ScanStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class TriggerType(enum.Enum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    WEBHOOK = "WEBHOOK"


db_client = DatabaseApiClient()


@dataclass
class Scan:
    status: ScanStatus
    trigger_type: TriggerType
    shop_id: int
    scan_id: int = None
    app_name: str = None
    docs: Doc = None

    def to_dict(self):
        return {
            "status": self.status.value,
            "trigger_type": self.trigger_type.value,
            "shop_id": self.shop_id
        }

    def commit(self):
        for doc in self.docs:
            if doc.storage_status == "POST":
                db_client.add_doc(self.scan_id, doc)
            elif doc.storage_status == "PUT":
                db_client.update_doc(doc)
            elif doc.storage_status == "DELETE":
                db_client.remove_doc(doc.id)
