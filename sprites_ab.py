import pygame as pg
from data_ab import get_data
from config_ab import Config
import numpy as np
import pandas as pd
import random
import sys

monster_data = get_data('monsters')


class Monster(Config, pg.sprite.Sprite):
    def __init__(self, groups, pos, type: str):
        super().__init__()
        pg.sprite.Sprite.__init__(self, groups) 

        mob = pg.image.load('./ab_images/monster/' + type + '.png').convert_alpha()
        HEIGHT = mob.get_height()
        WIDTH = mob.get_width()
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.type = type
        self.player = False
        self.animation = False
        self.attacked = False

        self.df = monster_data[monster_data['name'] == self.type].reset_index(drop=True)
        # Assign stats name, size_scalar, health, max_health, exp, damage, speed, menace, armor, weapon, gold_min, gold_max
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
    
    def get_target(self):
        total_menace = sum(hero.menace for hero in Config.party_heroes)
        prob = [hero.menace/total_menace for hero in Config.party_heroes]
        target = np.random.choice(Config.party_heroes, p=prob)
        return target

    def melee_attack(self):
        target = self.get_target()
        self.animation = False
        DAMAGE = self.damage - target.armor
        target.health -= DAMAGE
    
    def draw_health_bar(self, width=100, height=10, border_width_factor=0.01):

        health_ratio = self.health / self.max_health
        bar_width = int(width * health_ratio)
        border_width = int(width * border_width_factor)

        pg.draw.rect(self.screen, self.black, [self.pos_x - border_width, self.pos_y - 10 - border_width, width + 2 * border_width, height + 2 * border_width])
        pg.draw.rect(self.screen, self.red, [self.pos_x, self.pos_y - 10, bar_width, height])

class Adventure(pg.sprite.Sprite):
    def __init__(self, pos, groups, desc: str, name: str):
        super().__init__(groups)
        scenery = pg.image.load('./ab_images/map/' + name + '.png').convert_alpha()
        height = scenery.get_height()
        width = scenery.get_width()
        scenery_size_scalar = 9
        self.height = height / scenery_size_scalar
        self.width = width / scenery_size_scalar
        self.pos_x = Config.width * float(pos[0])
        self.pos_y = Config.height * float(pos[1])

        #stuff in shops

        self.image = pg.transform.smoothscale(scenery, (self.width, self.height))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        self.desc = desc
        self.name = name
        

class Location(pg.sprite.Sprite):
    def __init__(self, groups, df):
        super().__init__(groups)

        # Assign id, name, type, y_coord, size_scalar, tier, depth, desc, image_name, parent1, parent2, child1, child2
        for stat_name in df.index:
            setattr(self, stat_name, int(df[stat_name]) if str(df[stat_name]).isdigit() else df[stat_name])

        scenery = pg.image.load('./ab_images/location/' + self.image_name + '.png').convert_alpha()
        self.height = scenery.get_height()
        self.width = scenery.get_width()

        self.pos_x = Config.width * (0.07 * self.depth)
        self.pos_y = Config.height * float(self.y_coord)
        self.pos = (self.pos_x, self.pos_y)
    
        self.image = pg.transform.smoothscale(scenery, ((self.width / self.size_scalar), (self.height / self.size_scalar)))
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))

        self.treasure = []

class Button(Config, pg.sprite.Sprite):
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


class TalentCard(Config, pg.sprite.Sprite):
    def __init__(self, groups, df, pos_x, pos_y, hero, font):
        super().__init__() 
        pg.sprite.Sprite.__init__(self, groups) 

        self.name = df.at[0, 'name']
        self.type = df.at[0, 'type']
        self.desc = df.at[0, 'desc']

        self.selected = False
        self.font = font
        self.hero = hero
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos = (self.pos_x, self.pos_y)

        self.image = self.render_texts()
        self.rect = self.image.get_rect(topleft=self.pos) #position
        self.height = self.image.get_height()
        #inflate rect
        #draw border
        self.border_width = 2
        self.border_color = (self.black)
        self.draw_border()

    def draw_border(self):
        pg.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_width)

    def render_texts(self):
        name_surface = self.font.render(self.name + ":", True, self.black)
        desc_surface = self.font.render(self.desc, True, self.black)
        #add padding to width and heights
        padding_x = 10 
        padding_y = 5
        combined_width = max(name_surface.get_width(), desc_surface.get_width()) + padding_x
        combined_height = name_surface.get_height() + desc_surface.get_height() + padding_y
        combined_surface = pg.Surface((combined_width, combined_height), pg.SRCALPHA)
        #combined_surface.fill(self.white)
        combined_surface.blit(name_surface, (5, 0))
        combined_surface.blit(desc_surface, (5, name_surface.get_height()))

        return combined_surface


class MagicItem(): 
    def __init__(self, name: str, desc: str, effect: str, type: str):
        self.name_text = name
        self.desc_text = desc
        self.effect = effect
        self.type = type
