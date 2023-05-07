from os import getenv
import discord

from src.classes.challenge import Challenge
from src.classes.user import User
from src.pngmaker.new_validated_challenge import NewValidatedChallenge


SECRET = getenv('USELESS_SECRET')
MODE = getenv('MODE')

def main():
    print("hello world from pyflag")
    print("here is my secret from env var:", SECRET)

    print("I also have imported pip package discord.py see `discord.__dir__()`:", dir(discord))

    print(f"And we currently are in {MODE} mode")

    chall = Challenge(5,"HTML - Code source","web-serveur","",5,"very easy")
    xlitoni = User(478523,"Xlitoni",5660,1)
    png_chall = NewValidatedChallenge(xlitoni,chall,1)
    png_chall.image.save("example_png_first_blood.png")


if __name__ == '__main__':
    main()
