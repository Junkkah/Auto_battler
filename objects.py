import pygame as pg
from data import Data

#put all stats from dict into self.stats

class Hero(pg.sprite.Sprite):
    def __init__(self, pos, groups, name: str, type: str):
        super().__init__(groups)
        self.xpos = pos[0]
        self.ypos = pos[1]
        path = 'auto_battle/ab_kuvat/' + name + '.png'
        naama = pg.image.load(path) 
        width = naama.get_width()
        height = naama.get_height()             
        self.image = pg.transform.scale(naama, ((width / (height / 150)), 150))
        self.rect = self.image.get_rect(topleft = (self.xpos, self.ypos))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.name = name
        self.player = True
        self.type = type
        self.abilities = []
        self.spot_frame = False
        #gold cost, random starting talent
        heroes = Data.hero_data()
        self.data = heroes[type]
        for i in self.data:
            if self.data[i] == type:
                continue
            self.data[i] = int(self.data[i])
        self.damage = self.data["damage"]
        self.exp = self.data["exp"]
        self.level = 1
        self.next_level = 10
        self.health = self.data["health"]
        self.max_health = self.data["max_health"]
        self.health = min(self.health, self.max_health)
        #from data self.attack_type for animation
        self.animation = False
        self.attacked = False
               
class Monster(pg.sprite.Sprite):
    def __init__(self, pos, groups, type: str):
        super().__init__(groups)
        path = 'auto_battle/ab_kuvat/' + type + '.png'
        mob = pg.image.load(path)
        height = mob.get_height()
        width = mob.get_width()
        self.xpos = pos[0]
        self.ypos = pos[1]
        self.image = pg.transform.scale(mob, ((width / 10), (height / 10)))
        self.rect = self.image.get_rect(topleft = (self.xpos, self.ypos))
        self.type = type
        self.player = False

        monsters = Data.monster_data()
        self.data = monsters[type]
        for i in self.data:
            if self.data[i] == type:
                continue
            self.data[i] = int(self.data[i])
        self.damage = self.data["damage"]
        self.exp = self.data["exp"]
        self.health = self.data["health"]
        self.max_health = self.data["max_health"]
        self.health = min(self.health, self.max_health)
        self.animation = False
        self.attacked = False
        
class Loc(pg.sprite.Sprite):
    def __init__(self, pos, groups, location, name: str):
        super().__init__(groups)
        path = 'auto_battle/ab_kuvat/' + name + '.png'
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
        self.treasure = [] #money, stuff and magic items
        #self.terrain
        #self.modifier

class Arrow(pg.sprite.Sprite):
    def __init__(self, pos, angle: int, groups, destination: object, name: str):
        super().__init__(groups)
        path = 'auto_battle/ab_kuvat/' + name + '.png'
        picture = pg.image.load(path)
        self.height = picture.get_height()
        self.width = picture.get_width()
        arrow = pg.transform.scale(picture, ((self.width / 12), (self.height / 12)))
        self.image = pg.transform.rotozoom(arrow, angle, 1) #lock in 50 and -50
        self.rect = self.image.get_rect(center = pos)
        self.destination = destination
        self.content = [] #not needed anymore
        self.visible = False

class Spellhand(pg.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        kasi = pg.image.load('auto_battle/ab_kuvat/rhand.png')
        height = kasi.get_height()
        width = kasi.get_width()
        self.image = pg.transform.scale(kasi, ((width / 15), (height / 15)))
        self.rect = self.image.get_rect(topleft = pos)