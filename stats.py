import pygame as pg
from data import Data
from objects import Hero, Monster

class Stats():
    def __init__(self):
        self.level_cost = {}
        self.abilities = {}
    
    def add_talent(self, hero, talent):
        pass
        #add talent to hero.talents and add relevant stats to hero 
    
    def levelup(self, hero: object):
        pass
        #hero.level += 1
        #hero.next_level = x
        #gain stats
        #gain talent