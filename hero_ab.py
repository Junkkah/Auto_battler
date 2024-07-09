"""
Hero module for managing hero characters in the game.

Contains:
    - Hero: Represents a hero character with attributes, stats, worn items, and methods for actions such as 
      displaying the hero's name and health bar, attacking, and casting spells.
"""

import pygame as pg
from data_ab import row_to_dict, get_data
from config_ab import Config
from sprites_ab import Equipment
from items_ab import SuffixActivations
import numpy as np
import pandas as pd
import random

hero_data = get_data('classes')
exp_data = get_data('experience')
spells_data = get_data('spells')

class Hero(Config, pg.sprite.Sprite):
    """
    Represents a hero character used by the player to battle monsters.
    """

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
        self.is_follower = False
        self.is_monster = False
        self.type = hero_type
        self.inventory_spot = None
        self.inventory_spot_number = None

        self.level = 1
        self.exp_df = exp_data
        self.next_level = self.exp_df.at[0, 'exp']
        self.worn_items = {'head': None, 'body': None, 'hand1': None, 'consumable': None}
        #self.worn_items = {'head': None, 'body': None, 'hand1': None, 'hand2': None, 'consumable': None}
        #"hand2": [[0.37, 0.27], [0.57, 0.27], [0.77, 0.27]],

        self.df = hero_data[hero_data['type'] == self.type].reset_index(drop=True)
        # Assign stats type, health, max_health, damage, speed, exp, menace, armor, attack_type
        for stat_name in self.df.columns:
            setattr(self, stat_name, int(self.df.at[0, stat_name]) if str(self.df.at[0, stat_name]).isdigit() else self.df.at[0, stat_name])

        self.unarmed_damage = 1
        self.magic_power = 0
        self.songmaster_rank = 0
        self.critical = 0
        self.evasion = 0
        self.spells = []
        self.talents = []
        self.active_spell = None

        self.talent_bonus = {'speed': 0, 'damage': 0, 'menace': 0, 'armor': 0, 'magic_power': 0, 'critical': 0, 'evasion': 0}
        self.spell_mastery = {'fire': 0, 'lightning': 0, 'acid': 0, 'cold': 0, 'nature': 0}
        self.talent_groups = {'combat': {}, 'location': {}, 'map': {}, 'song': {}} #combat -> off/def
        self.item_stats_dict = {'speed': 0, 'damage': 0, 'menace': 0, 'armor': 0, 'magic_power': 0, 'critical': 0, 'evasion': 0}

        self.talent_activations = {}
        #single activation talent: 'stone_skin': 1
        #single activation melee_attack, spell_attack, take_damage
        self.aura = None
        self.enemy_armor_penalty = 0

    def evaluate_spells(self):
        #select spells which have highest masteries
        max_values = max(self.spell_mastery.values())
        masteries = [key for key, value in self.spell_mastery.items() if value == max_values]
        mastery_spells = [spell for spell in self.spells if spell.get('type') in masteries]
        if len(Config.room_monsters) > 1:
            #filter out single target spells if multiple targets
            aoe_spells = [aoe_spell for aoe_spell in mastery_spells if aoe_spell.get('area') == 1]
            #check if valid aoe spells exist
            if aoe_spells:
                mastery_spells = aoe_spells

        max_damage = max(dam_spell.get('damage') for dam_spell in mastery_spells)
        max_damage_spells = [max_spell for max_spell in mastery_spells if max_spell.get('damage') == max_damage]
        chosen_spell = random.choice(max_damage_spells)
        return chosen_spell
        
    def evaluate_action(self):
        if attack_type == 'spell':
            self.spell_attack()
        if attack_type == 'song':
            self.song_attack()
        else:
            #self.special_attack()
            self.melee_attack()
        
    #if type == 'stat', 'combat', 'instant'
    #need separate activation methods for stat, combat and instant
    def activate_aura(self):
        if self.aura:
            aura_stat_name, stat_val_str = self.aura.split()
            aura_stat_val = int(stat_val_str)
            Config.aura_bonus[aura_stat_name] += aura_stat_val

    #activated start of combat
    def activate_item_stats(self):
        for item_slot, item in self.worn_items.items():
            if item is not None:
                item_effect = self.worn_items[item_slot].item_prefix_effect #return (effect, tier, effect_type)
                effect_name = item_effect[0]
                effect_tier = item_effect[1]
                effect_type = item_effect[2]
                if effect_name is not None and effect_type == 'stat':
                    self.item_stats_dict[effect_name] += effect_tier


    def activate_item_effects(self):
        for item_slot, item in self.worn_items.items():
            if item is not None:
                item_effect = self.worn_items[item_slot].item_suffix_effect #return (effect, tier, effect_type)
                effect_name = item_effect[0]
                effect_tier = item_effect[1]
                effect_type = item_effect[2]
                if effect_name is not None and effect_type != 'stat':
                    if item.item_type == 'consumable':
                        method_name = f'{effect_name}_activation'
                        activation_method = getattr(self, method_name)
                        activation_method(effect_tier)
                        self.worn_items[item_slot] = None

    def activate_def_item_effects(self, taken_damage: int, damage_type: str, attacker): 
        for item_slot, item in self.worn_items.items():
            if item is not None:
                item_effect = self.worn_items[item_slot].item_suffix_effect #return (effect, tier, effect_type)
                effect_name = item_effect[0]
                effect_type = item_effect[2]
                if effect_name is not None and effect_type == 'defence':
                    method_name = effect_name
                    activation_method = getattr(SuffixActivations, method_name)
                    activation_method(taken_damage, damage_type, attacker, self)
    
    #returns values: can active only single item
    def activate_off_item_effects(self, damage: int, armor_penalty: int, crit_multi: int, target): 
        for item_slot, item in self.worn_items.items():
            if item is not None:
                item_effect = self.worn_items[item_slot].item_suffix_effect #return (effect, tier, effect_type)
                effect_name = item_effect[0]
                effect_type = item_effect[2]
                if effect_name is not None and effect_type == 'offence':
                    method_name = effect_name
                    activation_method = getattr(SuffixActivations, method_name)
                    damage, armor_penalty, crit_multi = activation_method(damage, armor_penalty, crit_multi, target, self)
        return damage, armor_penalty, crit_multi

    def total_stat(self, stat: str):
        base_value = getattr(self, stat)
        item_value = self.item_stats_dict[stat]
        weapon_value = 0
        bonus_value = self.talent_bonus[stat]
        self.talent_bonus[stat] = 0
        if stat == 'damage':
            if self.worn_items['hand1']:
                weapon_value = self.worn_items['hand1'].base_damage
            else:
                weapon_value = self.unarmed_damage
        return base_value + item_value + bonus_value + weapon_value + Config.aura_bonus[stat]

    def get_target(self):
        total_menace = sum(monster.total_stat('menace') for monster in Config.room_monsters)
        prob = [monster.total_stat('menace')/total_menace for monster in Config.room_monsters]
        target = np.random.choice(Config.room_monsters, p=prob)
        return target

    #calling static methods
    #combat -> off/def
    def activate_talent_group(self, group):
        for talent_effect, talent_info in self.talent_groups[group].items():
            activation_method = talent_info['activation_method']
            rank = talent_info['rank']
            activation_method(self, rank)
            
    def critical_hit(self):
        crit_stat = self.total_stat('critical')
        critical_chance = crit_stat * 0.10
        random_number = random.random()
        if random_number <= critical_chance:
            return True
        else:
            return False
    
    def evade_attack(self):
        evade = self.total_stat('evasion')
        evasion_chance = evade * 0.05
        random_number = random.random()
        if random_number <= evasion_chance:
            return True
        else:
            return False

    #separate melee_hit() that performs hit
    #leave melee_attack() as method that activates item/talents and calls melee_hit
    def melee_attack(self, target):
        self.animation = False
        DAMAGE = self.total_stat('damage')
        critical_multiplier = 2

        armor_penalty = self.enemy_armor_penalty
        DAMAGE, armor_penalty, critical_multiplier = self.activate_off_item_effects(DAMAGE, armor_penalty, critical_multiplier, target)
        if self.critical_hit():
            DAMAGE = critical_multiplier * DAMAGE

        LOG_DAMAGE = DAMAGE - max(0, target.total_stat('armor') - armor_penalty)
        log_entry = (self.name, LOG_DAMAGE, target.name)
        Config.combat_log.append(log_entry)
        target.take_damage(DAMAGE, 'physical', armor_penalty)
        self.enemy_armor_penalty = 0

    def spell_attack(self, spell: dict, target):
        damage_type = spell['type']
        self.animation = False
        DAMAGE = spell['damage'] + (self.spell_mastery[damage_type] * ((self.level // 2) + 1)) + self.total_stat('magic_power')
        armor_penalty = self.enemy_armor_penalty
        self.enemy_armor_penalty = 0

        if spell['area'] == 1:
            log_entry = (self.name, DAMAGE, 'ALL')
            Config.combat_log.append(log_entry)
            for target_mob in Config.room_monsters:
                target_mob.take_damage(DAMAGE, damage_type, armor_penalty)
        if spell['area'] == 0:
            #target = self.get_target()
            log_entry = (self.name, DAMAGE, target.name)
            Config.combat_log.append(log_entry)
            target.take_damage(DAMAGE, damage_type, armor_penalty)

    def song_attack(self):
        #actual song attack is handled by talent group activation
        #handle song group activation here
        #add magic_power to songs-dome something about healing
        self.animation = False
        log_entry = (self.name, 'song', 'everyone')
        Config.combat_log.append(log_entry)

    def take_damage(self, damage_amount: int, damage_type: str, attacker):
        if damage_type == 'physical':   
            armor = self.total_stat('armor')
            taken_damage = max(0, damage_amount - armor)
        else:
            taken_damage = damage_amount
        self.activate_def_item_effects(taken_damage, damage_type, attacker)
        if self.evade_attack():
            taken_damage = 0
        self.health -= taken_damage
    
    def gain_max_health(self, gained_max_health:int):
        """Increase hero's maximum health by the given amount."""
        self.max_health += gained_max_health

    def gain_health(self, gained_health: int):
        """Increase hero's health by the given amount, up to hero's maximum health."""
        self.health = min(self.health + gained_health, self.max_health)

    #move to levelup
    #def gain_level(self):
    #    self.level += 1
    #    self.next_level = self.exp_df.loc[self.exp_df['level'] == self.level, 'exp'].iloc[0]
    #    self.max_health += self.level_health
    #    self.gain_health(self.level_health)  
    
    def equip_starting_weapon(self):
        if self.attack_type not in ['spell', 'song']:
            weapon = Equipment(self.attack_type, 'weapon', 'hand1', '', '', None, None, None, None, 0, 0)
            self.worn_items['hand1'] = weapon

    def equip_item(self, item: object):
        slot = item.slot_type
        self.worn_items[slot] = item
    
    def drop_item(self, slot: object):
        self.worn_items[slot] = None

    def add_stat(self, stat_bonus: str):
        stat_name, stat_val_str = stat_bonus.split()
        stat_val = int(stat_val_str)
        old_val = getattr(self, stat_name, 0)
        new_val = old_val + stat_val
        setattr(self, stat_name, new_val) 
    
    def display_name(self):
        health_bar_height = 20
        OFFSET = (self.screen_height / self.offset_divisor) + health_bar_height
        COORDS_INFO_X = self.pos_x
        COORDS_INFO_Y = self.pos_y + OFFSET
        info = self.name.capitalize()
        info_text = self.info_font.render(info, True, self.black)
        info_text_rect = info_text.get_rect(topleft=(COORDS_INFO_X, COORDS_INFO_Y))
        self.screen.blit(info_text, info_text_rect)

    def draw_health_bar(self, width=100, height=10, border_width_factor=0.01):
        health_ratio = self.health / self.max_health
        bar_width = int(width * health_ratio)
        border_width = int(width * border_width_factor)

        bar_x = self.pos_x - (width / 2) + (self.width / 2)
        pg.draw.rect(self.screen, self.black, [bar_x - border_width, self.pos_y + self.height + 10 - border_width, width + 2 * border_width, height + 2 * border_width])
        pg.draw.rect(self.screen, self.red, [bar_x, self.pos_y +self.height + 10, bar_width, height])

    def draw_frame(self):
        pg.draw.rect(self.screen, self.red, [self.pos_x, self.pos_y, self.width, self.height], self.frame_width)
    
    def fire_spell_activation(self, rank):
        if rank > 1:
            spell_name = 'fireball'
        else:
            spell_name = 'flame_bolt'
        fire_spell = row_to_dict(spells_data, spell_name)
        self.spell_attack(fire_spell)

    #used for talent and item
    def healing_activation(self, rank):
        total_rank = rank
        healing_per_rank = 3
        total_healing = healing_per_rank * total_rank
        self.gain_health(total_healing)
