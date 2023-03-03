#!/bin/sh

[ "$#" -ne 1 ] && { echo "Please give exactly one argument"; exit 1; }

if [ "$1" == "prod" ]; then
	# prod mode
	docker build --file Dockerfile -t pyflag-bot:latest .
	docker run --rm --interactive --tty --env-file .env.prod pyflag-bot:latest
	exit 0
fi

if [ "$1" == "dev" ]; then
	# dev mode
	docker build --file Dockerfile-dev -t pyflag-bot-dev:latest .
	docker run --rm --interactive --tty --env-file .env.dev --volume ./src:/opt/pyflag-bot/src pyflag-bot-dev:latest
	exit 0
fi

echo "'$1' is an unkown command please only use 'prod' or 'dev'"
