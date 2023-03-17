import pygame as pg

class States(object):
    party_heroes = []
    room_monsters = []
    current_location = None
    acting = None
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None
        
        self.width = 1920
        self.height = 1080
        self.screen = pg.display.set_mode((self.width, self.height))
        self.hero_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.weapon_sprites = pg.sprite.Group()
        self.map_sprites = pg.sprite.Group()