import pygame as pg
import sys
from config_ab import Config
from sprites_ab import Adventure
from data_ab import get_data, row_to_dict
import pandas as pd


class WorldMap(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path'
        self.error = False
        self.line_thickness = 10

    def cleanup(self):
        self.map_objects = []
        self.map_sprites.empty()

    def startup(self):
        self.error = False
        self.line_thickness = 10

        map_data = get_data('adventures')
        self.map_objects = []
        for index, row in map_data.iterrows():
            name = row['name']
            coords = (row['pos_x'], row['pos_y'])
            desc = row['desc']
            child = row['child']
            adventure = Adventure(coords, self.map_sprites, desc, name, child)
            self.map_objects.append(adventure)


        def set_child(df):
            for obj in self.map_objects:
                obj_name = obj.name
                obj_child_name = df.loc[df['name'] == obj_name, 'child'].values[0]

                if pd.notna(obj_child_name):
                    obj.child = next((child_obj for child_obj in self.map_objects if child_obj.name == obj_child_name), None)
        set_child(map_data)

        bubble = pg.image.load('./ab_images/map_bubble.png').convert_alpha()
        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        COORDS_BUBBLE  = (self.screen_width * 0.12, self.screen_height * 0.85)
        COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
        SCALAR_BUBBLE = ((bubble.get_width() / 7), (bubble.get_height() / 7))
        SCALAR_HOOD = ((hood.get_width() / 8), (hood.get_height() / 8))

        self.bubble = pg.transform.smoothscale(bubble, SCALAR_BUBBLE)
        self.hood = pg.transform.smoothscale(hood, SCALAR_HOOD)
        self.bubble_rect = self.bubble.get_rect(bottomleft=COORDS_BUBBLE)
        self.hood_rect = self.hood.get_rect(topleft=COORDS_HOOD)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            for obj in self.map_objects:
                if obj.rect.collidepoint(pg.mouse.get_pos()):
                    if obj.name == 'dark_forest':
                        Config.current_adventure = obj.name
                        self.next = 'path'
                        self.done = True

                    else:
                        error = 'Inaccessible'
                        self.error_text = self.info_font.render((error), True, (self.red))
                        self.error_text_rect = self.error_text.get_rect(topleft=((obj.pos_x), (obj.pos_y))) 
                        self.error = True

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))

        for node in self.map_objects:
            if node.child:
                pg.draw.line(self.screen, self.white, node.pos, node.child.pos, self.line_thickness)

        self.map_sprites.draw(self.screen)

        self.screen.blit(self.bubble, self.bubble_rect)
        self.screen.blit(self.hood, self.hood_rect)

        collided_objects = [obj for obj in self.map_objects if obj.rect.collidepoint(pg.mouse.get_pos())]
        if collided_objects:
            obj = collided_objects[0]
            info_text = self.info_font.render(obj.desc, True, self.black)
            info_text_rect = info_text.get_rect(bottomleft=(obj.pos_x + obj.width // 2, obj.pos_y + obj.height // 2 + 5))
            self.screen.blit(info_text, info_text_rect)
            #create adv list, if obj.name == next item on list
            if obj.name == 'dark_forest':
                pg.draw.rect(self.screen, self.red, obj.rect, 2)
        
        if self.error == True:
            self.screen.blit(self.error_text, self.error_text_rect)