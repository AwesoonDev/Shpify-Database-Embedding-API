from celery import Celery
from awesoon.adapter.db.shop_client import DatabaseShopClient

from awesoon.config import config
from awesoon.adapter.db.scan_client import DatabaseScanClient
from awesoon.core.exceptions import ShopInstallationNotFoundError
from awesoon.core.models.scan import Scan
from awesoon.core.scan import Scanner

# configure celery app with Redis as the message broker
app = Celery("scan_tasks",
             broker=f"{config.celery_broker.url}/0",
             result_backend=f"{config.celery_broker.url}/0")
PERIOD_TIME = 28000


@app.task
def manual_scan_request(scan_id):
    scan: Scan = DatabaseScanClient.get_scan(scan_id)
    Scanner.scan(scan)
    print(f"Scan complete: {scan_id}")
    return True


@app.task
def webhook_scan_request(scan_id):
    pass


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        PERIOD_TIME,
        cron_scan_request.s(),
    )


@app.task
def cron_scan_request():
    shops = DatabaseShopClient.get_shops()
    for shop in shops:
        try:
            shop = DatabaseShopClient.get_shop_installation(shop["shop_identifier"])
            scan: Scan = Scanner.create_scan(shop.shop_id)
            manual_scan_request.delay(scan.id)
        except ShopInstallationNotFoundError:
            pass
