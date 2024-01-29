import pygame as pg
from stats import Data, Stats, get_data
from states import States
import numpy as np
import pandas as pd
import random
import sys

hero_data = get_data('classes')
monster_data = get_data('monsters')

class Hero(pg.sprite.Sprite):
    def __init__(self, pos, groups, name: str, type: str):
        super().__init__(groups)
        self.pos = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        face = pg.image.load('./ab_images/hero/' + name + '.png').convert_alpha()
        width = face.get_width()
        height = face.get_height() 
        pixel_height = 150
        stats = Stats()            
        self.image = pg.transform.smoothscale(face, ((width / (height / 150)), (States.height / 7.2)))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.animation = False
        self.attacked = False
        self.spot_frame = False
        self.name = name
        self.player = True
        self.type = type
        self.level = 1
        self.next_level = 2

        self.df = hero_data[hero_data['type'] == self.type].reset_index(drop=True)
        # Assign stats type, health, max_health, damage, speed, exp, menace, armor, attack_type
        for stat_name in self.df.columns:
            setattr(self, stat_name, int(self.df.at[0, stat_name]) if str(self.df.at[0, stat_name]).isdigit() else self.df.at[0, stat_name])
        
        self.spells = []
        self.talents = []
        self.damage_numbers = pg.sprite.Group()
        #done before creating animation object
        #set acting, run eval, create animation object
        #def eval_attack_type(self): uncertainty
            #if song in talents do song
            #if spell in spells compare melee, spell
                #if spell compare spells, healing?
    def get_target(self):
        total_menace = sum(monster.menace for monster in States.room_monsters)
        prob = [monster.menace/total_menace for monster in States.room_monsters]
        target = np.random.choice(States.room_monsters, p=prob)
        return target
    
    def melee_attack(self):
        target = self.get_target()
        self.animation = False
        DAMAGE = self.damage - target.armor
        target.health -= DAMAGE
        DAMAGE_NUMBER_OBJ = DamageNumber(DAMAGE, target.pos_x, target.pos_y)
        target.damage_numbers.add(DAMAGE_NUMBER_OBJ)

    def spell_attack(self, spell):
        self.animation = False
        DAMAGE = spell["damage"]
        if spell["area"] == 1:
            for target_mob in States.room_monsters:
                target_mob.health -= DAMAGE
                DAMAGE_NUMBER_OBJ = DamageNumber(DAMAGE, target_mob.pos_x, target_mob.pos_y)
                target_mob.damage_numbers.add(DAMAGE_NUMBER_OBJ)
        else:
            target = self.get_target()
            target.health -= DAMAGE
            DAMAGE_NUMBER_OBJ = DamageNumber(DAMAGE, target.pos_x, target.pos_y)
            target.damage_numbers.add(DAMAGE_NUMBER_OBJ)
        #elif spell["area"] == 0 single target attack
        #elif spell["area"] == 2 heal spell
        #elif buff elif debuff

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

        #self.data = stats.monsters[type]
        #self.data = {key: int(value) if value.isdigit() else value for key, value in self.data.items()}
        #for name, value in self.data.items():
        #    setattr(self, name, value)
        
        self.df = monster_data[monster_data['name'] == self.type].reset_index(drop=True)
        # Assign stats name, size_scalar, health, max_health, exp, damage, speed, menace, armor, weapon
        for stat_name in self.df.columns:
            setattr(self, stat_name, int(self.df.at[0, stat_name]) if str(self.df.at[0, stat_name]).isdigit() else self.df.at[0, stat_name])
        
  
        self.health = min(self.health, self.max_health)
        SCALAR_W = WIDTH / self.size_scalar
        SCALAR_H = HEIGHT / self.size_scalar
        self.image = pg.transform.smoothscale(mob, (SCALAR_W, SCALAR_H))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        #self.abilities = ["regenerating": True/False]
        self.damage_numbers = pg.sprite.Group()
    
    def get_target(self):
        total_menace = sum(hero.menace for hero in States.party_heroes)
        prob = [hero.menace/total_menace for hero in States.party_heroes]
        target = np.random.choice(States.party_heroes, p=prob)
        return target

    def melee_attack(self):
        target = self.get_target()
        self.animation = False
        DAMAGE = self.damage - target.armor
        target.health -= DAMAGE
        DAMAGE_NUMBER_OBJ = DamageNumber(DAMAGE, target.pos_x, target.pos_y)
        target.damage_numbers.add(DAMAGE_NUMBER_OBJ)

