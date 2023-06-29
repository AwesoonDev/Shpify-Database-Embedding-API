
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
class Scan:
    status: ScanStatus
    trigger_type: TriggerType
    shop_id: int
    scan_id: int = None
    app_name: str = None

    def to_dict(self):
        return {
            "status": self.status.value,
            "trigger_type": self.trigger_type.value,
            "shop_id": self.shop_id
        }
