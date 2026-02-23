#!/bin/sh
set -e

if [ "$(id -u)" = "0" ]; then
	exec gosu appuser "$@"
fi

exec "$@"
