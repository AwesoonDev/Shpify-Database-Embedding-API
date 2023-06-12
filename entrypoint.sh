#!/bin/bash
echo 'starting gnicorn now'
. activate db-api
gunicorn -w 4 -k gevent -b :80 --timeout 120 --forwarded-allow-ips="*" --log-level=info --error-logfile - --access-logfile - 'cookiecutter.app:create_app()'