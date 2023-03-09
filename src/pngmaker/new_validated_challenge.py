from PIL import Image,ImageDraw,ImageFont

from classes.challenge import Challenge
from classes.user import User

class NewValidatedChallenge() :

    def __init__(self,user,challenge) -> None:
        self.image = Image.open("/opt/root-pythia/src/assets/bg_dark.jpg")


user = User(471176,"Xlitoni",5660,733)
chall = Challenge(5,"HTML - Code Source","Web - Serveur","Rien de bien difficile",5,"Très facile")
new_chall_obj = NewValidatedChallenge(user,chall)

new_chall_obj.image.save("output.png")