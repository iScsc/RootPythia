#!/bin/sh

docker build --file Dockerfile -t pyflag-bot:latest .
docker run --rm --interactive --tty pyflag-bot:latest
