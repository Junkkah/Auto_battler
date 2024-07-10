"""
Items module for managing item creation and activation in the game.

Contains:
    - ItemManager: Handles the creation of magic item loot and various helper functions for managing items.
    - SuffixActivation: Manages the activation of item effects dynamically.
"""

import pygame as pg
from config_ab import Config
from sprites_ab import Equipment
from data_ab import get_json_data, get_affix
import random

class ItemManager(Config):
    """
    Handles the creation of magic item loot and various helper functions for managing items.

    This class includes methods to generate items with magical properties and provides helper functions
    for item management within the game.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def item_to_backpack(item):
        sorted_keys = sorted(Config.party_backpack.keys(), key=lambda x: int(x.split('slot')[1]))
        for key in sorted_keys:
            if Config.party_backpack[key] is None:
                Config.party_backpack[key] = item
                break 
    
    @staticmethod
    def create_magic_item(item_type, subtype, max_power):
        min_power = max(1, max_power // 2)
        power = random.randint(min_power, max_power)
        slot_type_mapping = {'weapon': 'hand1', 'armor': subtype}
        prefix_effect_type = None
        prefix_effect = None
        suffix_effect_type = None
        suffix_effect = None
        prefix_tier = 0
        suffix_tier = 0

        if item_type == 'consumable':
            tier = power
            if tier > 5:
                tier = 5
            tier_name = 'tier_' + str(tier)
            affix_df = get_affix(subtype, 'suffix')
            random_affix = affix_df.sample(n = 1)
            suffix = random_affix[tier_name].iloc[0]
            prefix = ''
            effect_type = random_affix['mod_type'].iloc[0]
            effect = random_affix['mod_effect'].iloc[0]
            suffix_effect_type = effect_type
            suffix_effect = effect
            suffix_tier = tier
     
        elif power == 1:
            affix_df = get_affix(item_type, 'prefix')
            affix_df = affix_df[affix_df['mod_ratio'] == 1]
            random_affix = affix_df.sample(n = 1)
            prefix = random_affix['tier_1'].iloc[0]
            suffix = ''
            effect_type = random_affix['mod_type'].iloc[0]
            effect = random_affix['mod_effect'].iloc[0]
            prefix_effect_type = effect_type
            prefix_effect = effect
            prefix_tier = power

        elif power > 11:
            max_prefix_power = 10
            suffix_power = power - max_prefix_power
            prefix_df = get_affix(item_type, 'prefix')
            random_prefix = prefix_df.sample(n = 1)
            mod_ratio = random_prefix['mod_ratio'].iloc[0]
            mod_power = max_prefix_power // mod_ratio
            prefix_tier = mod_power
            if mod_ratio == 1:
                tier = mod_power // 2
            else:
                tier = mod_power

            tier_name = 'tier_' + str(tier)
            prefix = random_prefix[tier_name].iloc[0]
            effect_type = random_prefix['mod_type'].iloc[0]
            effect = random_prefix['mod_effect'].iloc[0]
            prefix_effect_type = effect_type
            prefix_effect = effect

            suffix_df = get_affix(item_type, 'suffix')
            suffix_mod_ratio = 2
            tier = suffix_power // suffix_mod_ratio
            tier_name = 'tier_' + str(tier)
            suffix_tier = tier

            suffix_row = suffix_df[suffix_df[tier_name].notna()]
            suffix = suffix_df.loc[suffix_df[tier_name].notna(), tier_name].values[0]

            effect_type = suffix_row['mod_type'].iloc[0]
            effect = suffix_row['mod_effect'].iloc[0]
            suffix_effect_type = effect_type
            suffix_effect = effect
        
        else:
            #adjust +1/+2 = tier 1 for 1/1 items
            affix_df = get_affix(item_type, 'prefix')
            random_affix = affix_df.sample(n = 1)

            mod_ratio = random_affix['mod_ratio'].iloc[0]
            mod_power = power // mod_ratio
            prefix_tier = mod_power
            if mod_ratio == 1:
                tier = mod_power // 2
            else:
                tier = mod_power

            tier_name = 'tier_' + str(tier)
            prefix = random_affix[tier_name].iloc[0]
            suffix = ''
            effect_type = random_affix['mod_type'].iloc[0]
            effect = random_affix['mod_effect'].iloc[0]
            prefix_effect_type = effect_type
            prefix_effect = effect

        slot_type = slot_type_mapping.get(item_type, item_type)
        magic_item = Equipment(subtype, item_type, slot_type, prefix, suffix, prefix_effect_type, prefix_effect, suffix_effect_type, suffix_effect, prefix_tier, suffix_tier)
        return magic_item

    @staticmethod
    def create_random_item(item_probabilities):
        item_type = random.choices(list(item_probabilities.keys()), weights=[40, 45, 15])[0]
        subtype = random.choices(item_probabilities[item_type]['types'], weights=item_probabilities[item_type]['prob'])[0]
        item_power = max(1, Config.current_location.tier // 2)
        created_item = ItemManager.create_magic_item(item_type, subtype, item_power)
        return created_item
    
    @staticmethod
    def create_item_loot():
        looted_items = []
        item_probabilities = get_json_data('item_probabilities')
        drop_chance_bonus = (Config.current_location.tier / 100)
        for monster in Config.room_monsters:
            #number_of_loot_rolls attribute, 1-5. Repeat for each 
            item_drop_chance = monster.loot_roll + drop_chance_bonus + Config.magic_find
            if random.random() <= item_drop_chance:
                #random_item = self.create_random_item(item_probabilities)
                random_item = ItemManager.create_random_item(item_probabilities)
                looted_items.append(random_item)
        return looted_items  
    
    @staticmethod
    def activate_book(hero, book):
        #activate_stat_book
        #spell_books, exp_books, talent_books, trait_books
        tier = book.modifier_tier
        effect_mapping = {1: 'speed', 2: 'menace', 3: 'max_health', 4: 'damage', 5: 'armor'}
        effect_strength_mapping = {'speed': '2', 'menace': '2', 'max_health': '5', 'damage': '2', 'armor': '1'}
        effect = effect_mapping.get(tier)
        strength = effect_strength_mapping.get(effect)
        stat_bonus = effect + ' ' + strength
        hero.add_stat(stat_bonus)

class SuffixActivations(Config):
    """
    Manages the activation of item effects dynamically.

    This class contains methods to dynamically activate the effects of items based on their suffixes.
    """
    
    def __init__(self):
        super().__init__()

    #only reflect phys damage
    @staticmethod
    def reflect(damage, damage_type, attacker, hero):
        if damage_type == 'physical':
            reflected_damage = max(1, damage // 10)
            armor_penalty = 100
            attacker.take_damage(reflected_damage, 'physical', armor_penalty)
            #how to stop two reflects looping?
            LOG_DAMAGE = reflected_damage - max(0, attacker.total_stat('armor') - armor_penalty)
            log_entry = (hero.name, LOG_DAMAGE, attacker.name)
            Config.combat_log.append(log_entry)
    
    @staticmethod
    def revive(damage, damage_type, attacker, hero):
        if damage >= hero.health:
            hero.gain_health(damage)

    @staticmethod
    def regenerate(damage, damage_type, attacker, hero):
        regeneration_rate = 1
        hero.gain_health(regeneration_rate)
    
    #perform additional attack on non-target monster, if one exists
    @staticmethod
    def cleave(damage, armor_penalty, crit_multi, target, hero):
        if len(Config.room_monsters) > 1:
            for monster in Config.room_monsters:
                if monster is not target:
                    if hero.critical_hit():
                        damage = crit_multi * damage
                    LOG_DAMAGE = DAMAGE - max(0, target.total_stat('armor') - armor_penalty)
                    log_entry = (hero.name, LOG_DAMAGE, target.name)
                    Config.combat_log.append(log_entry)
                    target.take_damage(damage, 'physical', armor_penalty)
                    break
        return damage, armor_penalty, crit_multi
    
    @staticmethod
    def slaughter(damage, armor_penalty, crit_multi, target, hero):
        crit_multi = 3
        return damage, armor_penalty, crit_multi

    @staticmethod
    def crush(damage, armor_penalty, crit_multi, target, hero):
        armor_penalty = 3
        return damage, armor_penalty, crit_multi