!/bin/sh

set -e

cd /home/ubuntu/gamesguru-api
/usr/bin/docker compose run --rm certbot certbot renew
