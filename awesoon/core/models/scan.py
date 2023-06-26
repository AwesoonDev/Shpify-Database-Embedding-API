
from dataclasses import dataclass
import enum


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
class scan_status:
    status: ScanStatus

    def to_dict(self):
        return {"status": self.status.value}


@dataclass
class scan:
    status: ScanStatus
    trigger_type: TriggerType
    shop_id: str
