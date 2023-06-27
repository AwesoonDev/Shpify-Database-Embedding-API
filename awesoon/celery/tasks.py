from celery import Celery

from awesoon.core.docs import scan_shop
from awesoon.config import config
# configure celery app with Redis as the message broker
app = Celery("scan_tasks",
             broker=f"{config.celery_broker.url}/0",
             result_backend=f"{config.celery_broker.url}/0")


@app.task
def manual_scan_request(shop_id, scan_id, args):
    scan_shop(shop_id, scan_id, args)
    print(f"Scan complete: {scan_id}")
    return True


@app.task
def webhook_scan_request(scan_id):
    pass
