from os import getenv
from PIL import Image,ImageDraw,ImageFont

class NewValidatedChallenge() :
    """
    Class that creates an image when initialized
    """

    def __init__(self,user,challenge,order) -> None:
        #load PYTHONPATH to get the assets path
        if getenv("PYTHONPATH") is not None :
            self.assets_path = getenv("PYTHONPATH")+"/assets"
        else :
            raise Exception("PYTHONPATH env variable not set")
        #take the background picture for base
        self.image = Image.open(self.assets_path+"/bg_dark.jpg")
        # fill the picture
        self.make_title()
        self.make_profile(user)
        self.make_challenge(challenge)
        self.make_challenge_category(challenge)
        self.make_order(order)

    def make_title(self) :
        # print the title of the picture
        draw = ImageDraw.Draw(self.image)
        font_title = ImageFont.truetype(self.assets_path+"/fonts/Staatliches.ttf",48)
        draw.text((60,25), "Nouveau Challenge Validé", fill=(245, 117, 32), font=font_title)

    def make_profile(self,user) :
        # TODO : Make the profile pic dynamic according to the user
        alpha = Image.new("RGBA", self.image.size, (0,0,0,0))
        #this should be modified to a profile pic depending on the username
        pp = Image.open(self.assets_path+"/profile_pics/auton0.png")

        pp = pp.resize((50,50))
        alpha.paste(pp,(60,90),pp)
        self.image = Image.alpha_composite(self.image.convert("RGBA"),alpha)
        # print the username
        draw = ImageDraw.Draw(self.image)
        font_username = ImageFont.truetype(self.assets_path+"/fonts/gimenell.ttf",24)
        draw.text((120,90), user.username, fill=(229, 232, 151), font=font_username)
        # print the score
        font_score = ImageFont.truetype(self.assets_path+"/fonts/ContrailOne.ttf",18)
        draw.text((120,118), "Score : "+str(user.score), fill=(130, 171, 167), font=font_score)

    def make_challenge(self,challenge) :
        # print the challenge name
        draw = ImageDraw.Draw(self.image)
        font_title = ImageFont.truetype(self.assets_path+"/fonts/Staatliches.ttf",30)
        draw.text((60,150), challenge.title, fill=(108, 212, 155), font=font_title)
        chall_name_size = draw.textlength(challenge.title,font=font_title)
        # print the scoring of the chall
        font_score = ImageFont.truetype(self.assets_path+"/fonts/ContrailOne.ttf",24)
        score_pos = (60+20+int(chall_name_size),155)
        draw.text(score_pos, str(challenge.pts)+" points", fill=(130, 171, 167), font=font_score)

    def make_challenge_category(self,challenge) :
        #print the category logo
        alpha = Image.new("RGBA", self.image.size, (0,0,0,0))
        pp = Image.open(self.assets_path+"/categories/"+challenge.category+".png")
        pp = pp.resize((35,35))
        alpha.paste(pp,(60,190),pp)
        self.image = Image.alpha_composite(self.image.convert("RGBA"),alpha)
        #print the category name
        draw = ImageDraw.Draw(self.image)
        font_category = ImageFont.truetype(self.assets_path+"/fonts/Staatliches.ttf",24)
        draw.text((110,195), challenge.category, fill=(130, 171, 167), font=font_category)

    def make_order(self,order) :
        # print the scoring of the chall
        draw = ImageDraw.Draw(self.image)
        font_score = ImageFont.truetype(self.assets_path+"/fonts/ContrailOne.ttf",20)
        if order==1 :
            draw.text((60,240), "First Blood !", fill=(255, 0, 0), font=font_score)
        else :
            draw.text((60,240), f"{order}ème du serveur", fill=(130, 171, 167), font=font_score)
        # if first blood print the little blood drop (uh it hurts)
        if order==1 :
            alpha = Image.new("RGBA", self.image.size, (0,0,0,0))
            pp = Image.open(self.assets_path+"/firstblood.png")
            pp = pp.resize((100,100))
            alpha.paste(pp,(550,80),pp)
            self.image = Image.alpha_composite(self.image.convert("RGBA"),alpha)

