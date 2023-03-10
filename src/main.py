from os import getenv

from api.rate_limiter import RateLimiter
from api.rootme_api import RootMeApi

import discord
import asyncio

SECRET = getenv('USELESS_SECRET')
MODE = getenv('MODE')

async def main():
    print("hello world from pyflag")
    print("here is my secret from env var:", SECRET)

    print("I also have imported pip package discord.py see `discord.__dir__()`:", dir(discord))

    print(f"And we currently are in {MODE} mode")

    rate_limiter = RateLimiter()
    ApiRootMe = RootMeApi(rate_limiter)
    data_test = await ApiRootMe.GetChallengeById(5)
    print(data_test)
    data_test = await ApiRootMe.GetUserById(471176)
    print(data_test)



if __name__ == '__main__':
    asyncio.run(main())
