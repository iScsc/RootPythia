from os import getenv
import asyncio
import logging
import discord

from classes.challenge import Challenge
from classes.user import User
from pngmaker.new_validated_challenge import NewValidatedChallenge
from src.api.rate_limiter import RateLimiter
from src.api.rootme_api import RootMeApi

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
    logging.debug("here is my secret from env var: %s", SECRET)

    logging.debug("I also have imported pip package discord.py see `discord.__dir__()`:%s",
                   str(dir(discord)))

    logging.debug("And we currently are in %s mode",str(MODE))

    rate_limiter = RateLimiter()
    ApiRootMe = RootMeApi(rate_limiter)
    data_test = await ApiRootMe.GetChallengeById(5)
    logging.debug(data_test)
    data_test = await ApiRootMe.GetUserById(471176)
    logging.debug(data_test)


    chall = Challenge(5,"HTML - Code source","web-serveur","",5,"very easy")
    xlitoni = User(478523,"Xlitoni",5660,1)
    png_chall = NewValidatedChallenge(xlitoni,chall,1)
    png_chall.image.save("example_png_first_blood.png")


if __name__ == '__main__':
    asyncio.run(main())
