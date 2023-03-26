import pygame as pg

class States(object):
    party_heroes = []
    room_monsters = []
    current_location = None
    acting = None
    width = 1920
    height = 1080
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None
        self.screen = pg.display.set_mode((self.width, self.height))
        self.hero_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.weapon_sprites = pg.sprite.Group()
        self.map_sprites = pg.sprite.Group()
        
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.blue = (0,0,255)
        self.ground = pg.image.load('./ab_images/game_bg.png')
        self.info_font = pg.font.SysFont("Arial", 20)
        self.max_party_size = 3
