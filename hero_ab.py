import pygame as pg
from data_ab import row_to_dict, get_data, get_talent_data
from states import States
import numpy as np
import pandas as pd
import random
import sys

hero_data = get_data('classes')
exp_data = get_data('experience')
spells_data = get_data('spells')

class Hero(States, pg.sprite.Sprite):
    def __init__(self, groups, pos, name: str, type: str):
        super().__init__()
        pg.sprite.Sprite.__init__(self, groups) 

        self.pos = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        face = pg.image.load('./ab_images/hero/' + name + '.png').convert_alpha()
        width = face.get_width()
        height = face.get_height() 
        desired_height = self.screen_height / 7.2 #150
        self.image = pg.transform.smoothscale(face, ((width / (height / desired_height)), desired_height))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.animation = False
        self.attacked = False
        self.spot_frame = False
        self.name = name
        self.player = True
        self.type = type

        #what if starting level > 1
        self.level = 1
        self.exp_df = exp_data
        #self.next_level = self.exp_df.at[0, 'exp']
        self.next_level = 2

        self.df = hero_data[hero_data['type'] == self.type].reset_index(drop=True)
        # Assign stats type, health, max_health, damage, speed, exp, menace, armor, attack_type
        for stat_name in self.df.columns:
            setattr(self, stat_name, int(self.df.at[0, stat_name]) if str(self.df.at[0, stat_name]).isdigit() else self.df.at[0, stat_name])
        
        self.spells = []
        self.talents = []
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

    def spell_attack(self, spell):
        self.animation = False
        DAMAGE = spell["damage"]
        if spell["area"] == 1:
            for target_mob in States.room_monsters:
                target_mob.health -= DAMAGE
        else:
            target = self.get_target()
            target.health -= DAMAGE
        #elif spell["area"] == 0 single target attack
        #elif spell["area"] == 2 heal spell
        #elif buff elif debuff
    
    def gain_level(self):
        self.level += 1
        self.next_level = self.exp_df.loc[self.exp_df['level'] == self.level, 'exp'].iloc[0]
        self.max_health += self.level_health
        self.health += self.level_health  

    def add_stat(self, stat_bonus):
        stat_name, stat_val_str = stat_bonus.split()
        stat_val = int(stat_val_str)
        old_val = getattr(self, stat_name, 0)
        new_val = old_val + stat_val
        setattr(self, stat_name, new_val) 
    
    def add_talent(self, talent_name: str, talent_type: str):
        hero_talents = get_talent_data(self.type)
        talents_row = hero_talents[hero_talents['name'] == talent_name]
        talents = row_to_dict(talents_row, talent_name)

        if talent_type == "spell":
            #resolve name/effect in spells with id
            #Talent name: 'Fire Gush' effect: 'fire_gush'
            #effect should be name, name should be name_text

            spell_name = talents["effect"] 
            talent_spell = row_to_dict(spells_data, spell_name)
            self.talents.append(talent_name)
            self.spells.append(talent_spell)

        elif talent_type == "stat":
            self.talents.append(talent_name)
            stat_bonus = talents["effect"]
            self.add_stat(stat_bonus)

        elif talent_type == "special":
            self.talents.append(talent_name)
            #check hero talent list start of combat and pull effects from data

        elif talent_type == "domain":
            self.talents.append(talent_name) 
            self.type = talents["effect"]


        elif talent_type == "m_stat":
            self.talents.append(talent_name)
            #speed 1 damage 1

        elif talent_type == "song":
            #create songs and tunes
            self.talents.append(talent_name)
    
    def draw_health_bar(self, width=100, height=10):
        health_ratio = self.health / self.max_health
        bar_width = int(width * health_ratio)
        pg.draw.rect(self.screen, self.red, [self.pos_x, (self.pos_y + self.height + 10), bar_width, height])

    def draw_health_bar(self, width=100, height=10, border_width_factor=0.01):

        health_ratio = self.health / self.max_health
        bar_width = int(width * health_ratio)
        border_width = int(width * border_width_factor)

        pg.draw.rect(self.screen, self.black, [self.pos_x - border_width, self.pos_y + self.height + 10 - border_width, width + 2 * border_width, height + 2 * border_width])
        pg.draw.rect(self.screen, self.red, [self.pos_x, self.pos_y +self.height + 10, bar_width, height])

