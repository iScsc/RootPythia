#!/bin/sh

run__prod () {
	# prod mode
	docker build --file Dockerfile -t root-pythia:latest .
	docker run --rm --interactive --tty --env-file .env.prod root-pythia:latest
}

run__dev () {
	# dev mode
	docker build --file Dockerfile.dev -t root-pythia-dev:latest .
	docker run --rm --interactive --tty --env-file .env.dev --volume ./src:/opt/root-pythia/src root-pythia-dev:latest
}

run__watch () {
	# watch mode
	docker build --file Dockerfile.watch -t root-pythia-dev:latest .
	docker run --rm --interactive --tty --env-file .env.dev --volume ./src:/opt/root-pythia/src root-pythia-watch:latest
}

run() {
	local subcmd=$1; shift
	if type "run__$subcmd" &>/dev/null; then
		"run__$subcmd" "$@"
	else
		echo "subcommand '$subcmd' not recognized" >&2
		echo "please only use 'prod', 'dev' or 'watch'" >&2
		exit 1
	fi
}

[ "$#" -ne 1 ] && { echo "Please give exactly one argument"; exit 1; }
run "$@"
