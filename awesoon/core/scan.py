
import logging
from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.exceptions import ScanError
from awesoon.core.filter import ResourceFilter
from awesoon.core.models.scan import Scan, ScanStatus, TriggerType
from awesoon.core.resource import Resource
from awesoon.core.shop import get_shop_resources


db = DatabaseApiClient()


class Scanner:

    @classmethod
    def create_scan(cls, shop_id: int) -> Scan:
        scan = Scan(
            status=ScanStatus.PENDING,
            trigger_type=TriggerType.MANUAL,
            shop_id=shop_id
        )
        scan_id = db.post_new_scan(scan)
        scan.scan_id = scan_id
        return scan

    @classmethod
    def scan(cls, scan: Scan):
        db.update_scan_status(scan, ScanStatus.IN_PROGRESS)
        try:
            filter = ResourceFilter(scan.shop_id)
            shop_resources: List[Resource] = get_shop_resources(scan.shop_id, scan.app_name)
            for resource in shop_resources:
                resource.parse().apply_filter(
                    filter
                ).embed().execute(scan)
            filter.delete_docs().execute(scan)
            scan.commit()
            db.update_scan_status(scan, ScanStatus.COMPLETED)
        except Exception as e:
            logging.exception("Scan error happened")
            db.update_scan_status(scan, ScanStatus.ERROR)
            raise ScanError(e)
