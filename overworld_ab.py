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

    def generate_random_path(self, adventure: str):
        pass

    def startup(self):
        self.error = False
        self.line_thickness = 10
        self.rect_thickness = 2
        self.text_offset_y = 5

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

        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        self.coords_dialogue = ((self.screen_width * 0.12, self.screen_height * 0.72))
        COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
        SCALAR_HOOD = ((hood.get_width() / self.npc_size_scalar), (hood.get_height() / self.npc_size_scalar))

        self.overworld_dialogue = ['"Choose Dark Forest for', 'your first adventure"']

        self.hood_image = pg.transform.smoothscale(hood, SCALAR_HOOD)
        self.hood_rect = self.hood_image.get_rect(topleft=COORDS_HOOD)

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            for obj in self.map_objects:
                if obj.rect.collidepoint(mouse_pos):
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

        for i, dia_line in enumerate(self.overworld_dialogue):
            dia_line_text = self.dialogue_font.render(dia_line, True, self.black)
            dia_line_rect = dia_line_text.get_rect(center=(self.coords_dialogue[0], self.coords_dialogue[1] + i * self.medium_font_size))
            self.screen.blit(dia_line_text, dia_line_rect)

        self.screen.blit(self.hood_image, self.hood_rect)

        collided_objects = [obj for obj in self.map_objects if obj.rect.collidepoint(pg.mouse.get_pos())]
        if collided_objects:
            obj = collided_objects[0]
            info_text = self.info_font.render(obj.desc, True, self.black)
            info_text_rect = info_text.get_rect(bottomleft=(obj.pos_x + obj.width // 2, obj.pos_y + obj.height // 2 + self.text_offset_y))
            self.screen.blit(info_text, info_text_rect)
            #create adv list, if obj.name == next item on list
            if obj.name == 'dark_forest':
                pg.draw.rect(self.screen, self.red, obj.rect, self.rect_thickness)
        
        if self.error == True:
            self.screen.blit(self.error_text, self.error_text_rect)