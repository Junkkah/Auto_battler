import pygame as pg
import sys
from config_ab import Config
from sounds_ab import play_sound_effect
from sprites_ab import Button, EquipmentSlot
from hero_ab import Hero
from battle_ab import BattleManager
from data_ab import get_slots_data

class Inventory(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path' 

    def cleanup(self):
        self.inventory_buttons = []
        self.hero_spots = []
        self.eq_slots = []
        self.backpack_slots = []
        self.figure_coords = []
        self.inventory_items = []
        self.inventory_sprites.empty()
        self.inventory_button_sprites.empty()
        self.inventory_icon_sprites.empty()
        self.dragging_hero = False
        self.dragging_item = False
        self.dragged_object = None
        self.original_spot = None
        self.spot_found = False
        self.startup_done = False
    
    def reorder_party(self):
        Config.party_heroes.sort(key=lambda hero: hero.inventory_spot)
        for i, hero in enumerate(Config.party_heroes, start=1):
            hero.inventory_spot_number = i
    
    def create_figure_slots(self):
        slots_data = get_slots_data()
        for slot_type, slot_ratios in slots_data.items():
            for i, (x_ratio, y_ratio) in enumerate(slot_ratios, start=1):
                pos_x = self.screen_width * x_ratio
                pos_y = self.screen_height * y_ratio
                spot_number = i
                slot = EquipmentSlot(pos_x, pos_y, self.slot_side_length, self.slot_side_length, slot_type, spot_number)
                setattr(self, f'{slot_type}_slot{i}', slot)
                self.eq_slots.append(slot)
    
    #create slot_loader in Config to preload slots into memory
    def create_backpack_slots(self, slot_list):
        first_slot_x_ratio = 0.05
        first_slot_y_ratio = 0.11
        backpack_row = 5
        backpack_column = 4
        gutter = 5
        backpack_slot_number = 1
        for row_i in range(backpack_row):
            for column_j in range(backpack_column):
                spot_number = 0
                slot_type = 'backpack'
                width_gap =  self.slot_side_length + gutter
                height_gap =  self.slot_side_length + gutter
                pos_x = self.screen_width * first_slot_x_ratio + (column_j) * width_gap
                pos_y = self.screen_height * first_slot_y_ratio + (row_i) * height_gap
                slot = EquipmentSlot(pos_x, pos_y, self.slot_side_length, self.slot_side_length, slot_type, spot_number)
                setattr(self, f'{slot_type}_slot{backpack_slot_number}', slot)
                slot_list.append(slot)
                backpack_slot_number += 1

    def worn_items_in_slots(self):
        for clean_slot in self.eq_slots:
            clean_slot.equipped_item = None
        for i, eq_hero in enumerate(Config.party_heroes, start = 1):
            worn_items = eq_hero.worn_items
            for item_slot, item in worn_items.items():
                if item is not None:
                    slot_name = f'{item_slot}_slot{i}'
                    equipment_slot = getattr(self, slot_name)
                    slot_x = equipment_slot.rect.x
                    slot_y = equipment_slot.rect.y
                    item.rect.x = slot_x
                    item.rect.y = slot_y
                    item.inventory_spot = equipment_slot
                    equipment_slot.equipped_item = item

                    if not self.startup_done:
                        self.inventory_items.append(item)
                        self.inventory_icon_sprites.add(item)

    def backpack_to_slots(self, item_list, sprite_group):
        for i, backpack_item in enumerate(Config.party_backpack, start = 1):
            slot_name = f'backpack_slot{i}'
            equipment_slot = getattr(self, slot_name)
            slot_x = equipment_slot.rect.x
            slot_y = equipment_slot.rect.y
            backpack_item.rect.x = slot_x
            backpack_item.rect.y = slot_y
            backpack_item.inventory_spot = equipment_slot
            equipment_slot.equipped_item = backpack_item
            item_list.append(backpack_item)
            sprite_group.add(backpack_item)

    def create_hero_spots(self):
        # Create rect objects for hero spots
        self.hero_spots = []
        for i, hero in enumerate(Config.party_heroes, start = 1):
            var_name = f'hero_spot{i}'
            hero_rect = hero.rect
            value = pg.Rect(hero_rect.x - 5, hero_rect.y - 5, self.max_hero_width + 10, hero_rect.height + 10)
            setattr(self, var_name, value)
            inv_spot = getattr(self, var_name)
            self.hero_spots.append(inv_spot)
            hero.inventory_spot = inv_spot
            hero.inventory_spot_number = i
    
    def create_figures(self):
        figure_count = 3
        figure_size_scalar = 3
        figure = pg.image.load('./ab_images/figure.png').convert_alpha()
        scalar_width = figure.get_width() // figure_size_scalar
        scalar_height = figure.get_height() // figure_size_scalar
        self.figure_image = pg.transform.smoothscale(figure, (scalar_width, scalar_height))
        self.figure_coords = [(self.screen_width * (0.27 + 0.2 * i), self.screen_height * 0.10) for i in range(figure_count)]
    
    def move_bumped_item(self):
        for origin_hero in Config.party_heroes:
            origin_spot_number = self.original_spot.spot_number
            if origin_hero.inventory_spot_number == origin_spot_number:
                origin_hero.drop_item(self.bumped_item.slot_type)
                origin_hero.equip_item(self.bumped_item)
                break
        self.original_spot.equipped_item = None
        self.original_spot.equipped_item = self.bumped_item
        self.bumped_item = None
    
    def clear_origin_slot(self):
        self.original_spot.equipped_item = None
        origin_spot_number = self.original_spot.spot_number
        if origin_spot_number == 0:
            pass
        else:
            for origin_hero in Config.party_heroes:
                if origin_hero.inventory_spot_number == origin_spot_number:
                    slot_to_drop = self.original_spot.slot_type
                    origin_hero.drop_item(slot_to_drop)
                    break

    def equip_drop_item(self):
        for drop_hero in Config.party_heroes:
            if drop_hero.inventory_spot_number == self.drop_spot_number:
                item_to_equip = self.dragged_object
                drop_hero.equip_item(item_to_equip)
                self.drop_spot_number = None
                break

    def startup(self):
        self.inventory_buttons = []
        self.eq_slots = []
        self.backpack_slots = []
        self.figure_coords = []
        self.inventory_items = []
        self.inventory_sprites = pg.sprite.Group()
        self.inventory_button_sprites = pg.sprite.Group()
        self.inventory_icon_sprites = pg.sprite.Group()
        self.dragging_hero = False
        self.dragging_item = False
        self.dragged_object = None
        self.original_spot = None
        self.spot_found = False
        self.startup_done = False
        # With hero_width_scalar value 7.5 all heroes fit to hero_spots
        self.hero_width_scalar = 7.5
        self.max_hero_width = self.screen_height // self.hero_width_scalar
        self.continue_button = Button(self.inventory_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)
        
        # Position heroes 
        battle_instance = BattleManager()
        battle_instance.position_heroes(Config.party_heroes)
        for inv_hero in Config.party_heroes:
            self.inventory_sprites.add(inv_hero)
        
        self.create_hero_spots()
        self.create_figures()
        self.create_figure_slots()
        self.create_backpack_slots(self.backpack_slots)

        self.worn_items_in_slots()
        self.backpack_to_slots(self.inventory_items, self.inventory_icon_sprites)
        self.startup_done = True
        
    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
            if event.key == pg.K_i:
                self.next = 'path'
                self.done = True
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'path'
                self.done = True
        
            # Start dragging hero or item with mouse
            if event.button == self.primary_mouse_button:
                for move_hero in Config.party_heroes: 
                    if move_hero.rect.collidepoint(mouse_pos):
                        self.dragging_hero = True
                        self.dragged_object = move_hero
                        self.original_spot = self.dragged_object.inventory_spot
                        self.offset_x = mouse_pos[0] - self.dragged_object.rect.x
                        self.offset_y = mouse_pos[1] - self.dragged_object.rect.y
                for move_item in self.inventory_items:
                    if move_item.rect.collidepoint(mouse_pos):
                        self.dragging_item = True
                        self.dragged_object = move_item
                        self.original_spot = self.dragged_object.inventory_spot
                        self.offset_x = mouse_pos[0] - self.dragged_object.rect.x
                        self.offset_y = mouse_pos[1] - self.dragged_object.rect.y
   
        # Drop hero or item that is being dragged with mouse
        # Object returns to original location if not dropped in valid location
        # If drop location already has object, that object is bumped to the original location
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == self.primary_mouse_button:  
                if self.dragging_hero:
                    for hero_spot in self.hero_spots:
                        if hero_spot.colliderect(self.dragged_object.rect):
                            for bumped_hero in Config.party_heroes:
                                if bumped_hero.inventory_spot == hero_spot:
                                    bumped_hero.rect.x = self.original_spot.x
                                    bumped_hero.rect.y = self.original_spot.y
                                    bumped_hero.inventory_spot = self.original_spot
                            self.dragged_object.rect.x = hero_spot.x
                            self.dragged_object.rect.y = hero_spot.y
                            self.spot_found = True
                            self.dragged_object.inventory_spot = hero_spot
                            self.reorder_party ()
                            self.worn_items_in_slots()
                    if not self.spot_found:   
                        self.dragged_object.rect.x = self.original_spot.x
                        self.dragged_object.rect.y = self.original_spot.y
                    self.dragging_hero = False
                    self.spot_found = False
                    self.original_spot = None
                    self.dragged_object = None

                if self.dragging_item:
                    # Dropping item to equipped slot
                    for drop_slot in self.eq_slots:
                        if drop_slot.rect.colliderect(self.dragged_object.rect) and drop_slot.slot_type == self.dragged_object.slot_type:
                            if drop_slot.equipped_item:
                                self.bumped_item = drop_slot.equipped_item
                                self.bumped_item.rect.x = self.original_spot.rect.x
                                self.bumped_item.rect.y = self.original_spot.rect.y
                                self.bumped_item.inventory_spot = self.original_spot
                                self.move_bumped_item()

                            if drop_slot.equipped_item is None: 
                                self.clear_origin_slot()
                            
                            self.drop_spot_number = drop_slot.spot_number
                            if self.drop_spot_number == 0:
                                self.drop_spot_number = None
                            else:
                                self.equip_drop_item()

                            drop_slot.equipped_item = self.dragged_object
                            self.dragged_object.rect.x = drop_slot.rect.x
                            self.dragged_object.rect.y = drop_slot.rect.y
                            self.dragged_object.inventory_spot = drop_slot
                            self.spot_found = True
                            play_sound_effect('drop')

                    for backpack_drop_slot in self.backpack_slots:
                        # Dropping item to backpack slot
                        if backpack_drop_slot.rect.collidepoint(mouse_pos):
                            if backpack_drop_slot.equipped_item:
                                self.bumped_item = backpack_drop_slot.equipped_item
                                self.bumped_item.rect.x = self.original_spot.rect.x
                                self.bumped_item.rect.y = self.original_spot.rect.y
                                self.bumped_item.inventory_spot = self.original_spot
                                self.move_bumped_item()
                            if backpack_drop_slot.equipped_item is None:
                                self.clear_origin_slot()
                            
                            self.drop_spot_number = backpack_drop_slot.spot_number
                            if self.drop_spot_number == 0:
                                self.drop_spot_number = None
                            else:
                                self.equip_drop_item()

                            backpack_drop_slot.equipped_item = self.dragged_object
                            self.dragged_object.rect.x = backpack_drop_slot.rect.x
                            self.dragged_object.rect.y = backpack_drop_slot.rect.y
                            self.dragged_object.inventory_spot = backpack_drop_slot
                            Config.party_backpack.append(self.dragged_object)
                            self.spot_found = True
                            play_sound_effect('drop')

                    if not self.spot_found:   
                        self.dragged_object.rect.x = self.original_spot.rect.x
                        self.dragged_object.rect.y = self.original_spot.rect.y
                        play_sound_effect('drop')
                    self.dragging_item = False
                    self.spot_found = False
                    self.dragged_object = None
                    self.original_spot = None

    def update(self, screen, dt):
        if self.dragging_hero or self.dragging_item:
            mouse_x, mouse_y = pg.mouse.get_pos()
            self.dragged_object.rect.x = mouse_x - self.offset_x
            self.dragged_object.rect.y = mouse_y - self.offset_y

        self.draw(screen)

    def draw(self, screen):
        self.screen.fill(self.grey)
        for draw_coords in self.figure_coords:
            self.screen.blit(self.figure_image, draw_coords)
        
        self.inventory_button_sprites.draw(self.screen)
        
        for worn_slot in self.eq_slots:
            worn_slot.draw_border()
        
        for backpack_slot in self.backpack_slots:
            backpack_slot.draw_border()
        
        for spot in self.hero_spots:
            pg.draw.rect(self.screen, self.black, spot, 3)
        
        self.inventory_icon_sprites.draw(self.screen)    
        self.inventory_sprites.draw(self.screen)
        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        #render log
        #if mousemotion and self.dragging:
        #highlight correct drop point if collidepoint