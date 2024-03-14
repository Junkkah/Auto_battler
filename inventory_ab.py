import pygame as pg
import sys
from config_ab import Config
from sounds_ab import sound_effect
from sprites_ab import Button, EquipmentSlot
from hero_ab import Hero
from battle_ab import BattleManager

class Inventory(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path' 

    def cleanup(self):
        Config.party_heroes.sort(key=lambda hero: hero.inventory_spot)
        self.inventory_buttons = []
        self.hero_spots = []
        self.eq_slots = []
        self.figure_coords = []
        self.inventory_sprites.empty()
        self.inventory_button_sprites.empty()
        self.inventory_icon_sprites.empty()
        self.dragging = False
        self.dragged_hero = None
        self.original_spot = None
        self.spot_found = False

    def icons_to_slots(self):
        for i, eq_hero in enumerate(Config.party_heroes, start = 1):
            hand1_item = eq_hero.worn_items.get('hand1')
            
            if hand1_item is not None:
                slot_name = f"hand1_slot{i}"
                slot_x = getattr(self, slot_name).rect.x
                slot_y = getattr(self, slot_name).rect.y
                hand1_item.rect.x = slot_x
                hand1_item.rect.y = slot_y
                self.inventory_icon_sprites.add(hand1_item)

    def startup(self):
        self.inventory_buttons = []
        self.eq_slots = []
        self.figure_coords = []
        self.inventory_sprites = pg.sprite.Group()
        self.inventory_button_sprites = pg.sprite.Group()
        self.inventory_icon_sprites = pg.sprite.Group()
        self.dragging = False
        self.dragged_hero = None
        self.original_spot = None
        self.spot_found = False
        # Hardcoded largest hero image width for creating uniform size hero spots
        self.hero_width_scalar = 7.5
        self.max_hero_width = self.screen_height // self.hero_width_scalar #144 with witdth 1080

        self.continue_button = Button(self.inventory_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)

        # Position heroes 
        battle_instance = BattleManager()
        battle_instance.position_heroes(Config.party_heroes)
        for inv_hero in Config.party_heroes:
            self.inventory_sprites.add(inv_hero)
        
        # Create rect objects for hero spots
        self.hero_spots = []
        for i in range(len(Config.party_heroes)):
            var_name = f"hero_spot{i + 1}"
            hero_rect = Config.party_heroes[i].rect
            value = pg.Rect(hero_rect.x - 5, hero_rect.y - 5, self.max_hero_width + 10, hero_rect.height + 10)
            setattr(self, var_name, value)
            inv_spot = getattr(self, var_name)
            self.hero_spots.append(inv_spot)
            Config.party_heroes[i].inventory_spot = inv_spot

        self.figure1_coords = (self.screen_width * 0.27, self.screen_height * 0.10)
        self.figure2_coords = (self.screen_width * 0.47, self.screen_height * 0.10)
        self.figure3_coords = (self.screen_width * 0.67, self.screen_height * 0.10)
        for figure_coords in [self.figure1_coords, self.figure2_coords, self.figure3_coords]:
            self.figure_coords.append(figure_coords)
        figure = pg.image.load('./ab_images/figure.png').convert_alpha()
        HEIGHT = figure.get_height()
        WIDTH = figure.get_width()
        figure_size_scalar = 3
        SCALAR_W = WIDTH / figure_size_scalar
        SCALAR_H = HEIGHT / figure_size_scalar
        self.figure_image = pg.transform.smoothscale(figure, (SCALAR_W, SCALAR_H))

        #lists for head, body, hands
        #when dragging 'head' item, check collision with head_slot_list items only
        slot_side_length = self.screen_width // self.eq_slot_size_scalar

        # Create equipment slots for each equippable item on character figures
        head_slot_ratios = [(0.31, 0.11), (0.51, 0.11), (0.71, 0.11)]
        for i, (x_ratio, y_ratio) in enumerate(head_slot_ratios, start=1):
            pos_x = self.screen_width * x_ratio
            pos_y = self.screen_height * y_ratio
            slot = EquipmentSlot(pos_x, pos_y, slot_side_length, slot_side_length)
            setattr(self, f'head_slot{i}', slot)
            self.eq_slots.append(slot)

        body_slot_ratios = [(0.31, 0.21), (0.51, 0.21), (0.71, 0.21)]
        for i, (x_ratio, y_ratio) in enumerate(body_slot_ratios, start=1):
            pos_x = self.screen_width * x_ratio
            pos_y = self.screen_height * y_ratio
            slot = EquipmentSlot(pos_x, pos_y, slot_side_length, slot_side_length)
            setattr(self, f'body_slot{i}', slot)
            self.eq_slots.append(slot)

        hand1_slot_ratios = [(0.26, 0.27), (0.46, 0.27), (0.66, 0.27)]
        for i, (x_ratio, y_ratio) in enumerate(hand1_slot_ratios, start=1):
            pos_x = self.screen_width * x_ratio
            pos_y = self.screen_height * y_ratio
            slot = EquipmentSlot(pos_x, pos_y, slot_side_length, slot_side_length)
            setattr(self, f'hand1_slot{i}', slot)
            self.eq_slots.append(slot)

        hand2_slot_ratios = [(0.37, 0.27), (0.57, 0.27), (0.77, 0.27)]
        for i, (x_ratio, y_ratio) in enumerate(hand2_slot_ratios, start=1):
            pos_x = self.screen_width * x_ratio
            pos_y = self.screen_height * y_ratio
            slot = EquipmentSlot(pos_x, pos_y, slot_side_length, slot_side_length)
            setattr(self, f'hand2_slot{i}', slot)
            self.eq_slots.append(slot)

        consumable_slot_ratios = [(0.31, 0.45), (0.51, 0.45), (0.71, 0.45)]
        for i, (x_ratio, y_ratio) in enumerate(consumable_slot_ratios, start=1):
            pos_x = self.screen_width * x_ratio
            pos_y = self.screen_height * y_ratio
            slot = EquipmentSlot(pos_x, pos_y, slot_side_length, slot_side_length)
            setattr(self, f'consumable_slot{i}', slot)
            self.eq_slots.append(slot)

        backpack_slot_spot = (self.screen_width * 0.85, self.screen_height * 0.10)
        self.icons_to_slots()
        #self.worn_items = {'head': None, 'body': None, 'hand1': None, 'hand2': None, 'consumable': None}

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(mouse_pos):
                sound_effect('click')
                self.next = 'path'
                self.done = True
        
            if event.button == self.primary_mouse_button:
                for i in range(len(Config.party_heroes)): 
                    if Config.party_heroes[i].rect.collidepoint(mouse_pos) and not self.dragging:
                        self.dragging = True
                        self.dragged_hero = Config.party_heroes[i]
                        self.original_spot = self.dragged_hero.inventory_spot
                        self.offset_x = mouse_pos[0] - self.dragged_hero.rect.x
                        self.offset_y = mouse_pos[1] - self.dragged_hero.rect.y
                        

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == self.primary_mouse_button:  
                if self.dragging:
                    for hero_spot in self.hero_spots:
                        if hero_spot.colliderect(self.dragged_hero.rect):
                            for bumped_hero in Config.party_heroes:
                                if bumped_hero.inventory_spot == hero_spot:
                                    bumped_hero.rect.x = self.original_spot.x
                                    bumped_hero.rect.y = self.original_spot.y
                                    bumped_hero.inventory_spot = self.original_spot
                            self.dragged_hero.rect.x = hero_spot.x
                            self.dragged_hero.rect.y = hero_spot.y
                            self.spot_found = True
                            self.dragged_hero.inventory_spot = hero_spot

                    if not self.spot_found:   
                        self.dragged_hero.rect.x = self.original_spot.x
                        self.dragged_hero.rect.y = self.original_spot.y
                    self.dragging = False
                    self.spot_found = False
                    

    def update(self, screen, dt):
        if self.dragging:
            mouse_x, mouse_y = pg.mouse.get_pos()
            self.dragged_hero.rect.x = mouse_x - self.offset_x
            self.dragged_hero.rect.y = mouse_y - self.offset_y
        #place equipped items to correct figures after moving heroes
        self.draw(screen)

    def draw(self, screen):
        self.screen.fill(self.grey)
        for draw_coords in self.figure_coords:
            self.screen.blit(self.figure_image, draw_coords)
        self.inventory_sprites.draw(self.screen)
        self.inventory_button_sprites.draw(self.screen)
        self.inventory_icon_sprites.draw(self.screen)
        
        for slot in self.eq_slots:
            slot.draw_border()

        for spot in self.hero_spots:
            pg.draw.rect(self.screen, self.black, spot, 3)

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        if self.dragging:
            pass
        #highlight correct drop point if collide