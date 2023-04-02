import pygame as pg
from stats import Data, Stats
from states import States

class Hero(pg.sprite.Sprite):
    def __init__(self, pos, groups, name: str, type: str):
        super().__init__(groups)
        self.pos = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        face = pg.image.load('./ab_images/hero/' + name + '.png').convert_alpha()
        width = face.get_width()
        height = face.get_height() 
        stats = Stats()            
        self.image = pg.transform.scale(face, ((width / (height / 150)), (States.height / 7.2)))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
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
        self.data = stats.heroes[type]
        self.data = {key: int(value) if value.isdigit() else value for key, value in self.data.items()}
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
        self.spells = []
        self.armor = 0
              
class Monster(pg.sprite.Sprite):
    def __init__(self, pos, groups, type: str):
        super().__init__(groups)
        mob = pg.image.load('./ab_images/monster/' + type + '.png').convert_alpha()
        HEIGHT = mob.get_height()
        WIDTH = mob.get_width()
        stats = Stats()
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.type = type
        self.player = False
        self.animation = False
        self.attacked = False
        self.data = stats.monsters[type]
        self.data = {key: int(value) if value.isdigit() else value for key, value in self.data.items()}
        for name, value in self.data.items():
            setattr(self, name, value)
        #self.speed = self.data["speed"]
        #self.damage = self.data["damage"]
        #self.exp = self.data["exp"]
        #self.health = self.data["health"]
        #self.max_health = self.data["max_health"]
        #self.health = min(self.health, self.max_health)
        #self.menace = self.data["menace"]
        #self.armor = self.data["armor"]
        #SIZE_SCALAR = self.data["size_scalar"]
        self.health = min(self.health, self.max_health)
        SCALAR_W = WIDTH / self.size_scalar
        SCALAR_H = HEIGHT / self.size_scalar
        self.image = pg.transform.scale(mob, (SCALAR_W, SCALAR_H))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        #self.abilities = ["regenerating": True/False]

class Adventure(pg.sprite.Sprite):
    def __init__(self, pos, groups, desc: str, name: str):
        super().__init__(groups)
        scenery = pg.image.load('./ab_images/map/' + name + '.png').convert_alpha()
        height = scenery.get_height()
        width = scenery.get_width()
        self.height = height / 9
        self.width = width / 9
        self.pos_x = States.width * float(pos[0])
        self.pos_y = States.height * float(pos[1])
        self.image = pg.transform.scale(scenery, (self.width, self.height))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        self.desc = desc
        self.name = name
        
class Location(pg.sprite.Sprite):
    def __init__(self, pos, groups, desc, name, content):
        super().__init__(groups)
        scenery = pg.image.load('./ab_images/location/' + name + '.png').convert_alpha()
        self.height = scenery.get_height()
        self.width = scenery.get_width()
        self.pos_x = States.width * float(pos[0])
        self.pos_y = States.height * float(pos[1])
        self.left = None
        self.right = None
        self.desc = desc
        self.image = pg.transform.scale(scenery, ((self.width / 5), (self.height / 5)))
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))
        self.name = name
        self.content = content.split(" ")
        self.treasure = []
        #self.terrain
        #self.modifier

class Arrow(pg.sprite.Sprite):
    def __init__(self, pos, angle: int, groups, destination: object):
        super().__init__(groups)
        w_picture = pg.image.load('./ab_images/w_arrow.png').convert_alpha()
        r_picture = pg.image.load('./ab_images/r_arrow.png').convert_alpha()
        self.height = w_picture.get_height()
        self.width = w_picture.get_width()
        w_arrow = pg.transform.scale(w_picture, ((self.width / 12), (self.height / 12)))
        r_arrow = pg.transform.scale(r_picture, ((self.width / 12), (self.height / 12)))
        self.angle = int(angle)
        self.r_image = pg.transform.rotozoom(r_arrow, self.angle, 1)
        self.w_image = pg.transform.rotozoom(w_arrow, self.angle, 1)
        self.image = self.w_image
        self.pos_x = States.width * float(pos[0])
        self.pos_y = States.height * float(pos[1])
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))
        self.dest = destination

class TalentName():
    def __init__(self, sample, pos_x, pos_y, font, hero):
        self.font = font
        self.a_name = sample[0][1]['name']
        self.a_text = self.font.render(self.a_name + ":", True, (0,0,0))
        self.b_name = sample[1][1]['name']
        self.b_text = self.font.render(self.b_name + ":", True, (0,0,0))
        self.a_rect = self.a_text.get_rect(topleft=(pos_x, pos_y[0]))
        self.b_rect = self.b_text.get_rect(topleft=(pos_x, pos_y[1]))
        self.a_selected = False
        self.b_selected = False
        self.hero = hero
        self.pos = pos_x
        self.a_type = sample[0][1]['type']
        self.b_type = sample[1][1]['type']

class TalentInfo():
    def __init__(self, sample, pos_x, pos_y, font):
        self.font = font  
        self.a_info = sample[0][1]['desc']
        self.a_text = self.font.render(self.a_info, True, (0,0,0))
        self.b_info = sample[1][1]['desc']
        self.b_text = self.font.render(self.b_info, True, (0,0,0))
        self.a_rect = self.a_text.get_rect(topleft=(pos_x, pos_y[0]))
        self.b_rect = self.b_text.get_rect(topleft=(pos_x, pos_y[1]))
        self.a_selected = False
        self.b_selected = False

class Talent(): 
    def __init__(self, name: str, desc: str, effect: str):
        self.name_text = name
        self.desc_text = desc
        self.effect = effect