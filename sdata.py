import pygame as pg
from csv import DictReader

#create data startup only
class Data:
    def __init__(self):
        pass
    def monster_data():
        with open('auto_battle/ab_data/monsters.csv', "r") as mobs:
            mob_reader = DictReader(mobs)
            monster_stats = list(mob_reader)
            mdata = {}
            for x in range(len(monster_stats)):
                mdata[monster_stats[x]["name"]] = monster_stats[x]
            return mdata       
        

    def hero_data():
        with open('auto_battle/ab_data/heroes.csv', "r") as hero:
            hero_reader = DictReader(hero)
            hero_stats = list(hero_reader)
            hdata = {}
            for y in range(len(hero_stats)):
                hdata[hero_stats[y]["class"]] = hero_stats[y]
            return hdata
#Data.monster_data()




