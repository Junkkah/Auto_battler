import pygame as pg
import csv
from csv import DictReader
from states import States
import json
import sqlite3
import pandas as pd

# Query and return data
def get_data(table: str) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')
    db.isolation_level = None
    # "SELECT * FROM Monsters WHERE name IN ('goblin', 'orc')"
    query = "SELECT * FROM " + table
    df = pd.read_sql_query(query, db)
    db.close()
    return df

def row_to_dict(dataframe, name) -> dict:
    name_index_df = dataframe.set_index('name')
    row_dict = name_index_df.loc[name].to_dict()
    return row_dict


class Data:
    def __init__(self):
        pass
    #
    def monster_data():
        with open('./ab_data/monsters.csv', "r") as mobs:
            mob_reader = DictReader(mobs)
            monster_stats = list(mob_reader)
            mdata = {monster["name"]: monster for monster in monster_stats}
            return mdata       
    #  
    def hero_data():
        with open('./ab_data/heroes.csv', "r") as hero:
            hero_reader = DictReader(hero)
            hero_stats = list(hero_reader)
            hdata = {hero["class"]: hero for hero in hero_stats}
            return hdata
    #
    def name_data():
        with open('./ab_data/names.csv', "r") as name:
            name_reader = csv.reader(name)
            name_stats = list(tuple(row) for row in name_reader)
            return name_stats 

    
    def talent_data(type):
        with open('./ab_data/talents/' + type + '_talents.csv', "r") as talent:
            talent_reader = DictReader(talent)
            talent_stats = list(talent_reader)
            tdata = {talent["name"]: talent for talent in talent_stats}
            return tdata

    #
    def spell_data():
        with open('./ab_data/spells.csv', "r") as spells:
            spell_reader = DictReader(spells)
            spell_stats = list(spell_reader)
            sdata = {spell["name"]: {k: int(v) if v.isdigit() else v for k, v in spell.items()} for spell in spell_stats}
            return sdata
    
    #
    def map_data():
        with open('./ab_data/map.csv', "r") as map:
            map_reader = DictReader(map)
            map_stats = list(map_reader)
            adata = {map["name"]: map for map in map_stats}
            return adata
    
    #
    def location_data(name):
        with open('./ab_data/' + name + '/location.csv', "r") as loc:
            loc_reader = DictReader(loc)
            loc_stats = list(loc_reader)
            ldata = {loc["desc"]: loc for loc in loc_stats}
            return ldata
     
    # 
    def arrow_data(name):
        with open('./ab_data/' + name + '/arrow.csv', "r") as arr:
            arr_reader = DictReader(arr)
            arr_stats = list(arr_reader)
            rdata = {arr["name"]: arr for arr in arr_stats}
            return rdata
    
    #
    def loc_tree_data(name):
        with open('./ab_data/' + name + '/loc_tree.json', "r") as tree:
            loc_tree = json.load(tree)
            return loc_tree

class Stats():
    def __init__(self):
        self.level_cost = {1: "2", 2: "15", 3: "30", 4: "50", 5: "75"} #current level and exp needed for next
        self.abilities = {"bard": {}, "cleric": {}, "barbarian": {}, "ranger": {}, "thief": {}, "paladin": {}, "warrior": {}, "wizard": {}}
        self.level_health = {"bard": 2, "cleric": 4, "barbarian": 5, "ranger": 4, "thief": 3, "paladin": 4, "warrior": 5, "wizard": 2}

        self.spells = get_data('spells')
        
    #move to hero methods 
    def add_stat(self, hero, stat_bonus):
        stat_name, stat_val_str = stat_bonus.split()
        stat_val = int(stat_val_str)
        if hasattr(hero, stat_name):
            old_val = getattr(hero, stat_name)
            new_val = old_val + stat_val
            setattr(hero, stat_name, new_val)

    def add_talent(self, hero: object, name: str, type: str):
        talents = Data.talent_data(hero.type)

        if type == "spell":
            #add spell id on spell talents and query the spell, needs function
            #Talent name: 'Fire Gush' effect: 'fire_gush'
            #effect should be name, name should be name_text
            spell_name = talents[name]["effect"]
            talent_spell = row_to_dict(self.spells, spell_name)
            hero.talents.append(name)
            hero.spells.append(talent_spell)
            #hero.spells.append(self.spells[(talents[name]["effect"])])
        elif type == "stat":
            hero.talents.append(name)
            stat_bonus = talents[name]["effect"]
            self.add_stat(hero, stat_bonus)
        elif type == "special":
            hero.talents.append(name)
            #check hero talent list start of combat and pull effects from data
        elif type == "domain":
            hero.talents.append(name) 
            hero.type = talents[name]["effect"]
            bonus = talents[name]["bonus"]
            self.add_stat(hero, bonus)
        elif type == "m_stat":
            hero.talents.append(name)
            #speed 1 damage 1
        elif type == "song":
            hero.talents.append(name)
        
    def levelup(self, hero):
        hero.level += 1
        hero.next_level = int(self.level_cost[hero.level])
        
        if hero.type not in self.level_health.keys():
            hero_type = 'cleric'
        else:
            hero_type = hero.type
        hero.max_health += self.level_health[hero_type]
        hero.health += self.level_health[hero_type] #hero.level     