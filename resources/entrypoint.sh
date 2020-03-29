#!/usr/bin/env bash

set -e

touch -a /kanikervanaf/log/uwsgi.log
touch -a /kanikervanaf/log/django.log

cd /kanikervanaf/src/website

./manage.py collectstatic --no-input -v0 --ignore="*.scss"
./manage.py migrate --no-input

chown --recursive www-data:www-data /kanikervanaf/

echo "Starting uwsgi server."
uwsgi --chdir=/kanikervanaf/src/website \
    --module=kanikervanaf.wsgi:application \
    --master --pidfile=/tmp/project-master.pid \
    --socket=:8000 \
    --processes=5 \
    --uid=www-data --gid=www-data \
    --harakiri=20 \
    --post-buffering=16384 \
    --max-requests=5000 \
    --thunder-lock \
    --vacuum \
    --logfile-chown \
    --logto2=/kanikervanaf/log/uwsgi.log \
    --ignore-sigpipe \
    --ignore-write-errors \
    --disable-write-exception
