from os import getenv

from api.rate_limiter import RateLimiter
from api.rootme_api import RootMeApi

import asyncio
import logging
import discord

SECRET = getenv('USELESS_SECRET')
MODE = getenv('MODE')

async def main():
    # Basic configuration
    # (means its setup globally directly for the class logging)
    # Could be fixed in the future if several logger are needed
    # then the format will have to be assigned to each logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s (%(filename)s) %(message)s'
        )
    logging.info("Trying to log stuff")

    logging.debug("hello world from pyflag")
    logging.debug("here is my secret from env var:", SECRET)

    logging.debug("I also have imported pip package discord.py see `discord.__dir__()`:", dir(discord))

    logging.debug(f"And we currently are in {MODE} mode")

    rate_limiter = RateLimiter()
    ApiRootMe = RootMeApi(rate_limiter)
    data_test = await ApiRootMe.GetChallengeById(5)
    logging.debug(data_test)
    data_test = await ApiRootMe.GetUserById(471176)
    logging.debug(data_test)




if __name__ == '__main__':
    asyncio.run(main())
