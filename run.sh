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
	echo 'Watching RootPythia'
	[ ! -f ~/.local/bin/watchmedo ] && pip install watchdog
	~/.local/bin/watchmedo shell-command --patterns "requirement*.txt;src/*.py" --recursive --command='echo "Reloading" && ./run.sh dev'
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
