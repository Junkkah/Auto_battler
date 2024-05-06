import pygame as pg
from data_ab import row_to_dict, get_data, get_talent_data, get_json_data
from config_ab import Config
from sprites_ab import Equipment
import numpy as np
import pandas as pd
import random
import sys
from enum import Enum

hero_data = get_data('classes')
exp_data = get_data('experience')
spells_data = get_data('spells')
follower_data = get_data('followers')
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
        self.is_follower = False
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

        self.unarmed_damage = 1
        self.magic_power = 0
        self.critical = 0
        self.spells = []
        self.talents = []

        self.talent_bonus = {'speed': 0, 'damage': 0, 'menace': 0, 'armor': 0, 'magic_power': 0, 'critical': 0}
        self.spell_mastery = {'fire': 0, 'lightning': 0, 'acid': 0, 'cold': 0, 'nature': 0}
        self.talent_groups = {'combat': {}, 'location': {}, 'map': {}, 'song': {}}
        self.item_stats_dict = {'speed': 0, 'damage': 0, 'menace': 0, 'armor': 0, 'magic_power': 0, 'critical': 0}

        #when adding single activation talent, add new key/value pair to dict: 'stone_skin': 1
        #end of combat loop would need to reset activations to correct values if > 1
        self.talent_activations = {}

        self.aura = None
        self.enemy_armor_penalty = 0

    #def evaluate_spells(self):
        #check spell_book
        #check talents
        #if mastery or several, limit to mastery spells
        #if one mastery > others
        #if len monsters > 1, cast mastery aoe
            #if several, get most damage
            #if no aoe, get most damage
            #return chosen_spell
        #if no mastery
        #if len monsters > 1 cast aoe, most damage
        #else cast most damage
        


    
    #def evaluate_action(self, attack_type):
        #done before creating animation object
        #set acting, run eval, create animation object
        #requires weapon data in hero object
        
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
                item_effect = self.worn_items[item_slot].item_effect #return (effect, tier, effect_type)
                effect_name = item_effect[0]
                effect_tier = item_effect[1]
                effect_type = item_effect[2]
                if effect_name is not None and effect_type == 'stat':
                    self.item_stats_dict[effect_name] += effect_tier

    #activated when acting
    #divide combat effects to off/def 
    #activate off with attack()
    #activate def with take_damage()
    def activate_item_effects(self):
        for item_slot, item in self.worn_items.items():
            if item is not None:
                item_effect = self.worn_items[item_slot].item_effect #return (effect, tier, effect_type)
                effect_name = item_effect[0]
                effect_tier = item_effect[1]
                effect_type = item_effect[2]
                if effect_name is not None and effect_type != 'stat':
                    if item.item_type == 'consumable':
                        method_name = f'{effect_name}_activation'
                        activation_method = getattr(self, method_name)
                        activation_method(effect_tier)
                        self.worn_items[item_slot] = None

    def activate_book(self, book):
        #activate_stat_book
        tier = book.modifier_tier
        effect_mapping = {1: 'speed', 2: 'menace', 3: 'max_health', 4: 'damage', 5: 'armor'}
        effect_strength_mapping = {'speed': '2', 'menace': '2', 'health': '5', 'damage': '2', 'armor': '1'}
        effect = effect_mapping.get(tier)
        strength = effect_strength_mapping.get(effect)
        stat_bonus = effect + ' ' + strength
        self.add_stat(stat_bonus)

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

    def activate_talent_group(self, group):
        for talent_effect, talent_info in self.talent_groups[group].items():
            activation_method = talent_info['activation_method']
            rank = talent_info['rank']
            activation_method(rank)
    
    def critical_hit(self):
        crit_stat = self.total_stat('critical')
        critical_chance = crit_stat * 0.10
        random_number = random.random()
        if random_number <= critical_chance:
            return True
        else:
            return False

    def melee_attack(self):
        target = self.get_target()
        self.animation = False
        DAMAGE = self.total_stat('damage')
        if self.critical_hit():
            DAMAGE = 2 * DAMAGE
        armor_penalty = self.enemy_armor_penalty
        LOG_DAMAGE = DAMAGE - max(0, target.total_stat('armor') - armor_penalty)
        log_entry = (self.name, LOG_DAMAGE, target.name)
        Config.combat_log.append(log_entry)
        target.take_damage(DAMAGE, 'physical', armor_penalty)
        self.enemy_armor_penalty = 0

    def spell_attack(self, spell: dict):
        damage_type = spell['type']
        self.animation = False
        DAMAGE = spell['damage'] + (self.spell_mastery[damage_type] * self.level) #+ self.total_stat('magic_power')
        armor_penalty = self.enemy_armor_penalty
        self.enemy_armor_penalty = 0
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

    def take_damage(self, damage_amount: int, damage_type: str):
        #activate defensive talent
        if damage_type == 'physical':   
            armor = self.total_stat('armor')
            taken_damage = max(0, damage_amount - armor)
        else:
            taken_damage = damage_amount
        self.health -= taken_damage

    def gain_health(self, gained_health: int):
        self.health = min(self.health + gained_health, self.max_health)

    def gain_level(self):
        self.level += 1
        self.next_level = self.exp_df.loc[self.exp_df['level'] == self.level, 'exp'].iloc[0]
        self.max_health += self.level_health
        self.gain_health(self.level_health)  
    
    def equip_starting_weapon(self):
        if self.attack_type != 'spell':
            weapon = Equipment(self.attack_type, 'weapon', 'hand1', '', '', None, None, 0)
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

        #pilfer 2 would automatically upgrade activation method to rank 2?
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
        
        elif talent_type == 'spell_mastery':
            self.talents.append(talent_name)
            mastery_type = talents['effect']
            self.spell_mastery[mastery_type] += 1
        
        elif talent_type == 'once':
            self.talents.append(talent_name)
            effect = talents['effect']
            method, effect = effect.split()
            method_name = f'{method}_activation'
            activation_method = getattr(self, method_name)
            activation_method(effect)

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
    
    #TalentActivations()
    #@staticmethod
    #def invisibility_activation(hero, rank):
    #    hero.menace = 1
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
            surprised_monster.take_debuff('speed', total_speed_penalty)
    
    def reveal_activation(self, rank):
        armor_penalty_per_rank = 1
        total_armor_penalty = armor_penalty_per_rank * rank
        for revealed_monster in Config.room_monsters:
            revealed_monster.take_debuff('armor', total_armor_penalty)

    def berserk_activation(self, rank):
        #menace affect actions of monsters during their turns
        #causes the barb to have residual menace if 
        #monsters act before barb in next combat
        self.talent_bonus['menace'] = 0
        damage_bonus_per_rank = 3
        menace_bonus_per_rank = 2
        total_damage = damage_bonus_per_rank * rank
        total_menace = menace_bonus_per_rank * rank
        if self.health < self.max_health // 2:
            self.talent_bonus['damage'] += total_damage
            self.talent_bonus['menace'] += total_menace

    def crush_activation(self, rank):
        armor_pierced_per_rank = 2
        total_pierce = armor_pierced_per_rank * rank
        self.enemy_armor_penalty += total_pierce

    def smite_activation(self, rank):
        damage_per_rank = 2
        damage_type = 'holy'
        DAMAGE = damage_per_rank * rank
        armor_penalty = 0
        for target_mob in Config.room_monsters:
            target_mob.take_damage(DAMAGE, damage_type, armor_penalty)
    
    def smiting_activation(self, rank):
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

    def ambush_activation(self, rank):
        DAMAGE = self.worn_items['hand1'].base_damage
        target = self.get_target()
        armor_penalty = 0
        target.take_damage(DAMAGE, 'physical', armor_penalty)
    
    def gladiator_activation(self, rank):
        damage_bonus_per_rank = 4
        total_damage_bonus = damage_bonus_per_rank * rank
        armor_bonus_per_rank = 1
        total_armor_bonus = armor_bonus_per_rank * rank
        if len(Config.party_heroes) == 1:
            self.talent_bonus['damage'] += total_damage_bonus
            self.talent_bonus['armor'] += total_armor_bonus
    
    def inevitable_activation(self, rank):
        damage_increase_per_rank = 1
        total_damage_increase = damage_increase_per_rank * rank
        self.damage += total_damage_increase
    
    def bloodthirst_activation(self, rank):
        healing_per_rank = 2
        total_healing = healing_per_rank * rank
        self.gain_health(total_healing)
    
    def xtr_att_activation(self, rank):
        extra_attacks_per_rank = 1
        total_extra_attacks = extra_attacks_per_rank * rank
        self.melee_attack()
    
    def coordinate_activation(self, rank):
        menace_debuff_per_rank = 3
        total_menace_debuff = menace_debuff_per_rank * rank
        target = self.get_target()
        target.take_debuff('menace', total_menace_debuff)
    
    def entrap_activation(self, rank):
        armor_penalty_per_rank = 1
        total_armor_penalty = armor_penalty_per_rank * rank
        for entrapped_monster in Config.room_monsters:
            entrapped_monster.take_debuff('armor', total_armor_penalty)
    
    def follower_activation(self, effect):
        follower_type = effect
        follower_names = get_json_data('follower_names')
        name = random.choice(follower_names[follower_type])
        new_follower = Follower(name, follower_type, self)
        Config.party_followers.append(new_follower)
    
    def foll_dam_activation(self, effect):
        rank = int(effect)
        damage_increase_per_rank = 2
        total_damage_increase = damage_increase_per_rank * rank
        for follower in Config.party_followers:
            if follower.following == self:
                follower.damage += total_damage_increase

