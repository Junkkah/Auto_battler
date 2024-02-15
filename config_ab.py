import pygame as pg

#class Config
class Config(object):
    party_heroes = []
    room_monsters = []
    gold_count = 50
    current_location = None
    current_adventure = None
    acting_character = None
    width = 1920
    height = 1080
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))

        self.hero_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.weapon_sprites = pg.sprite.Group()
        self.map_sprites = pg.sprite.Group()
        self.path_sprites = pg.sprite.Group()
        self.menu_button_sprites = pg.sprite.Group()

        self.max_party_size = 3
        
        self.ground = pg.image.load('./ab_images/game_bg.png').convert()
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.blue = (0, 0, 255)
        self.grey = (127, 127, 127)
        self.green = (0, 255, 0)
        self.yellow = (255, 255, 0)

        self.default_font = "Arial"
        self.default_font_size = 20
        self.medium_font_size = 30
        self.big_font_size = 50
        self.title_font_size = 75

        self.info_font_size = 20
        INFO_FONT_NAME = "Arial"
        self.info_font = pg.font.SysFont(INFO_FONT_NAME, self.info_font_size)
        self.med_info_font = pg.font.SysFont(INFO_FONT_NAME, self.medium_font_size)
        self.large_info_font = pg.font.SysFont(INFO_FONT_NAME, self.big_font_size)
        self.title_font = pg.font.SysFont(INFO_FONT_NAME, self.title_font_size)


        self.coords_gold = (10, 10)
        self.gold_font_name = 'Verdana'
        self.gold_font_size = 25
    
    def create_gold_text(self):
        gold_value = Config.gold_count
        gold = f'{gold_value :.0f} Gold coins'
        font = pg.font.SysFont(self.gold_font_name, self.gold_font_size)
        text_surface = font.render(gold, True, self.yellow) 
        return text_surface
