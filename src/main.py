import logging
from os import getenv
import sys

# in bytes
DEFAULT_LOG_FILE_SIZE_MAX = 10e6
# the number of files the rotating file handler will generate at max
# if exceeded it removes the older one
# see https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler
DEFAULT_LOG_FILES_NUMBER = 5

import discord

from bot import BOT as root_pythia

MODE = getenv("MODE")
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
LOG_LEVEL = getenv("LOG_LEVEL")
if LOG_LEVEL.isnumeric():
    LOG_LEVEL = int(LOG_LEVEL)

LOG_FILE_SIZE_MAX = getenv("LOG_FILE_SIZE_MAX") or DEFAULT_LOG_FILE_SIZE_MAX
try:
    LOG_FILE_SIZE_MAX = int(LOG_FILE_SIZE_MAX)
except ValueError as exc:
    logging.exception("LOG_FILE_SIZE_MAX is not an integer")
    exit(1)

LOG_FILES_NUMBER = getenv("LOG_FILES_NUMBER") or DEFAULT_LOG_FILES_NUMBER
try:
    LOG_FILES_NUMBER = int(LOG_FILES_NUMBER)
except ValueError as exc:
    logging.exception("LOG_FILES_NUMBER is not an integer")
    exit(1)


def main():
    # Setup a beautiful root logger
    discord.utils.setup_logging(root=True, level=LOG_LEVEL)

    # Add a file handler to the root logger
    file_handler = logging.RotatingFileHandler(
        "./logs/RootPythia.log", mode="a", maxBytes=LOG_FILE_SIZE_MAX, backupCount=LOG_FILES_NUMBER
    )
    logging.getLogger().addHandler(file_handler)
    logging.info("FileHandler added to root logger it will write to '%s'", file_handler.stream.name)

    # are these call secure??
    logging.debug("discord token: %s", DISCORD_TOKEN)

    try:
        root_pythia.run(DISCORD_TOKEN, log_handler=None)
    except discord.errors.LoginFailure:
        logging.error("Invalid Discord token!")
        sys.exit(1)


if __name__ == "__main__":
    main()
