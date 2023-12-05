#!/bin/sh

set -e

cd /home/ubuntu/gamesguru-api
/usr/bin/docker compose run --rm gamesguru sh -c "python manage.py outdate_offers"
