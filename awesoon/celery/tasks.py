from celery import Celery

from awesoon.config import config
from awesoon.adapter.db.scan_client import DatabaseScanClient
from awesoon.core.models.scan import Scan
from awesoon.core.scan import Scanner

# configure celery app with Redis as the message broker
app = Celery("scan_tasks",
             broker=f"{config.celery_broker.url}/0",
             result_backend=f"{config.celery_broker.url}/0")


@app.task
def manual_scan_request(scan_id):
    scan: Scan = DatabaseScanClient.get_scan(scan_id)
    Scanner.scan(scan)
    print(f"Scan complete: {scan_id}")
    return True


@app.task
def webhook_scan_request(scan_id):
    pass
