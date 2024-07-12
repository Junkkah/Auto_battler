"""
Path module for managing adventure maps and player interactions.

Contains:
    - Path: Creates, displays, and handles interactions with adventure map objects.
"""

import pygame as pg
from config_ab import Config
from sprites_ab import Location, Button
from hero_ab import Hero
from data_ab import get_data, get_monster_encounters, get_json_data
from sounds_ab import play_music_effect, play_sound_effect
import pandas as pd
import math
import random


class Path(Config):
    """
    Manages the adventure map and player interactions.

    This class creates adventure map objects, draws them on the screen, 
    and handles player interactions, including navigation to the inventory 
    and information screens.
    """

    def __init__(self):
        """Initialize path with default settings and set next state to 'battle'."""
        super().__init__()
        self.next = 'battle'
        self.rooms_done = 0
        self.line_thickness = 5
        self.max_pulse_radius = 50
        self.pulsation_speed = 0.005
        self.hovered_item = None

    def cleanup(self):
        """Reset class-specific variables and clear associated sprites."""
        self.path_sprites.empty()
        self.loc_objects = []
        self.map_key_images = []
        self.map_key_texts = []
        self.hovered_item = None

    def create_encounter(self, tier) -> list:
        """Create and return a random encounter based on the given tier."""
        encounters_df = get_monster_encounters(Config.current_adventure, tier)
        probs = encounters_df['Probability'].tolist()
        mob_lists = encounters_df.apply(lambda row: [value for value in row[4:].tolist() if value is not None], axis=1).tolist()
        encounter = random.choices(mob_lists, weights=probs, k=1)[0]
        return encounter
    
    def set_children(self, df):
        """Assign child nodes to location objects based on the given DataFrame."""
        for loc_object in self.loc_objects:
            obj_name = loc_object.name
            obj_child1_name = df.loc[df['name'] == obj_name, 'child1'].values[0]
            obj_child2_name = df.loc[df['name'] == obj_name, 'child2'].values[0]

            if pd.notna(obj_child1_name):
                loc_object.child1 = next((child_obj for child_obj in self.loc_objects if child_obj.name == obj_child1_name), None)
            if pd.notna(obj_child2_name):
                loc_object.child2 = next((child_obj for child_obj in self.loc_objects if child_obj.name == obj_child2_name), None)

    def create_map_key(self, adventure):
        """Create and position map key images and texts for the adventure."""
        node_json = get_json_data('node_types')
        node_type_data = node_json[adventure]
        shop = node_type_data['shop']
        tough = node_type_data['tough']
        fight_options = node_type_data['fight']
        if isinstance(fight_options, list):
            fight1 = fight_options[0]
            fight2 = fight_options[1]
        else:
            fight1, fight2 = fight_options

        map_key_image_data = {
            'fight1': (f'./ab_images/location/{fight1}.png', (self.screen_width * 0.20, self.screen_height * 0.92)),
            'fight2': (f'./ab_images/location/{fight2}.png', (self.screen_width * 0.24, self.screen_height * 0.93)),
            'tough': (f'./ab_images/location/{tough}.png', (self.screen_width * 0.37, self.screen_height * 0.92)),
            'shop': (f'./ab_images/location/{shop}.png', (self.screen_width * 0.49, self.screen_height * 0.93)),
            'boss': ('./ab_images/location/cave.png', (self.screen_width * 0.62, self.screen_height * 0.93))
        }

        size_scalar = 15
        self.map_key_images = []
        for key, (path, coords) in map_key_image_data.items():
            image = self.load_and_scale_image(path, size_scalar)
            rect = image.get_rect(topleft=coords)
            self.map_key_images.append({'image': image, 'rect': rect})
        
        map_key_text_data = {
            'fight': ('Monsters:', (self.screen_width * 0.15, self.screen_height * 0.94)),
            'tough': ('Tough Monster:', (self.screen_width * 0.29, self.screen_height * 0.94)),
            'shop': ('Merchant:', (self.screen_width * 0.43, self.screen_height * 0.94)),
            'boss': ('Boss Monster:', (self.screen_width * 0.55, self.screen_height * 0.94))
        }

        self.map_key_texts = []
        for key, (desc_text, coords) in map_key_text_data.items():
            text, rect = self.create_text_and_rect(self.info_font, desc_text, self.black, coords)
            self.map_key_texts.append({'text': text, 'rect': rect})

    def startup(self):
        """Initialize resources and set up the path state."""
        play_music_effect(Config.current_adventure)

        self.generated_path = Config.generated_path
        for talent_hero in Config.party_heroes:
            talent_hero.activate_talent_group('map')

        self.loc_objects = []
        locations_data = self.generated_path

        for index, row in locations_data.iterrows():
            adventures_df = get_data('adventures')
            current_adventure_df = adventures_df[adventures_df['name'] == Config.current_adventure].reset_index(drop=True)
            width_gap = current_adventure_df.iloc[0]['width_gap']
            new_location = Location(self.path_sprites, row, width_gap)
            self.loc_objects.append(new_location)

        self.create_map_key(Config.current_adventure)
        self.set_children(locations_data)

        self.COORDS_INV = (self.screen_width * 0.91, self.screen_height * 0.95)
        self.COORDS_INFO = (self.screen_width * 0.06, self.screen_height * 0.95)

        INV_TEXT = 'Inventory (i)'
        self.inventory_button = Button(self.path_sprites, INV_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_INV)
        INFO_TEXT = 'Info (f)'
        self.info_button = Button(self.path_sprites, INFO_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_INFO)

    def get_event(self, event):
        """Handle user input events for the path state."""
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
            if event.key ==pg.K_i:
                self.next = 'inventory'
                self.done = True

            if event.key ==pg.K_f:
                self.next = 'info'
                self.done = True

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.inventory_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'inventory'
                self.done = True

            if self.info_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'info'
                self.done = True

            clicked_location = None
            if Config.current_location:
                for child in [Config.current_location.child1, Config.current_location.child2]:
                    if child and child.rect.collidepoint(mouse_pos):
                        clicked_location = child
                        break  

            if not clicked_location:
                for locs_click in self.loc_objects:
                    if locs_click.parent1 is None and locs_click.rect.collidepoint(mouse_pos):
                        clicked_location = locs_click
                        break 

            if clicked_location and clicked_location.type in  ['fight', 'boss']:
                Config.room_monsters = self.create_encounter(clicked_location.tier)
                Config.current_location = clicked_location
                self.next = 'battle'
                self.done = True
            
            if clicked_location and clicked_location.type == 'shop':
                Config.current_location = clicked_location
                self.next = 'shop'
                self.done = True
        
        elif event.type == pg.MOUSEMOTION and Config.scout_active:          
            for path_loc in self.loc_objects:
                if path_loc.rect.collidepoint(mouse_pos):
                    self.hovered_item = path_loc
                    break
                else:
                    self.hovered_item = None
        

    def update(self, screen, dt):
        """Update the path state based on user input and game events."""
        self.draw(screen)

    def draw_circle(self, color, center, radius, thickness):
        """Draw circle to the screen."""
        pg.draw.circle(self.screen, color, center, radius, thickness)
    
    def draw(self, screen):
        """Draw the path state to the screen."""
        self.screen.blit(self.ground, (0,0))
        mouse_pos = pg.mouse.get_pos()
        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        radius = self.max_pulse_radius * abs(math.sin(pg.time.get_ticks() * self.pulsation_speed))

        for desc_text in self.map_key_texts:
            self.screen.blit(desc_text['text'], desc_text['rect'])

        for map_key in self.map_key_images:
            self.screen.blit(map_key['image'], map_key['rect'])
        
        if Config.current_location:
            self.draw_circle(self.white, Config.current_location.child1.pos, int(radius), 2)
            if Config.current_location.child2:
                self.draw_circle(self.white, Config.current_location.child2.pos, int(radius), 2)
        else:
            for locs_draw in self.loc_objects:
                if locs_draw.parent1 is None:
                    self.draw_circle(self.white, locs_draw.pos, int(radius), 2)
        
        #don't draw lines further than next layer at swamp
        if Config.current_adventure != 'swamp' or Config.scout_active:
            for node in self.loc_objects:
                if node.child1:
                    pg.draw.line(self.screen, self.white, node.pos, node.child1.pos, self.line_thickness)
                if node.child2:
                    pg.draw.line(self.screen, self.white, node.pos, node.child2.pos, self.line_thickness)

        self.path_sprites.draw(self.screen)

        if Config.scout_active:
            if self.hovered_item:
                desc_text = self.item_info_font.render(self.hovered_item.type.capitalize(), True, self.black)
                text_rect = desc_text.get_rect()
                offset_divisor = 54
                offset_y = self.screen_height // offset_divisor
                text_rect.topleft = (mouse_pos[0], mouse_pos[1] - offset_y)
        
                text_padding = 1
                rect_width = text_rect.width
                rect_height = text_rect.height
                
                rect_surface = pg.Surface((rect_width, rect_height))
                rect_surface.fill((self.white)) 
                self.screen.blit(rect_surface, (text_rect.left - text_padding, text_rect.top - text_padding))
                self.screen.blit(desc_text, text_rect.topleft)