#!/bin/sh

NAME="root-pythia"

run__prod () {
	# prod mode
	docker build --file Dockerfile -t ${NAME}:latest .

	source ./.env.prod
	docker run --rm --interactive --tty \
	--detach \
	--volume $(realpath -P ${LOG_FOLDER}):/opt/${NAME}/logs \
	--volume $(realpath -P  ${DB_FOLDER}):/opt/${NAME}/${DB_FOLDER} \
	--env-file .env.prod \
	--name ${NAME} \
	${NAME}:latest
}

run__dev () {
	# dev mode
	docker build --file Dockerfile.dev -t ${NAME}-dev:latest .
	VOLUMES="--volume $(realpath -P ./src):/opt/${NAME}/src --volume $(realpath -P ./tests):/opt/${NAME}/tests"
	# PYTHONPATH is needed to import sources from tests folder
	HARDCODED_ENV='--env PYTHONPATH=./src'
	docker run --interactive --tty --env-file .env.dev ${HARDCODED_ENV} ${VOLUMES} --name ${NAME} ${NAME}-dev:latest
}

run__watch () {
	# watch mode
	docker build --file Dockerfile.watch -t ${NAME}-watch:latest .
	docker run --interactive --tty --env-file .env.dev --volume $(realpath -P ./src):/opt/${NAME}/src --name ${NAME} ${NAME}-watch:latest
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
