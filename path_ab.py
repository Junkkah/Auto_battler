import pygame as pg
from config_ab import Config
from sprites_ab import Location, Button
from hero_ab import Hero
from data_ab import get_data, get_monster_encounters
from sounds_ab import play_music_effect, play_sound_effect
import pandas as pd
import math
import random


class Path(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'battle'
        self.rooms_done = 0
        self.line_thickness = 5
        self.max_pulse_radius = 50
        self.pulsation_speed = 0.005
        self.hovered_item = None

    def cleanup(self):
        self.path_sprites.empty()
        self.loc_objects = []
        self.hovered_item = None

    def create_encounter(self, tier) -> list:
        encounters_df = get_monster_encounters(Config.current_adventure, tier)
        probs = encounters_df['Probability'].tolist()
        mob_lists = encounters_df.apply(lambda row: [value for value in row[4:].tolist() if value is not None], axis=1).tolist()
        encounter = random.choices(mob_lists, weights=probs, k=1)[0]
        return encounter
    
    def startup(self):
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

        def set_children(df):
            #assign locations objects as child nodes
            for loc_object in self.loc_objects:
                obj_name = loc_object.name
                obj_child1_name = df.loc[df['name'] == obj_name, 'child1'].values[0]
                obj_child2_name = df.loc[df['name'] == obj_name, 'child2'].values[0]

                if pd.notna(obj_child1_name):
                    loc_object.child1 = next((child_obj for child_obj in self.loc_objects if child_obj.name == obj_child1_name), None)
                if pd.notna(obj_child2_name):
                    loc_object.child2 = next((child_obj for child_obj in self.loc_objects if child_obj.name == obj_child2_name), None)
        set_children(locations_data)

        self.COORDS_INV = (self.screen_width * 0.91, self.screen_height * 0.95)
        self.COORDS_INFO = (self.screen_width * 0.06, self.screen_height * 0.95)

        INV_TEXT = 'Inventory (i)'
        self.inventory_button = Button(self.path_sprites, INV_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_INV)
        INFO_TEXT = 'Info (f)'
        self.info_button = Button(self.path_sprites, INFO_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_INFO)


    def get_event(self, event):
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
        self.draw(screen)

    def draw_circle(self, color, center, radius, thickness):
        pg.draw.circle(self.screen, color, center, radius, thickness)
    
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        mouse_pos = pg.mouse.get_pos()
        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        radius = self.max_pulse_radius * abs(math.sin(pg.time.get_ticks() * self.pulsation_speed))

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
                desc_text = self.item_info_font.render(self.hovered_item.type, True, self.black)
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