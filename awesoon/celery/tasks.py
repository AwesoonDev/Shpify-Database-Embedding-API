from celery import Celery

from awesoon.core.docs import scan_shop

# configure celery app with Redis as the message broker
app = Celery('scan_tasks', broker='redis://localhost:6379/0', result_backend='redis://localhost:6379/0')


@app.task
def manual_scan_request(shop_id, scan_id, args):
    scan_shop(shop_id, scan_id, args)
    print(f'Scan complete: {scan_id}')
    return True


@app.task
def webhook_scan_request(scan_id):
    pass