class Adventure(pg.sprite.Sprite):
    def __init__(self, pos, groups, desc: str, name: str):
        super().__init__(groups)
        scenery = pg.image.load('./ab_images/map/' + name + '.png').convert_alpha()
        height = scenery.get_height()
        width = scenery.get_width()
        scenery_size_scalar = 9
        self.height = height / scenery_size_scalar
        self.width = width / scenery_size_scalar
        self.pos_x = States.width * float(pos[0])
        self.pos_y = States.height * float(pos[1])
        #needs list of possible monsters in locations and boss
        #list of possible stuff in shops

        self.image = pg.transform.smoothscale(scenery, (self.width, self.height))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        self.desc = desc
        self.name = name
        
        #shop object

class Location(pg.sprite.Sprite):
    def __init__(self, groups, df):
        super().__init__(groups)

        # Assign id, name, type, y_coord, size_scalar, tier, depth, desc, image_name, parent1, parent2, child1, child2
        for stat_name in df.index:
            setattr(self, stat_name, int(df[stat_name]) if str(df[stat_name]).isdigit() else df[stat_name])

        scenery = pg.image.load('./ab_images/location/' + self.image_name + '.png').convert_alpha()
        self.height = scenery.get_height()
        self.width = scenery.get_width()

        self.pos_x = States.width * (0.07 * self.depth)
        self.pos_y = States.height * float(self.y_coord)
        self.pos = (self.pos_x, self.pos_y)
    

        self.image = pg.transform.smoothscale(scenery, ((self.width / self.size_scalar), (self.height / self.size_scalar)))
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))

        #define tiers for locations and do random content
        #random amount of gold / items depending on tier
        self.treasure = []

class Button(States, pg.sprite.Sprite):
    def __init__(self, groups, text, font, font_size, color, center):
        super().__init__() 
        pg.sprite.Sprite.__init__(self, groups) 

        self.text = text
        self.font = pg.font.SysFont(font, font_size)
        self.color = color
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect()
        padding_x = 20 
        padding_y = 10
        self.image = pg.Surface((text_rect.width + 2 * padding_x, text_rect.height + 2 * padding_y), pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.image.blit(text_surface, (padding_x, padding_y))
        self.rect = self.image.get_rect(center=center)
        self.border_width = 2
        self.border_color = (self.black)
        self.draw_border()

    def draw_border(self):
        pg.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_width)

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

class MagicItem(): 
    def __init__(self, name: str, desc: str, effect: str, type: str):
        self.name_text = name
        self.desc_text = desc
        self.effect = effect
        self.type = type

class DamageNumber(pg.sprite.Sprite):
    def __init__(self, damage, pos_x, pos_y):
        super().__init__()
        self.damage = damage
        self.image = pg.font.SysFont("Arial", 30).render(str(damage), True, (255, 0, 0))
        self.rect = self.image.get_rect()
        SCATTER_MIN = 15
        SCATTER_MAX = 110
        self.rect.center = (pos_x + random.randint(SCATTER_MIN, SCATTER_MAX), pos_y + random.randint(SCATTER_MIN, SCATTER_MAX))

#NOT NEEDED
class Loca(pg.sprite.Sprite):
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
        self.size_scalar = 10
        self.image = pg.transform.smoothscale(scenery, ((self.width / self.size_scalar), (self.height / self.size_scalar)))
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))
        self.name = name
        #define tiers for locations and do random content
        self.content = content.split(" ")
        #random amount of gold / items depending on tier
        self.treasure = []
        #self.terrain
        #self.modifier

#NOT NEEDED
class Arrow(pg.sprite.Sprite):
    def __init__(self, pos, angle: int, groups, destination: object):
        super().__init__(groups)
        w_picture = pg.image.load('./ab_images/w_arrow.png').convert_alpha()
        r_picture = pg.image.load('./ab_images/r_arrow.png').convert_alpha()
        self.height = w_picture.get_height()
        self.width = w_picture.get_width()
        w_arrow = pg.transform.smoothscale(w_picture, ((self.width / 12), (self.height / 12)))
        r_arrow = pg.transform.smoothscale(r_picture, ((self.width / 12), (self.height / 12)))
        self.angle = int(angle)
        self.r_image = pg.transform.rotozoom(r_arrow, self.angle, 1)
        self.w_image = pg.transform.rotozoom(w_arrow, self.angle, 1)
        self.image = self.w_image
        self.pos_x = States.width * float(pos[0])
        self.pos_y = States.height * float(pos[1])
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))
        self.dest = destination
