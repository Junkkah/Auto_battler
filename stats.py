import pygame as pg
from csv import DictReader

class Data:
    def __init__(self):
        pass
    def monster_data():
        with open('./ab_data/monsters.csv', "r") as mobs:
            mob_reader = DictReader(mobs)
            monster_stats = list(mob_reader)
            
            # mdata = {}
            # for x in range(len(monster_stats)):
            #    mdata[monster_stats[x]["name"]] = monster_stats[x]
            
            # S: Tässä voi käyttää dictionary comprehension.
            # +Tiiviimpi
            # +Python-tyylinen
            # +Nopeampi (Implementoitu C:llä); tosin koska näissä luetaan levyltä niin pullonkaula siellä
            
            mdata = {monster["name"]: monster for monster in monster_stats}
            return mdata       
        
    def hero_data():
        with open('./ab_data/heroes.csv', "r") as hero:
            hero_reader = DictReader(hero)
            hero_stats = list(hero_reader)
            # S: dictionary comprehension
            hdata = {hero["class"]: hero for hero in hero_stats}
            return hdata

    def talent_data(type):
        with open('./ab_data/' + type + '_talents.csv', "r") as talent:
            talent_reader = DictReader(talent)
            talent_stats = list(talent_reader)
            # S: dictionary comprehension
            tdata = {talent["name"]: talent for talent in talent_stats}
            return tdata

    def spell_data():
        with open('./ab_data/spells.csv', "r") as spell:
            spell_reader = DictReader(spell)
            spell_stats = list(spell_reader)
            # dS: ictionary comprehension
            sdata = {spell["name"]: spell for spell in spell_stats}
            return sdata

class Stats():
    def __init__(self):
        self.level_cost = {1: "2", 2: "15", 3: "30", 4: "50", 5: "75"} #current level and exp needed for next
        self.abilities = {"bard": {}, "cleric": {}, "barbarian": {}, "ranger": {}, "thief": {}, "paladin": {}, "warrior": {}, "wizard": {}}
        #self.abilities = Data.talent_data() 
        self.level_health = {"bard": 2, "cleric": 4, "barbarian": 5, "ranger": 4, "thief": 3, "paladin": 4, "warrior": 5, "wizard": 2}

    def add_talent(self, hero: object, name: str, type: str):
        talents = Data.talent_data(hero.type)
        spells = Data.spell_data()
        if type == "spell":
            hero.spells.append(spells[(talents[name]["effect"])]) #appending dict {'name': 'lightning_zap', 'damage': '2', 'speed': '1', 'type': 'lightning', 'area': '0'}
        elif type == "stat":
            stat_bonus = talents[name]["effect"]
            stat_name, stat_val_str = stat_bonus.split()
            stat_val = int(stat_val_str)
            if hasattr(hero, stat_name):
                old_val = getattr(hero, stat_name)
                new_val = old_val + stat_val
                setattr(hero, stat_name, new_val)
        elif type == "m_stat":
            pass #speed 1 damage 1
        elif type == "song":
            pass
        elif type == "special":
            pass
        #need special, song
        
    def levelup(self, hero):
        hero.level += 1
        hero.next_level = int(self.level_cost[hero.level])
        hero.health += hero.level
        hero.max_health += self.level_health[hero.type]
        
      