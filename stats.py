import pygame as pg
from csv import DictReader
from states import States
import json

class Data:
    def __init__(self):
        pass
    def monster_data():
        with open('./ab_data/monsters.csv', "r") as mobs:
            mob_reader = DictReader(mobs)
            monster_stats = list(mob_reader)
            mdata = {monster["name"]: monster for monster in monster_stats}
            return mdata       
        
    def hero_data():
        with open('./ab_data/heroes.csv', "r") as hero:
            hero_reader = DictReader(hero)
            hero_stats = list(hero_reader)
            hdata = {hero["class"]: hero for hero in hero_stats}
            return hdata

    def talent_data(type):
        with open('./ab_data/talents/' + type + '_talents.csv', "r") as talent:
            talent_reader = DictReader(talent)
            talent_stats = list(talent_reader)
            tdata = {talent["name"]: talent for talent in talent_stats}
            return tdata

    def spell_data():
        with open('./ab_data/spells.csv', "r") as spells:
            spell_reader = DictReader(spells)
            spell_stats = list(spell_reader)
            sdata = {spell["name"]: {k: int(v) if v.isdigit() else v for k, v in spell.items()} for spell in spell_stats}
            return sdata
    
    def map_data():
        with open('./ab_data/map.csv', "r") as map:
            map_reader = DictReader(map)
            map_stats = list(map_reader)
            adata = {map["name"]: map for map in map_stats}
            return adata
    
    def location_data(name):
        with open('./ab_data/' + name + '/location.csv', "r") as loc:
            loc_reader = DictReader(loc)
            loc_stats = list(loc_reader)
            ldata = {loc["desc"]: loc for loc in loc_stats}
            return ldata
     
    def arrow_data(name):
        with open('./ab_data/' + name + '/arrow.csv', "r") as arr:
            arr_reader = DictReader(arr)
            arr_stats = list(arr_reader)
            rdata = {arr["name"]: arr for arr in arr_stats}
            return rdata
    
    def loc_tree_data(name):
        with open('./ab_data/' + name + '/loc_tree.json', "r") as tree:
            loc_tree = json.load(tree)
            return loc_tree

class Stats():
    def __init__(self):
        self.level_cost = {1: "2", 2: "15", 3: "30", 4: "50", 5: "75"} #current level and exp needed for next
        self.abilities = {"bard": {}, "cleric": {}, "barbarian": {}, "ranger": {}, "thief": {}, "paladin": {}, "warrior": {}, "wizard": {}}
        self.level_health = {"bard": 2, "cleric": 4, "barbarian": 5, "ranger": 4, "thief": 3, "paladin": 4, "warrior": 5, "wizard": 2}
        self.monsters = Data.monster_data()
        self.heroes = Data.hero_data()
        self.map = Data.map_data()
        self.spells = Data.spell_data()
        #self.talents = Data.talent_data(type)
        #Clerics start with domain, create talent list for each domain

    def add_talent(self, hero: object, name: str, type: str):
        talents = Data.talent_data(hero.type)
        #spells = Data.spell_data()
        if type == "spell":
            hero.talents.append(name) #effect in talent data
            hero.spells.append(self.spells[(talents[name]["effect"])])
        elif type == "stat":
            hero.talents.append(name)
            stat_bonus = talents[name]["effect"]
            stat_name, stat_val_str = stat_bonus.split()
            stat_val = int(stat_val_str)
            if hasattr(hero, stat_name):
                old_val = getattr(hero, stat_name)
                new_val = old_val + stat_val
                setattr(hero, stat_name, new_val)
        elif type == "m_stat":
            hero.talents.append(name)
            #speed 1 damage 1
        elif type == "song":
            hero.talents.append(name)
        elif type == "domain":
            hero.talents.append(name)
        elif type == "special":
            hero.talents.append(name)
        #need special, song
        
    def levelup(self, hero):
        hero.level += 1
        hero.next_level = int(self.level_cost[hero.level])
        hero.health += hero.level
        hero.max_health += self.level_health[hero.type]
             