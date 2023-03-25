import pygame as pg
from stats import Data, Stats
from states import States

class Hero(pg.sprite.Sprite):
    def __init__(self, pos, groups, name: str, type: str):
        super().__init__(groups)
        self.xpos = pos[0]
        self.ypos = pos[1]
        path = './ab_images/hero/' + name + '.png'
        face = pg.image.load(path) 
        width = face.get_width()
        height = face.get_height() 
        stats = Stats()            
        self.image = pg.transform.scale(face, ((width / (height / 150)), (States.height / 7.2)))
        self.rect = self.image.get_rect(topleft = (self.xpos, self.ypos))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.animation = False
        self.attacked = False
        self.name = name
        self.player = True
        self.type = type
        self.talents = []
        self.spot_frame = False
        #gold cost, random starting talent
        #Create data dicts at startup only

        #heroes = Data.hero_data()
        #self.data = heroes[type]
        
        self.data = stats.heroes[type]  
        for i in self.data:
            if self.data[i] == type:
                continue
            elif self.data[i] == "spell" or self.data[i] == "weapon":
                continue
            self.data[i] = int(self.data[i])
        self.level = 1
        self.next_level = 2
        self.damage = self.data["damage"]
        self.exp = self.data["exp"]
        self.health = self.data["health"]
        self.max_health = self.data["max_health"]
        self.health = min(self.health, self.max_health)
        self.speed = self.data["speed"]
        self.menace = self.data["menace"]
        self.attack_type = self.data["attack_type"]
        #from data self.attack_type for animation
        self.spells = []
        self.armor = 0
              
class Monster(pg.sprite.Sprite):
    def __init__(self, pos, groups, type: str):
        super().__init__(groups)
        path = './ab_images/monster/' + type + '.png'
        mob = pg.image.load(path)
        height = mob.get_height()
        width = mob.get_width()
        stats = Stats()
        self.xpos = pos[0]
        self.ypos = pos[1]
        self.image = pg.transform.scale(mob, ((width / 10), (height / 10)))
        self.rect = self.image.get_rect(topleft = (self.xpos, self.ypos))
        self.type = type
        self.player = False
        self.animation = False
        self.attacked = False
 
        self.data = stats.monsters[type]
        self.data = {key: int(value) if value.isdigit() else value for key, value in self.data.items()}
        
        #for i in self.data:
        #    if self.data[i] == type:
        #        continue
        #    self.data[i] = int(self.data[i])

        self.speed = self.data["speed"]
        self.damage = self.data["damage"]
        self.exp = self.data["exp"]
        self.health = self.data["health"]
        self.max_health = self.data["max_health"]
        self.health = min(self.health, self.max_health)
        self.menace = self.data["menace"]
        self.armor = self.data["armor"]
        #self.abilities = ["regenerating": True/False]
        
class Loc(pg.sprite.Sprite):
    def __init__(self, pos, groups, location, name: str):
        super().__init__(groups)
        path = './ab_images/' + name + '.png'
        scenery = pg.image.load(path)
        self.height = scenery.get_height()
        self.width = scenery.get_width()
        self.xpos = pos[0]
        self.ypos = pos[1]
        self.left = None
        self.right = None
        self.location = location
        self.rwarrow = None
        self.rrarrow = None
        self.lwarrow = None
        self.rrarrow = None
        if self.height + self.width > 4000:
            self.image = pg.transform.scale(scenery, ((self.width / 17), (self.height / 17)))
        elif self.height + self.width > 3000:
            self.image = pg.transform.scale(scenery, ((self.width / 13), (self.height / 13)))
        else:
            self.image = pg.transform.scale(scenery, ((self.width / 8), (self.height / 8)))
        self.rect = self.image.get_rect(center = pos)
        self.name = name
        self.content = []
        self.treasure = []
        #self.terrain
        #self.modifier

class Arrow(pg.sprite.Sprite):
    def __init__(self, pos, angle: int, groups, destination: object, name: str):
        super().__init__(groups)
        path = './ab_images/' + name + '.png'
        picture = pg.image.load(path)
        self.height = picture.get_height()
        self.width = picture.get_width()
        arrow = pg.transform.scale(picture, ((self.width / 12), (self.height / 12)))
        self.image = pg.transform.rotozoom(arrow, angle, 1) #lock in 50 and -50
        self.rect = self.image.get_rect(center = pos)
        self.destination = destination
        self.visible = False

class TalentName():
    def __init__(self, sample, xpos, ypos1, ypos2, font, hero: int):
        self.font = font 
        self.a_name = sample[0][1]['name']
        self.a_text = self.font.render(self.a_name + ":", True, (0,0,0))
        self.b_name = sample[1][1]['name']
        self.b_text = self.font.render(self.b_name + ":", True, (0,0,0))
        self.a_rect = self.a_text.get_rect(topleft=(xpos, ypos1))
        self.b_rect = self.b_text.get_rect(topleft=(xpos, ypos2))
        self.a_selected = False
        self.b_selected = False
        self.hero = hero
        self.pos = xpos
        self.a_type = sample[0][1]['type']
        self.b_type = sample[1][1]['type']

class TalentInfo():
    def __init__(self, sample, xpos, ypos1, ypos2, font):
        self.font = font  
        self.a_info = sample[0][1]['desc']
        self.a_text = self.font.render(self.a_info, True, (0,0,0))
        self.b_info = sample[1][1]['desc']
        self.b_text = self.font.render(self.b_info, True, (0,0,0))
        self.a_rect = self.a_text.get_rect(topleft=(xpos, ypos1))
        self.b_rect = self.b_text.get_rect(topleft=(xpos, ypos2))
        self.a_selected = False
        self.b_selected = False

class Talent(): 
    def __init__(self, name: str, desc: str, effect: str):
        self.name_text = name
        self.desc_text = desc
        self.effect = effect

class Spellhand(pg.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        kasi = pg.image.load('./ab_images/rhand.png')
        height = kasi.get_height()
        width = kasi.get_width()
        self.image = pg.transform.scale(kasi, ((width / 15), (height / 15)))
        self.rect = self.image.get_rect(topleft = pos)