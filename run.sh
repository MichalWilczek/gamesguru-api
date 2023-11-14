#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

#gunicorn --config=/gunicorn.conf.py
uwsgi --socket :9000 --workers 4 --master --enable-threads --module gamesguru.wsgi
