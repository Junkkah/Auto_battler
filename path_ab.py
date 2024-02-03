import pygame as pg
#import sys
from states import States
from objects import Location
from data_ab import get_data, get_adv_monsters
import pandas as pd
import math

#create list of town names, randomly pick town name from list
#determine buyble stuff in town for each name

class Path(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'combat'
        self.rooms_done = 0
        self.line_thickness = 5
        self.max_pulse_radius = 50
        self.pulsation_speed = 0.005

        self.adventure_monsters = get_adv_monsters(States.current_adventure)
        #boss in adventure column or as content in cave loc

        self.content = ['goblin']


    def create_content(self, location):
        tier = location.tier
        #tier1 fights: goblin(2), goblin + kobold(3), orc(4)
        #tier2 fights: orc(4), orc + goblin(6), goblin + goblin(4), goblin_wizard(5)
        #tier3
        #tier4
        #boss fight: troll_berserk


    def cleanup(self):
        self.path_sprites.empty()
        self.loc_objects = []

    def startup(self):

        self.loc_objects = []
        locations_data = get_data(States.current_adventure)

        for index, row in locations_data.iterrows():
            name = row['name']
            image_name = row['image_name']
            new_location = Location(self.path_sprites, row)
            self.loc_objects.append(new_location)

        def set_children(df):
            for obj in self.loc_objects:
                obj_name = obj.name
                obj_child1_name = df.loc[df['name'] == obj_name, 'child1'].values[0]
                obj_child2_name = df.loc[df['name'] == obj_name, 'child2'].values[0]

                if pd.notna(obj_child1_name):
                    obj.child1 = next((child_obj for child_obj in self.loc_objects if child_obj.name == obj_child1_name), None)
                if pd.notna(obj_child2_name):
                    obj.child2 = next((child_obj for child_obj in self.loc_objects if child_obj.name == obj_child2_name), None)
        set_children(locations_data)
    

    #randomized paths


    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:

            clicked_location = None
            if self.current_location:
                for child in [self.current_location.child1, self.current_location.child2]:
                    if child and child.rect.collidepoint(pg.mouse.get_pos()):
                        clicked_location = child
                        break  

            if not clicked_location:
                for locs_click in self.loc_objects:
                    if locs_click.parent1 is None and locs_click.rect.collidepoint(pg.mouse.get_pos()):
                        clicked_location = locs_click
                        break 

            if clicked_location and clicked_location.type == 'fight':
                #States.room_monsters = self.create_content(clicked_location)
                States.room_monsters = self.content  
                self.current_location = clicked_location
                self.next = 'combat'
                self.done = True
            
            if clicked_location and clicked_location.type == 'shop':
                self.current_location = clicked_location
                self.next = 'shop'
                self.done = True


    def update(self, screen, dt):
        self.draw(screen)

    def draw_line(self, color, thickness, start_point, end_point):
        pg.draw.line(self.screen, color, start_point, end_point, thickness)

    def draw_circle(self, color, center, radius, thickness):
        pg.draw.circle(self.screen, color, center, radius, thickness)
    

    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))

        radius = self.max_pulse_radius * abs(math.sin(pg.time.get_ticks() * self.pulsation_speed))

        if self.current_location:
            self.draw_circle(self.white, self.current_location.child1.pos, int(radius), 2)
            if self.current_location.child2:
                self.draw_circle(self.white, self.current_location.child2.pos, int(radius), 2)
        else:
            for locs_draw in self.loc_objects:
                if locs_draw.parent1 is None:
                    self.draw_circle(self.white, locs_draw.pos, int(radius), 2)

        for node in self.loc_objects:
            if node.child1:
                self.draw_line(self.white, self.line_thickness, node.pos, node.child1.pos)
            if node.child2:
                self.draw_line(self.white, self.line_thickness, node.pos, node.child2.pos)

        
        self.path_sprites.draw(self.screen)