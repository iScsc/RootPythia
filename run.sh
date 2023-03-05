#!/bin/sh

run__prod () {
	# prod mode
	docker build --file Dockerfile -t pyflag-bot:latest .
	docker run --rm --interactive --tty --env-file .env.prod pyflag-bot:latest
}

run__dev () {
	# dev mode
	docker build --file Dockerfile-dev -t pyflag-bot-dev:latest .
	docker run --rm --dns=8.8.8.8 --interactive --tty --env-file .env.dev --volume /home/xlitoni/Desktop/RootPythiaProj/RootPythia/src:/opt/pyflag-bot/src pyflag-bot-dev:latest
}

run() {
	local subcmd=$1; shift
	if type "run__$subcmd" &>/dev/null; then
		"run__$subcmd" "$@"
	else
		echo "subcommand '$subcmd' not recognized" >&2
		echo "please only use 'prod' or 'dev'" >&2
		exit 1
	fi
}

[ "$#" -ne 1 ] && { echo "Please give exactly one argument"; exit 1; }
run "$@"
