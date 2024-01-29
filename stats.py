import pygame as pg
import csv
from csv import DictReader
from states import States
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

    def talent_data(type):
        with open('./ab_data/talents/' + type + '_talents.csv', "r") as talent:
            talent_reader = DictReader(talent)
            talent_stats = list(talent_reader)
            tdata = {talent["name"]: talent for talent in talent_stats}
            return tdata

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