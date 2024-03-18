import pygame as pg
from data_ab import row_to_dict, get_data, get_talent_data
from config_ab import Config
from sprites_ab import Weapon
import numpy as np
import pandas as pd
import random
import sys
from enum import Enum

hero_data = get_data('classes')
exp_data = get_data('experience')
spells_data = get_data('spells')
#weapons_data = get_data('weapons')

class AttackType(Enum):
    MELEE = 'melee'
    SPELL = 'spell'
    SONG = 'song'
#if Config.acting_character.attack_type == AttackType.SPELL:

class Hero(Config, pg.sprite.Sprite):
    def __init__(self, groups, pos, name: str, hero_type: str):
        super().__init__()
        pg.sprite.Sprite.__init__(self, groups) 

        self.pos = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        face = pg.image.load('./ab_images/hero/' + name + '.png').convert_alpha()
        width = face.get_width()
        height = face.get_height() 
        size_scalar = 7.2
        standard_height = self.screen_height / size_scalar
        self.image = pg.transform.smoothscale(face, ((width / (height / standard_height)), standard_height))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.animation = False
        self.attacked = False
        self.spot_frame = False
        self.frame_width = 2
        self.name = name
        self.is_player = True
        self.type = hero_type
        self.inventory_spot = None
        self.inventory_spot_number = None

        self.level = 1
        self.exp_df = exp_data
        self.next_level = self.exp_df.at[0, 'exp']
        self.worn_items = {'head': None, 'body': None, 'hand1': None, 'hand2': None, 'consumable': None}

        self.df = hero_data[hero_data['type'] == self.type].reset_index(drop=True)
        # Assign stats type, health, max_health, damage, speed, exp, menace, armor, attack_type
        for stat_name in self.df.columns:
            setattr(self, stat_name, int(self.df.at[0, stat_name]) if str(self.df.at[0, stat_name]).isdigit() else self.df.at[0, stat_name])

        self.talent_bonus_damage = 0
        self.tempt_talent_bonuses = {'damage' : 0, 'armor' : 0}
        self.spells = []
        self.talents = []
        self.talent_groups = {'combat' : {}, 'location' : {}, 'map' : {}, 'song' : {}}

        self.aura = None
        self.enemy_armor_penalty = 0

    #def evaluate_action(self):
        #done before creating animation object
        #set acting, run eval, create animation object
        #requires weapon data in hero object
            #pass weapons data from hero object to animation
            #if song in talents do song
            #if spell in spells 
                #compare melee, spell
            #if spell compare spells
                #aoe vs single target

    def get_target(self):
        total_menace = sum(monster.menace for monster in Config.room_monsters)
        prob = [monster.menace/total_menace for monster in Config.room_monsters]
        target = np.random.choice(Config.room_monsters, p=prob)
        return target

    def activate_talent_group(self, group):
        for talent_effect, talent_info in self.talent_groups[group].items():
            activation_method = talent_info['activation_method']
            rank = talent_info['rank']
            activation_method(rank)


    def melee_attack(self):
        target = self.get_target()
        self.animation = False
        DAMAGE = self.damage + self.talent_bonus_damage + Config.aura_bonus['damage']
        armor_penalty = self.enemy_armor_penalty
        self.enemy_armor_penalty = 0
        self.talent_bonus_damage = 0
        LOG_DAMAGE = DAMAGE - max(0, target.armor - armor_penalty)
        log_entry = (self.name, LOG_DAMAGE, target.name)
        Config.combat_log.append(log_entry)
        target.take_damage(DAMAGE, 'physical', armor_penalty)

    #Always casting spells[0], needs cast spell as parameter if evaluate_action

    def spell_attack(self, spell):
        damage_type = spell['type']
        self.animation = False
        DAMAGE = spell['damage'] + self.talent_bonus_damage
        armor_penalty = self.enemy_armor_penalty
        self.enemy_armor_penalty = 0
        self.talent_bonus_damage = 0
        self.songmaster_rank = 0

        if spell['area'] == 1:
            log_entry = (self.name, DAMAGE, 'ALL')
            Config.combat_log.append(log_entry)
            for target_mob in Config.room_monsters:
                target_mob.take_damage(DAMAGE, damage_type, armor_penalty)
        if spell['area'] == 0:
            target = self.get_target()
            log_entry = (self.name, DAMAGE, target.name)
            Config.combat_log.append(log_entry)
            target.take_damage(DAMAGE, damage_type, armor_penalty)

    def song_attack(self):
        target = self.get_target()
        self.animation = False
        log_entry = (self.name, 'song', 'everyone')
        Config.combat_log.append(log_entry)

    def take_damage(self, damage_amount, damage_type):
        #activate defensive talent
        if damage_type == 'physical':
            taken_damage = max(0, damage_amount - self.armor - Config.aura_bonus['armor'])
        else:
            taken_damage = damage_amount
        self.health -= taken_damage

    def gain_health(self, gained_health):
        self.health = min(self.health + gained_health, self.max_health)

    def gain_level(self):
        self.level += 1
        self.next_level = self.exp_df.loc[self.exp_df['level'] == self.level, 'exp'].iloc[0]
        self.max_health += self.level_health
        self.gain_health(self.level_health)  
    
    def equip_starting_weapon(self):
        if self.attack_type != 'spell':
            weapon = Weapon(self.attack_type, False)
            self.worn_items['hand1'] = weapon

    def equip_item(self, item):
        slot = item.slot_type
        self.worn_items[slot] = item
    
    def drop_item(self, slot):
        self.worn_items[slot] = None

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

        if talent_type == 'spell':
            #resolve name/effect in spells with id
            #Talent name: 'Fire Gush' effect: 'fire_gush'
            #effect should be name, name should be name_text

            spell_name = talents['effect'] 
            talent_spell = row_to_dict(spells_data, spell_name)
            self.talents.append(talent_name)
            self.spells.append(talent_spell)

        elif talent_type == 'stat':
            self.talents.append(talent_name)
            stat_bonus = talents['effect']
            self.add_stat(stat_bonus)

        elif talent_type in ['location', 'combat', 'map', 'song']:
            self.talents.append(talent_name)
            effect = talents['effect']
            effect_name, rank = effect.split()
            talent_rank = int(rank)
            method_name = f'{effect_name}_activation'
            activation_method = getattr(self, method_name)
            self.talent_groups[talent_type][effect] = {'activation_method': activation_method, 'rank': talent_rank}
            if talent_type == 'song':
                self.attack_type = 'song'
            
        elif talent_type == 'domain':
            self.talents.append(talent_name) 
            self.type = talents['effect']

        elif talent_type == 'm_stat':
            self.talents.append(talent_name)
            string = talents['effect']
            stats = string.split()
            first_bonus = ' '.join(stats[:2])
            second_bonus = ' '.join(stats[2:])
            self.add_stat(first_bonus)
            self.add_stat(second_bonus)
        
        elif talent_type == 'aura':
            self.talents.append(talent_name)
            self.aura = talents['effect']
    
    def draw_health_bar(self, width=100, height=10, border_width_factor=0.01):
        health_ratio = self.health / self.max_health
        bar_width = int(width * health_ratio)
        border_width = int(width * border_width_factor)

        pg.draw.rect(self.screen, self.black, [self.pos_x - border_width, self.pos_y + self.height + 10 - border_width, width + 2 * border_width, height + 2 * border_width])
        pg.draw.rect(self.screen, self.red, [self.pos_x, self.pos_y +self.height + 10, bar_width, height])

    def draw_frame(self):
        pg.draw.rect(self.screen, self.red, [self.pos_x, self.pos_y, self.width, self.height], self.frame_width)
    
    def invisibility_activation(self, rank):
        self.menace = 1
    
    def uplift_activation(self, rank):
        total_rank = self.songmaster_rank + rank
        damage_bonus_per_rank = 1
        total_damage_bonus = damage_bonus_per_rank * total_rank
        Config.aura_bonus['damage'] += total_damage_bonus

    def sooth_activation(self, rank):
        total_rank = self.songmaster_rank + rank
        healing_per_rank = 1
        total_healing = healing_per_rank * total_rank
        for healing_hero in Config.party_heroes:
            healing_hero.gain_health(total_healing)

    def loud_activation(self, rank):
        total_rank = self.songmaster_rank + rank
        damage_per_rank = 1
        total_damage = damage_per_rank * total_rank
        damage_type = 'physical'
        DAMAGE = total_damage
        armor_penalty = 1
        for target_mob in Config.room_monsters:
            target_mob.take_damage(DAMAGE, damage_type, armor_penalty)

    def songmaster_activation(self, rank):
        self.songmaster_rank = rank

    def scout_activation(self, rank):
        Config.scout_active = True 
    
    def surprise_activation(self, rank):
        speed_penalty_per_rank = 3
        total_speed_penalty = speed_penalty_per_rank * rank
        for surprised_monster in Config.room_monsters:
            surprised_monster.speed -= total_speed_penalty

    def berserk_activation(self, rank):
        damage_bonus_per_rank = 3
        total_damage = damage_bonus_per_rank * rank
        if self.health < self.max_health // 2:
            self.talent_bonus_damage += total_damage

    def crush_activation(self, rank):
        armor_pierced_per_rank = 1
        total_pierce = armor_pierced_per_rank * rank
        self.enemy_armor_penalty += total_pierce

    def smite_activation(self, rank):
        damage_per_rank = 1
        damage_type = 'holy'
        DAMAGE = damage_per_rank * rank
        armor_penalty = 0
        for target_mob in Config.room_monsters:
            target_mob.take_damage(DAMAGE, damage_type, armor_penalty)
    
    def replenish_activation(self, rank):
        healing_per_rank = 2
        total_healing = healing_per_rank * rank
        for healing_hero in Config.party_heroes:
            healing_hero.gain_health(total_healing)
    
    def pilfer_activation(self, rank):
        gold_per_rank = 2
        extra_gold = gold_per_rank * rank
        Config.gold_count += extra_gold
    
    def critical_activation(self, rank):
        critical_chance_per_rank = 0.05
        total_critical_chance = critical_chance_per_rank * rank
        random_number = random.random()
        if random_number <= total_critical_chance:
            self.talent_bonus_damage += self.damage
    
    def ambush_activation(self, rank):
        DAMAGE = self.damage
        target = self.get_target()
        armor_penalty = 0
        target.take_damage(DAMAGE, 'physical', armor_penalty)
    
    def gladiator_activation(self, rank):
        damage_bonus_per_rank = 4
        total_damage_bonus = damage_bonus_per_rank * rank
        #def actiatio
        #armor_bonus_per_rank = 1
        if len(Config.party_heroes) == 1:
            self.talent_bonus_damage += total_damage_bonus

    #testing more powerful spell mastery talents
    def lightning_activation(self, rank):
        damage_bonus_per_rank = self.level #// 2
        total_damage_bonus = damage_bonus_per_rank * rank
        if self.spells[0]['type'] == 'lightning':
            self.talent_bonus_damage += total_damage_bonus

    def acid_activation(self, rank):
        damage_bonus_per_rank = self.level #// 2
        total_damage_bonus = damage_bonus_per_rank * rank
        if self.spells[0]['type'] == 'acid':
            self.talent_bonus_damage += total_damage_bonus
    
    def fire_activation(self, rank):
        damage_bonus_per_rank = self.level #// 2
        total_damage_bonus = damage_bonus_per_rank * rank
        if self.spells[0]['type'] == 'fire':
            self.talent_bonus_damage += total_damage_bonus
    
    def cold_activation(self, rank):
        damage_bonus_per_rank = self.level #// 2
        total_damage_bonus = damage_bonus_per_rank * rank
        if self.spells[0]['type'] == 'cold':
            self.talent_bonus_damage += total_damage_bonus
    
    def nature_activation(self, rank):
        damage_bonus_per_rank = self.level #// 2
        total_damage_bonus = damage_bonus_per_rank * rank
        if self.spells[0]['type'] == 'nature':
            self.talent_bonus_damage += total_damage_bonus