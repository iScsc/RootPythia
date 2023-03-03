from os import getenv

import discord

SECRET = getenv('USELESS_SECRET')

def main():
    print("hello world from pyflag")
    print("here is my secret from env var:", SECRET)

    print("I also have imported pip package discord.py see `discord.__dir__()`:", discord.__dir__())


if __name__ == '__main__':
    main()
