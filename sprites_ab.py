"""
Module for handling all non-hero and non-animation sprites in the game.

This module includes classes for managing various types of game sprites, such as monsters, 
adventures, locations, buttons, followers, talent cards, equipment slots, and equipment. 
Some classes provide methods for specific behaviors and interactions.
"""

import pygame as pg
from data_ab import get_data
from config_ab import Config
import numpy as np
import pandas as pd
import random
import sys

monster_data = get_data('monsters')
weapons_data = get_data('weapons')
follower_data = get_data('followers')

class Monster(Config, pg.sprite.Sprite):
    """
    Class for handling monster sprites, their attributes, and behaviors.

    This class manages monster objects, including attacking, taking damage, and other related behaviors.
    """

    def __init__(self, groups, pos, monster_type: str):
        """Initialize a monster with position, type and monster data."""
        super().__init__()
        pg.sprite.Sprite.__init__(self, groups) 
        mob = pg.image.load('./ab_images/monster/' + monster_type + '.png').convert_alpha()
        HEIGHT = mob.get_height()
        WIDTH = mob.get_width()
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.type = monster_type
        self.is_monster = True
        self.is_player = False
        self.is_follower = False
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
        self.attack_type = 'claw'

        self.debuff_dict = {'speed': 0, 'damage': 0, 'menace': 0, 'armor': 0}
        self.special_attacks = {'rend': 0, 'regenerate': 0, 'scare': 0, 'summon_skeleton': 0, 'poison_breath': 0, 'trample': 0, 'lightning_breath': 0}
        #keys are names of special attack ativations, values number of times mob can execute
        #adjust value -= 1 after executing special attack

    def take_debuff(self, stat: str, debuff: int):
        """Apply a debuff to a specific stat."""
        if stat == 'menace':
            self.debuff_dict[stat] += debuff
        else:
            self.debuff_dict[stat] -= debuff

    def total_stat(self, stat):
        """Calculate the total value of a stat, accounting for debuffs."""
        base_value = getattr(self, stat)
        debuff_value = self.debuff_dict[stat]
        total_value = max(0, base_value + debuff_value)
        return total_value
    
    def get_target(self):
        """Determine and return a target based on menace probabilities."""
        total_menace = sum(hero.total_stat('menace') for hero in Config.party_heroes)
        prob = [hero.total_stat('menace')/total_menace for hero in Config.party_heroes]
        target = np.random.choice(Config.party_heroes, p=prob)
        return target

    def melee_attack(self, target):
        """Perform a melee attack on the target."""
        self.animation = False
        DAMAGE = self.total_stat('damage')
        LOG_DAMAGE = max(0, DAMAGE - target.total_stat('armor'))
        log_entry = (self.name, LOG_DAMAGE, target.name)
        Config.combat_log.append(log_entry)
        target.take_damage(DAMAGE, 'physical', self)
    
    def monster_action(self, target):
        """Execute an action based on the monster's type."""
        pass
        #if special action != 0:
        #special action -=1, execute special
        #if weapon = spell
            #cast spell
        #else:
        #melee

        #attribute normal/tough/boss
        #if boss
        #run attack list
        #troll berserk: melee_attack, rend, attack, regenerate

    def take_damage(self, damage_amount, damage_type, armor_penalty):
        """Reduce health based on damage taken."""
        ARMOR = max(0, self.total_stat('armor') - armor_penalty)
        if damage_type == 'physical':
            taken_damage = max(0, damage_amount - ARMOR)
        else:
            taken_damage = damage_amount
        self.health -= taken_damage

    def draw_health_bar(self, width=100, height=10, border_width_factor=0.01):
        """Draw the health bar for the monster."""
        health_ratio = self.health / self.max_health
        bar_width = int(width * health_ratio)
        border_width = int(width * border_width_factor)
        bar_x = self.pos_x - (width / 2) + (self.width / 2)
        pg.draw.rect(self.screen, self.black, [bar_x - border_width, self.pos_y - 10 - border_width, width + 2 * border_width, height + 2 * border_width])
        pg.draw.rect(self.screen, self.red, [bar_x, self.pos_y - 10, bar_width, height])
    
class Adventure(pg.sprite.Sprite):
    """
    Class for handling adventure sprites used in the WorldMap class.

    This class manages adventure sprites, including their initialization and interaction on the world map.
    """

    def __init__(self, pos, groups, desc: str, name: str, child):
        """Initialize an adventure sprite with its attributes."""
        super().__init__(groups)
        scenery = pg.image.load('./ab_images/map/' + name + '.png').convert_alpha()
        height = scenery.get_height()
        width = scenery.get_width()
        scenery_size_scalar = 9
        self.height = height / scenery_size_scalar
        self.width = width / scenery_size_scalar
        self.pos_x = Config.width * float(pos[0])
        self.pos_y = Config.height * float(pos[1])
        self.pos = (self.pos_x, self.pos_y)
        self.image = pg.transform.smoothscale(scenery, (self.width, self.height))
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))
        self.desc = desc
        self.name = name
        self.child = child
        
