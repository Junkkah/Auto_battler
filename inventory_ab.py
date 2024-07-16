"""
Inventory module for managing and displaying hero items and inventory.

Contains:
    - Inventory: Displays hero equipment, backpack items, and handles 
      item management including dragging, dropping, and displaying
      item info.
"""

import pygame as pg
import itertools
from config_ab import Config
from sounds_ab import play_sound_effect
from sprites_ab import Button, EquipmentSlot, Equipment
from hero_ab import Hero
from battle_ab import BattleManager
from items_ab  import ItemManager
from data_ab import get_json_data

class Inventory(Config):
    """
    Manages and displays hero items and inventory.

    This class handles the display of hero equipment and backpack items, 
    allowing for item management through dragging, dropping, and reordering 
    heroes and their items.
    """

    def __init__(self):
        """Initialize inventory with default settings and set next state to 'path'."""
        super().__init__()
        self.next = 'path' 

    def cleanup(self):
        """Reset class-specific variables and clear associated sprites."""
        self.inventory_buttons = []
        self.hero_spots = []
        self.figure_coords = []
        self.inventory_items = []
        self.inventory_sprites.empty()
        self.inventory_button_sprites.empty()
        self.inventory_icon_sprites.empty()
        self.dragging_hero = False
        self.dragging_item = False
        self.dragged_object = None
        self.original_spot = None
        self.hovered_item = None
        self.spot_found = False
        self.startup_done = False
    
    def reorder_party(self):
        """Sort party heroes by inventory spot and update their spot numbers."""
        Config.party_heroes.sort(key=lambda hero: hero.inventory_spot)
        for i, hero in enumerate(Config.party_heroes, start=1):
            hero.inventory_spot_number = i
    
    # Equipment slots are cleared
    # Item objects in heroes item dictionaries are moved to slots
    def worn_items_to_slots(self):
        """Clear equipment slots and move items from heroes' item dictionaries to their respective slots."""
        for eq_slots in Config.equipment_slots:
            for slot_type in eq_slots:
                eq_slots[slot_type].equipped_item = None
        for i, eq_hero in enumerate(Config.party_heroes):
            worn_items = eq_hero.worn_items
            for item_slot, item in worn_items.items():
                if item is not None:
                    equipment_slot = Config.equipment_slots[i][item_slot]
                    slot_x = equipment_slot.rect.x
                    slot_y = equipment_slot.rect.y
                    item.rect.x = slot_x
                    item.rect.y = slot_y
                    item.inventory_spot = equipment_slot
                    equipment_slot.equipped_item = item

                    if not self.startup_done:
                        self.inventory_items.append(item)
                        self.inventory_icon_sprites.add(item)

    # Backpack slots are cleared
    # Item objects in backpack dictionary are moved to backpack slots
    @staticmethod
    def backpack_to_slots(item_list, sprite_group):
        """Clear backpack slots and move items from the backpack dictionary to the corresponding slots."""
        for clean_slot in Config.backpack_slots:
            clean_slot.equipped_item = None
        for slot_key, backpack_item in Config.party_backpack.items():
            if backpack_item is not None:
                for slot_object in Config.backpack_slots:
                    if slot_object.name == slot_key:
                        equipment_slot = slot_object
                        slot_x = equipment_slot.rect.x
                        slot_y = equipment_slot.rect.y
                        backpack_item.rect.x = slot_x
                        backpack_item.rect.y = slot_y
                        backpack_item.inventory_spot = equipment_slot
                        equipment_slot.equipped_item = backpack_item
                        item_list.append(backpack_item)
                        sprite_group.add(backpack_item)
                        break 

    def create_hero_spots(self):
        """Create and assign Rect objects for hero inventory spots."""
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
        """Load and scale figure images, then set their coordinates."""
        figure_count = 3
        figure_size_scalar = 3
        figure = pg.image.load('./ab_images/figure.png').convert_alpha()
        scalar_width = figure.get_width() // figure_size_scalar
        scalar_height = figure.get_height() // figure_size_scalar
        self.figure_image = pg.transform.smoothscale(figure, (scalar_width, scalar_height))
        self.figure_coords = [(self.screen_width * (0.27 + 0.2 * i), self.screen_height * 0.10) for i in range(figure_count)]
    
    def move_bumped_item(self, bumped_item):
        """Move an item to the original slot of the dragged item."""
        bumped_item.rect.x = self.original_spot.rect.x
        bumped_item.rect.y = self.original_spot.rect.y
        bumped_item.inventory_spot = self.original_spot
        origin_spot_number = self.original_spot.spot_number
        if origin_spot_number == 0:
            Config.party_backpack[self.original_spot.name] = bumped_item
        else:
            for origin_hero in Config.party_heroes:
                if origin_hero.inventory_spot_number == origin_spot_number:
                    origin_hero.drop_item(bumped_item.slot_type)
                    origin_hero.equip_item(bumped_item)
                    break
        self.original_spot.equipped_item = None
        self.original_spot.equipped_item = bumped_item
    
    def clear_origin_slot(self):
        """Clear the original slot of the dragged item."""
        self.original_spot.equipped_item = None
        origin_spot_number = self.original_spot.spot_number
        if origin_spot_number == 0:
            Config.party_backpack[self.original_spot.name] = None
        else:
            for origin_hero in Config.party_heroes:
                if origin_hero.inventory_spot_number == origin_spot_number:
                    slot_to_drop = self.original_spot.slot_type
                    origin_hero.drop_item(slot_to_drop)
                    break

    def equip_dropped_item(self, drop_spot_number):
        """Equip the dragged item for the hero at the specified inventory spot."""
        for drop_hero in Config.party_heroes:
            if drop_hero.inventory_spot_number == drop_spot_number:
                item_to_equip = self.dragged_object
                drop_hero.equip_item(item_to_equip)
                break
    
    def handle_book(self, drop_spot_number):
        """Activate the book item for the hero at the specified inventory spot."""
        for reading_hero in Config.party_heroes:
            if reading_hero.inventory_spot_number == drop_spot_number:
                ItemManager.activate_book(reading_hero, self.dragged_object)
                self.inventory_items.remove(self.dragged_object)
                self.inventory_icon_sprites.remove(self.dragged_object)
                break
    
    @staticmethod
    def display_item_info(screen, screen_height, hovered_item, item_info_font, black, white):
        """Render and display item information on the screen."""
        mouse_pos = pg.mouse.get_pos()
        desc_text_line1 = item_info_font.render(hovered_item.desc, True, black)
        item_effect = hovered_item.item_prefix_effect
        if item_effect[0]:
            item_stat = item_effect[0].capitalize()
            stat_mod = str(item_effect[1])
            hovered_item_effect = item_stat + ' +' + stat_mod
        else:
            hovered_item_effect = ''
        desc_text_line2 = item_info_font.render(hovered_item_effect, True, black)
        
        text_rect_line1 = desc_text_line1.get_rect()
        text_rect_line2 = desc_text_line2.get_rect()

        offset_divisor = 54
        offset_y = screen_height // offset_divisor

        text_rect_line1.bottomright = (mouse_pos[0], mouse_pos[1] - offset_y)
        offset_x = text_rect_line1.width - text_rect_line2.width
        text_rect_line2.bottomright = (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y + text_rect_line1.height)
        
        rect_width = max(text_rect_line1.width, text_rect_line2.width)
        rect_height = text_rect_line1.height + text_rect_line2.height
        
        rect_surface = pg.Surface((rect_width, rect_height))
        rect_surface.fill(white)
        screen.blit(rect_surface, (text_rect_line1.left, text_rect_line1.top))
        screen.blit(desc_text_line1, text_rect_line1.topleft)
        screen.blit(desc_text_line2, text_rect_line2.topleft)

    def startup(self):
        """Initialize resources and set up the inventory state."""
        self.inventory_buttons = []
        self.figure_coords = []
        self.inventory_items = []
        self.inventory_sprites = pg.sprite.Group()
        self.inventory_button_sprites = pg.sprite.Group()
        self.inventory_icon_sprites = pg.sprite.Group()
        self.dragging_hero = False
        self.dragging_item = False
        self.spot_found = False
        self.startup_done = False
        self.dragged_object = None
        self.original_spot = None
        self.hovered_item = None
        # With hero_width_scalar value 7.5 all heroes fit to hero_spots
        self.hero_width_scalar = 7.5
        self.max_hero_width = self.screen_height // self.hero_width_scalar
        self.continue_button = Button(self.inventory_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)
        
        # Position heroes 
        battle_instance = BattleManager()
        battle_instance.position_heroes()
        for inv_hero in Config.party_heroes:
            self.inventory_sprites.add(inv_hero)
        
        self.create_hero_spots()
        self.create_figures()
        self.worn_items_to_slots()
        self.backpack_to_slots(self.inventory_items, self.inventory_icon_sprites)
        self.startup_done = True
 
    def get_event(self, event):
        """Handle user input events for the inventory state."""
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
            if event.key == pg.K_i:
                self.next = 'path'
                self.done = True
        
        elif event.type == pg.MOUSEMOTION:
            for hover_item in self.inventory_items:
                if hover_item.rect.collidepoint(mouse_pos):
                    self.hovered_item = hover_item
                    break
                else:
                    self.hovered_item = None

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'path'
                self.done = True
        
            # Start dragging object
            if event.button == self.primary_mouse_button:
                for obj in itertools.chain(Config.party_heroes, self.inventory_items):
                    if obj.rect.collidepoint(mouse_pos):
                        if isinstance(obj, Hero):
                            self.dragging_hero = True
                        elif isinstance(obj, Equipment):
                            self.dragging_item = True
                        
                        self.dragged_object = obj
                        self.original_spot = self.dragged_object.inventory_spot
                        self.offset_x = mouse_pos[0] - self.dragged_object.rect.x
                        self.offset_y = mouse_pos[1] - self.dragged_object.rect.y
                        break 

        # Drop dragged hero or item object
        # Object returns to original location if drop location is not valid
        # If drop location already has an object, that object is bumped to the original location
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
                            self.worn_items_to_slots()
                    if not self.spot_found:   
                        self.dragged_object.rect.x = self.original_spot.x
                        self.dragged_object.rect.y = self.original_spot.y
                    self.dragging_hero = False
                    self.spot_found = False
                    self.original_spot = None
                    self.dragged_object = None

                if self.dragging_item:
                    for eq_slots in Config.equipment_slots:
                        for slot_type in eq_slots:
                            drop_slot = eq_slots[slot_type]
                            if drop_slot.rect.colliderect(self.dragged_object.rect) and drop_slot.slot_type == self.dragged_object.slot_type:
                                if drop_slot.equipped_item:
                                    bumped_item = drop_slot.equipped_item
                                    self.move_bumped_item(bumped_item)
                                if drop_slot.equipped_item is None: 
                                    self.clear_origin_slot()
                                
                                drop_spot_number = drop_slot.spot_number
                                if self.dragged_object.item_name == 'book':
                                    self.handle_book(drop_spot_number)
                                else:
                                    self.equip_dropped_item(drop_spot_number)
                                    drop_slot.equipped_item = self.dragged_object
                                    self.dragged_object.rect.x = drop_slot.rect.x
                                    self.dragged_object.rect.y = drop_slot.rect.y
                                    self.dragged_object.inventory_spot = drop_slot
                        
                                self.spot_found = True
                                play_sound_effect('drop')

                    for backpack_drop_slot in Config.backpack_slots:
                        if backpack_drop_slot.rect.collidepoint(mouse_pos):
                            if backpack_drop_slot.equipped_item:
                                if self.original_spot.spot_number != 0 and self.dragged_object.slot_type != backpack_drop_slot.equipped_item.slot_type:
                                    break
                                bumped_item = backpack_drop_slot.equipped_item
                                Config.party_backpack[backpack_drop_slot.name] = None
                                self.move_bumped_item(bumped_item)
                            if backpack_drop_slot.equipped_item is None:
                                self.clear_origin_slot()
                            
                            self.drop_spot_number = backpack_drop_slot.spot_number
                            if self.drop_spot_number == 0:
                                self.drop_spot_number = None
                            else:
                                self.equip_dropped_item()

                            backpack_drop_slot.equipped_item = self.dragged_object
                            self.dragged_object.rect.x = backpack_drop_slot.rect.x
                            self.dragged_object.rect.y = backpack_drop_slot.rect.y
                            self.dragged_object.inventory_spot = backpack_drop_slot
                            Config.party_backpack[backpack_drop_slot.name] = self.dragged_object
                            self.spot_found = True
                            play_sound_effect('drop')
                            break

                    if not self.spot_found:   
                        self.dragged_object.rect.x = self.original_spot.rect.x
                        self.dragged_object.rect.y = self.original_spot.rect.y
                        play_sound_effect('error')
                    self.dragging_item = False
                    self.spot_found = False
                    self.dragged_object = None
                    self.original_spot = None

    def update(self, screen, dt):
        """Update the inventory state based on user input and game events."""
        if self.dragging_hero or self.dragging_item:
            mouse_x, mouse_y = pg.mouse.get_pos()
            self.dragged_object.rect.x = mouse_x - self.offset_x
            self.dragged_object.rect.y = mouse_y - self.offset_y

        self.draw(screen)

    def draw(self, screen):
        """Draw the inventory state to the screen."""
        mouse_pos = pg.mouse.get_pos()
        self.screen.fill(self.grey)
        for draw_coords in self.figure_coords:
            self.screen.blit(self.figure_image, draw_coords)
        
        self.inventory_button_sprites.draw(self.screen)
        
        for worn_slot in Config.equipment_slots:
            for slot_type in worn_slot:
                if self.dragging_item and self.dragged_object.slot_type == slot_type:
                    worn_slot[slot_type].border_color = worn_slot[slot_type].valid_spot_color
                else:
                    worn_slot[slot_type].border_color = worn_slot[slot_type].default_color
                worn_slot[slot_type].draw_border()
        
        for backpack_slot in Config.backpack_slots:
            if self.dragging_item and not backpack_slot.equipped_item:
                backpack_slot.border_color = backpack_slot.valid_spot_color
            else:
                backpack_slot.border_color = backpack_slot.default_color
            backpack_slot.draw_border()
        
        for spot in self.hero_spots:
            pg.draw.rect(self.screen, self.black, spot, 3)
        
        self.inventory_sprites.draw(self.screen)
        self.inventory_icon_sprites.draw(self.screen) 
        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        #weapon base damage in info. Armor bases?
        if self.hovered_item and not self.dragging_item:
            self.display_item_info(self.screen, self.screen_height, self.hovered_item, self.item_info_font, self.black, self.white)