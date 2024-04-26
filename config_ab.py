import pygame as pg

class Config(object):
    party_heroes = []
    room_monsters = []
    party_backpack = {}
    backpack_slots = []
    equipment_slots = []
    generated_path = []
    gold_count = 50
    current_location = None
    current_adventure = None
    acting_character = None
    width = 1920
    height = 1080
    scout_active = False
    aura_bonus = {'speed': 0, 'damage': 0, 'menace': 0, 'armor': 0, 'magic_power': 0}
    combat_log = []
    
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self.eq_slot_size_scalar = 25
        self.slot_side_length = self.screen_width // self.eq_slot_size_scalar
        self.primary_mouse_button = 1
        self.secondary_mouse_button = 3
        self.npc_size_scalar = 8
        self.speech_bubble_size_scalar = 7
        self.offset_divisor = 7.1

        self.hero_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.weapon_sprites = pg.sprite.Group()
        self.map_sprites = pg.sprite.Group()
        self.path_sprites = pg.sprite.Group()
        self.menu_button_sprites = pg.sprite.Group()
        self.volume_button_sprites = pg.sprite.Group()

        self.max_party_size = 3
        self.spell_types = {'fire', 'cold', 'lightning', 'nature', 'holy', 'acid'}
        self.ground = pg.image.load('./ab_images/background/game_bg.png').convert()
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.blue = (0, 0, 255)
        self.grey = (127, 127, 127)
        self.green = (0, 255, 0)
        self.yellow = (255, 255, 0)

        self.default_font = 'Arial'
        self.small_font_size = 15
        self.default_font_size = 20
        self.medium_font_size = 30
        self.big_font_size = 50
        self.title_font_size = 75

        self.info_font_size = 20
        self.log_font_size = 20
        self.info_font_name = 'Arial'
        self.item_info_font_name = 'Arial'
        DIALOGUE_FONT_NAME = 'Tahoma'
        LOG_FONT_NAME = 'Courier new'
        self.info_font = pg.font.SysFont(self.info_font_name, self.info_font_size)
        self.log_font = pg.font.SysFont(LOG_FONT_NAME, self.log_font_size)
        self.item_info_font = pg.font.SysFont(self.item_info_font_name, self.small_font_size)
        self.med_info_font = pg.font.SysFont(self.info_font_name, self.medium_font_size)
        self.large_info_font = pg.font.SysFont(self.info_font_name, self.big_font_size)
        self.title_font = pg.font.SysFont(self.info_font_name, self.title_font_size)
        self.dialogue_font = pg.font.SysFont(DIALOGUE_FONT_NAME, self.medium_font_size)

        self.CONT_TEXT = 'CONTINUE'
        self.CONT_FONT = self.default_font
        self.CONT_SIZE = self.big_font_size
        self.CONT_COL = self.black
        cont_x_ration = 0.90
        cont_y_ration = 0.90
        self.COORDS_CONT = (self.screen_width * cont_x_ration, self.screen_height * cont_y_ration)

        self.BACK_FONT = self.default_font
        self.BACK_SIZE = self.medium_font_size
        self.BACK_COL = self.black
        self.COORDS_BACK = (self.screen_width * 0.10, self.screen_height * 0.90)

        self.coords_gold = (10, 10)
        self.gold_font_name = 'Verdana'
        self.gold_font_size = 25
    
    def create_gold_text(self):
        gold_value = Config.gold_count
        gold = f'{gold_value :.0f} Gold coins'
        font = pg.font.SysFont(self.gold_font_name, self.gold_font_size)
        text_surface = font.render(gold, True, self.yellow) 
        return text_surface
