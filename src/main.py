from os import getenv
import asyncio
import logging
import discord

from classes.challenge import Challenge
from classes.user import User
from pngmaker.new_validated_challenge import NewValidatedChallenge
from bot.root_pythia_bot import BOT as root_pythia

MODE = getenv('MODE')
DISCORD_TOKEN = getenv('DISCORD_TOKEN')
LOG_LEVEL = getenv('LOG_LEVEL')

def main():
    # Setup a beautiful root logger
    discord.utils.setup_logging(root=True, level=LOG_LEVEL)

    # are these call secure??
    logging.debug("discord token: %s", DISCORD_TOKEN)

    # rate_limiter = RateLimiter()
    # ApiRootMe = RootMeApi(rate_limiter)
    # data_test = await ApiRootMe.GetChallengeById(5)
    # logging.debug(data_test)
    # data_test = await ApiRootMe.GetUserById(471176)
    # logging.debug(data_test)

    try:
        root_pythia.run(DISCORD_TOKEN, log_handler=None)
    except discord.errors.LoginFailure:
        logging.error("Invalid Discord token!")
        exit(1)

if __name__ == '__main__':
    main()
