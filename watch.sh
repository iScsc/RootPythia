#!/bin/sh
echo 'Watching RootPythia'
echo 'Modify and save one of the tracked files to start the app...'
watchmedo shell-command --interval 1 --patterns "src/*.py" --recursive --command='echo "${watch_src_path}" && python3 src/main.py'
