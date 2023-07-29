#!/bin/bash
echo 'starting gnicorn now'
. activate shop-api
gunicorn -w 4 -k gevent -b :$PORT --timeout 120 --forwarded-allow-ips="*" --log-level=info --error-logfile - --access-logfile - 'awesoon.app:create_app()'