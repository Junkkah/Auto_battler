import pygame as pg
import sys
from sstates import States

#choose location at map screen
#load path for that location
#goto path screen with that info

class Map(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'combat' #prev map
    def cleanup(self):
        pass #adventure path
    def startup(self):
        pass #draw adventure path
    def get_event(self, event): #mouseover animation info for nodes
        if event.type == pg.KEYDOWN:
            print('Game State keydown')
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.done = True
    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        screen.fill((0,0,255))