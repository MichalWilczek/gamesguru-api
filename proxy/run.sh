#!/bin/sh

# fail the entire script if any of the command lines fail
set -e

# environment substitute
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'