class Location(pg.sprite.Sprite):
    """
    Class for handling location sprites used in the Path class.

    This class manages location sprites, including their attributes and behaviors within the game paths.
    """

    def __init__(self, groups, df, width_gap):
        """Initialize a location sprite with its attributes."""
        super().__init__(groups)
        # Assign id, name, type, y_coord, size_scalar, tier, depth, desc, image_name, parent1, parent2, child1, child2
        for stat_name in df.index:
            setattr(self, stat_name, int(df[stat_name]) if str(df[stat_name]).isdigit() else df[stat_name])

        scenery = pg.image.load('./ab_images/location/' + self.image_name + '.png').convert_alpha()
        self.height = scenery.get_height()
        self.width = scenery.get_width()
        self.width_gap = width_gap
        self.pos_x = Config.width * (self.width_gap * self.depth)
        self.pos_y = Config.height * float(self.y_coord)
        self.pos = (self.pos_x, self.pos_y)
        self.image = pg.transform.smoothscale(scenery, ((self.width / self.size_scalar), (self.height / self.size_scalar)))
        self.rect = self.image.get_rect(center = (self.pos_x, self.pos_y))

class Button(Config, pg.sprite.Sprite):
    """
    Class for handling button sprites and player interactions.

    This class manages the drawing and interaction of buttons in the game.
    """

    def __init__(self, groups, text, font_name, font_size, text_color, center):
        """Initialize a button with its properties and render its text."""
        super().__init__() 
        pg.sprite.Sprite.__init__(self, groups) 

        self.text = text
        self.font = pg.font.SysFont(font_name, font_size)
        self.text_color = text_color
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect()
        self.button_color = self.grey
        padding_x = 20 
        padding_y = 10
        button_width = text_rect.width + 2 * padding_x
        button_height = text_rect.height + 2 * padding_y
        self.image = pg.Surface((button_width, button_height))
        self.image.fill(self.button_color)
        self.image.blit(text_surface, (padding_x, padding_y))
        self.rect = self.image.get_rect(center=center)
        self.border_width = 2
        self.border_color = (self.black)
        self.item_sold = False
        self.draw_border()

    def draw_border(self):
        """Draw the border of the button."""
        pg.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_width)

class Follower(Config, pg.sprite.Sprite):
    """
    Class for handling follower sprites, their attributes, and attack behavior.

    This class manages follower objects, including their attributes and attack mechanisms.
    """

    def __init__(self, follower_name: str, follower_type: str, master):
        """Initialize a follower with its properties and master."""
        super().__init__()
        self.following = master
        self.type = follower_type 
        self.name = follower_name
        self.attack_type = 'melee'
        self.is_follower = True
        self.is_player = False
        self.is_monster = False
        self.animation = False
        self.attacked = False

        self.df = follower_data[follower_data['type'] == self.type].reset_index(drop=True)
        # Assign stats type, size_scalar, damage, speed, offset_x, offset_y
        for stat_name in self.df.columns:
            setattr(self, stat_name, int(self.df.at[0, stat_name]) if str(self.df.at[0, stat_name]).isdigit() else self.df.at[0, stat_name])
 
    def total_stat(self, stat: str):
        """Return the total value of the specified stat."""
        base_value = getattr(self, stat)
        total_value = max(0, base_value)
        return total_value

    def get_target(self):
        """Determine and return a target based on menace probabilities."""
        total_menace = sum(monster.total_stat('menace') for monster in Config.room_monsters)
        prob = [monster.total_stat('menace')/total_menace for monster in Config.room_monsters]
        target = np.random.choice(Config.room_monsters, p=prob)
        return target

    def melee_attack(self, target):
        """Perform a melee attack on the target."""
        self.animation = False
        DAMAGE = self.total_stat('damage')
        armor_penalty = 0
        LOG_DAMAGE = max(0, DAMAGE - target.total_stat('armor'))
        log_entry = (self.name, LOG_DAMAGE, target.name)
        Config.combat_log.append(log_entry)
        target.take_damage(DAMAGE, 'physical', armor_penalty)
    
    def activate_talent_group(self, group):
        """Do nothing."""
        pass

