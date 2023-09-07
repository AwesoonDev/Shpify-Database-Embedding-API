
import logging
from awesoon.adapter.db.scan_client import DatabaseScanClient
from awesoon.core.exceptions import ScanError
from awesoon.core.filter import ResourceFilter
from awesoon.core.models.scan import Scan, ScanStatus, TriggerType
from awesoon.core.resource import Resources
from awesoon.core.shop import get_shop_resources


class Scanner:

    @classmethod
    def create_scan(cls, shop_id: int) -> Scan:
        scan = Scan(
            status=ScanStatus.PENDING,
            trigger_type=TriggerType.MANUAL,
            shop_id=shop_id
        )
        scan_id = DatabaseScanClient.post_new_scan(scan)
        scan.id = scan_id
        return scan

    @classmethod
    def scan(cls, scan: Scan):
        DatabaseScanClient.update_scan_status(scan, ScanStatus.IN_PROGRESS)
        try:
            filter = ResourceFilter(scan.shop_id)
            shop_resources_generator = get_shop_resources(scan.shop_id, scan.app_name)
            for shop_resources in shop_resources_generator:
                resources = Resources(shop_resources)
                resources.parse_all().apply_filter(
                    filter
                ).embed_all().save_all(scan=scan)
                scan.commit()
            filter.removable_docs().delete(scan=scan)
            scan.commit()
            DatabaseScanClient.update_scan_status(scan, ScanStatus.COMPLETED)
        except Exception as e:
            logging.exception("Scan error happened")
            DatabaseScanClient.update_scan_status(scan, ScanStatus.ERROR)
            raise ScanError(e)
