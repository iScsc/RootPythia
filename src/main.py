import logging
from os import getenv
import sys

import discord

from bot import BOT as root_pythia

MODE = getenv("MODE")
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
LOG_LEVEL = getenv("LOG_LEVEL")


def main():
    # Setup a beautiful root logger
    discord.utils.setup_logging(root=True, level=LOG_LEVEL)

    # Add a file handler to the root logger
    file_handler = logging.RotatingFileHandler("./logs/RootPythia.log", mode='a', maxBytes=10e6, backupCount=5)
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