class TalentCard(Config, pg.sprite.Sprite):
    """
    Class for handling talent card sprites from which players choose talents.

    This class manages the display and interaction of talent selection in the game.
    """

    def __init__(self, groups, df, pos_x, pos_y, hero, font):
        """Initialize a talent card with its properties and position."""
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
        self.rect = self.image.get_rect(topleft=self.pos)
        self.height = self.image.get_height()
        self.border_width = 2
        self.border_color = (self.black)
        self.draw_border()

    def draw_border(self):
        """Draw the border around the talent card."""
        pg.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_width)

    def render_texts(self):
        """Render and return the combined text surface for the talent card."""
        name_surface = self.font.render(self.name + ':', True, self.black)
        desc_surface = self.font.render(self.desc, True, self.black)
        #add padding to width and heights
        padding_x = 10 
        padding_y = 5
        combined_width = max(name_surface.get_width(), desc_surface.get_width()) + padding_x
        combined_height = name_surface.get_height() + desc_surface.get_height() + padding_y
        combined_surface = pg.Surface((combined_width, combined_height), pg.SRCALPHA)
        combined_surface.blit(name_surface, (5, 0))
        combined_surface.blit(desc_surface, (5, name_surface.get_height()))
        return combined_surface

class EquipmentSlot(Config):
    """
    Class for handling equipment slot sprites where items can be dragged to.

    This class manages the display and interaction of equipment slots in the game.
    """

    def __init__(self, name, pos_x, pos_y, width: int, height: int, slot_type: str, spot_number: int):
        """Initialize an equipment slot with its properties and position."""
        super().__init__()
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = pg.Rect(self.pos_x, self.pos_y, width, height)
        self.equipped_item = None
        self.slot_type = slot_type
        self.spot_number = spot_number
        self.border_width = 2
        self.default_color = (self.black)
        self.valid_spot_color = (self.green)
        self.border_color = (self.black)
        self.draw_border()

    def draw_border(self):
        """Draw the border of the equipment slot on the screen."""
        pg.draw.rect(self.screen, self.border_color, self.rect, self.border_width)

class Equipment(Config, pg.sprite.Sprite): 
    """
    Class for handling equipment sprites, their attributes, and images on screen.

    This class manages equipment objects, including their attributes and visual representation.
    """
    
    def __init__(self, name: str, item_type: str, slot_type: str, prefix: str, suffix: str, prefix_effect_type, prefix_effect, suffix_effect_type, suffix_effect, prefix_tier: int, suffix_tier: int):
        """Initialize an equipment object with attributes and image."""
        super().__init__()
        pg.sprite.Sprite.__init__(self)
        self.item_name = name #subtype
        self.item_type = item_type
        self.slot_type = slot_type
        self.inventory_spot = None
        icon_image = pg.image.load('./ab_images/icon/' + self.item_name + '_icon.png').convert_alpha()
        slot_side_length = self.screen_width // self.eq_slot_size_scalar
        icon_width = slot_side_length 
        icon_height = slot_side_length 
        self.pos_x = 0
        self.pos_y = 0
        self.image = pg.transform.smoothscale(icon_image, (icon_width, icon_height))
        self.rect = self.image.get_rect(topleft = (self.pos_x, self.pos_y))

        self.base_damage = None
        if self.item_type == 'weapon':
            weapon_df = weapons_data[weapons_data['name'] == self.item_name].reset_index(drop=True)
            damage = weapon_df.loc[0, 'base_damage']
            self.base_damage = damage
        self.prefix = prefix
        self.suffix = suffix
        self.prefix_tier = prefix_tier
        self.suffix_tier = suffix_tier
        self.modifier_tier = self.prefix_tier + self.suffix_tier
        self.speed_mod = 1

        self.prefix_effect_type = prefix_effect_type
        self.prefix_effect = prefix_effect
        self.suffix_effect_type = suffix_effect_type
        self.suffix_effect = suffix_effect
        self.buy_value = None
        self.sell_value = self.modifier_tier * 4

    @property
    def desc(self):
        """Return a formatted description of the equipment."""
        prefix_cap = self.prefix.capitalize()
        name_cap = self.item_name.capitalize()
        if self.suffix:
            words = self.suffix.split()
            words[1] = words[1].capitalize()
            suffix_cap = ' '.join(words)
        else:
            suffix_cap = self.suffix
        return f'{prefix_cap} {name_cap} {suffix_cap}'

    @property
    def item_prefix_effect(self):
        """Return the prefix effect details as a tuple."""
        return (self.prefix_effect, self.prefix_tier, self.prefix_effect_type)
    
    @property
    def item_suffix_effect(self):
        """Return the suffix effect details as a tuple."""
        return (self.suffix_effect, self.suffix_tier, self.suffix_effect_type)
