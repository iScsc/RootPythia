from os import getenv

import discord

SECRET = getenv('USELESS_SECRET')
MODE = getenv('MODE')

def main():
    print("hello world from pyflag")
    print("here is my secret from env var:", SECRET)

    print("I also have imported pip package discord.py see `discord.__dir__()`:", discord.__dir__())

    print(f"And we currently are in {MODE} mode")


if __name__ == '__main__':
    main()
