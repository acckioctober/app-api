#!/bin/sh

set -e

envsubst < /etc/nginx/templates/default.conf.tpl > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'