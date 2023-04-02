import pygame as pg

class States(object):
    party_heroes = []
    room_monsters = []
    current_location = None
    current_adventure = None
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
        self.blue = (0, 0, 255)
        self.grey = (127, 127, 127)
        self.ground = pg.image.load('./ab_images/game_bg.png').convert()
        self.info_font_size = 20
        INFO_FONT_NAME = "Arial"
        self.info_font = pg.font.SysFont(INFO_FONT_NAME, self.info_font_size)
        self.big_font_size = 50
        self.title_font_size = 75
        self.max_party_size = 3