class Follower(Config, pg.sprite.Sprite):
    def __init__(self, follower_name: str, follower_type: str, master):
        Config.__init__(self)

        self.following = master
        self.type = follower_type #bear
        self.name = follower_name
        self.attack_type = 'melee'
        self.is_follower = True
        self.is_player = False
        self.animation = False
        self.attacked = False

        self.df = follower_data[follower_data['type'] == self.type].reset_index(drop=True)
        # Assign stats type, size_scalar, damage, speed, offset_x, offset_y
        for stat_name in self.df.columns:
            setattr(self, stat_name, int(self.df.at[0, stat_name]) if str(self.df.at[0, stat_name]).isdigit() else self.df.at[0, stat_name])
 
    def total_stat(self, stat: str):
        base_value = getattr(self, stat)
        total_value = max(0, base_value)
        return total_value

    def get_target(self):
        total_menace = sum(monster.total_stat('menace') for monster in Config.room_monsters)
        prob = [monster.total_stat('menace')/total_menace for monster in Config.room_monsters]
        target = np.random.choice(Config.room_monsters, p=prob)
        return target

    def melee_attack(self):
        target = self.get_target()
        self.animation = False
        DAMAGE = self.total_stat('damage')
        armor_penalty = 0
        LOG_DAMAGE = max(0, DAMAGE - target.total_stat('armor'))
        log_entry = (self.name, LOG_DAMAGE, target.name)
        Config.combat_log.append(log_entry)
        target.take_damage(DAMAGE, 'physical', armor_penalty)
