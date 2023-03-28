import pygame as pg
import sys
from states import States
from objects import Location, Arrow
from stats import Data

class Path(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'combat'
        self.path_sprites = pg.sprite.Group()
        self.rooms_done = 0
        self.red_left = False
        self.red_right = False

    def cleanup(self):
        self.path_sprites.empty()
        self.loc_objects = []
    def startup(self):
        self.screen.blit(self.ground, (0,0))

        locations = Data.location_data(States.current_adventure)
        self.loc_objects = [Location((loc["xpos"], loc["ypos"]), self.path_sprites, loc["desc"], 
            loc["name"], loc["content"]) for loc in locations.values()]
        loc_names = [loc["desc"] for loc in locations.values()]
        for name, value in zip(loc_names, self.loc_objects):
            setattr(self, name, value)

        loc_tree = {
        self.city: {'left': self.tree1, 'right': self.bush1},
        self.tree1: {'left': self.tree2, 'right': self.bush2},
        self.bush1: {'left': self.tree3, 'right': self.tree4},
        self.tree2: {'left': self.city, 'right': self.bush3},
        self.bush2: {'left': self.bush3, 'right': self.city},
        self.tree3: {'left': self.city, 'right': self.bush4},
        self.tree4: {'left': self.bush4, 'right': self.city},
        self.bush3: {'left': self.city, 'right': self.cave},
        self.bush4: {'left': self.cave, 'right': self.city}
        }
        for parent, children in loc_tree.items():
            for dir, child in children.items():
                setattr(parent, dir, child)
      
        if States.current_location == None:
            States.current_location = self.city
            self.current_location = States.current_location
          
        COORDS_CITY_L_ARROW = ((self.width * 0.38), (self.height * 0.77))
        COORDS_CITY_R_ARROW = ((self.width * 0.62), (self.height * 0.77))
        COORDS_TREE1_L_ARROW = ((self.width * 0.24), (self.height * 0.57))
        COORDS_TREE1_R_ARROW = ((self.width * 0.36), (self.height * 0.57))
        COORDS_BUSH1_L_ARROW = ((self.width * 0.64), (self.height * 0.57))
        COORDS_BUSH1_R_ARROW = ((self.width * 0.76), (self.height * 0.57))
        COORDS_BUSH2_L_ARROW = ((self.width * 0.36), (self.height * 0.33))
        COORDS_TREE2_R_ARROW = ((self.width * 0.24), (self.height * 0.33))
        COORDS_TREE4_L_ARROW = ((self.width * 0.76), (self.height * 0.33))
        COORDS_TREE3_R_ARROW = ((self.width * 0.64), (self.height * 0.33))
        COORDS_BUSH4_L_ARROW = ((self.width * 0.61), (self.height * 0.15))
        COORDS_BUSH3_R_ARROW = ((self.width * 0.39), (self.height * 0.15))
        
        ANGLE_LEFT_ARROW = 50
        ANGLE_RIGHT_ARROW = -50
        
        arrows = {
            'city_L_arrow': {
                'origin': self.city,
                'destination': self.tree1,
                'coords': COORDS_CITY_L_ARROW,
                'angle': ANGLE_LEFT_ARROW
            },
            'city_R_arrow': {
                'origin': self.city,
                'destination': self.bush1,
                'coords': COORDS_CITY_R_ARROW,
                'angle': ANGLE_RIGHT_ARROW
            },
            'tree1_L_arrow': {
                'origin': self.tree1,
                'destination': self.tree2,
                'coords': COORDS_TREE1_L_ARROW,
                'angle': ANGLE_LEFT_ARROW
            },
            'tree1_R_arrow': {
                'origin': self.tree1,
                'destination': self.bush2,
                'coords': COORDS_TREE1_R_ARROW,
                'angle': ANGLE_RIGHT_ARROW
            },
            'bush1_L_arrow': {
                'origin': self.bush1,
                'destination': self.tree3,
                'coords': COORDS_BUSH1_L_ARROW,
                'angle': ANGLE_LEFT_ARROW
            },
            'bush1_R_arrow': {
                'origin': self.bush1,
                'destination': self.tree4,
                'coords': COORDS_BUSH1_R_ARROW,
                'angle': ANGLE_RIGHT_ARROW
            },
            'bush2_L_arrow': {
                'origin': self.bush2,
                'destination': self.bush3,
                'coords': COORDS_BUSH2_L_ARROW,
                'angle': ANGLE_LEFT_ARROW
            },
            'tree2_R_arrow': {
                'origin': self.tree2,
                'destination': self.bush3,
                'coords': COORDS_TREE2_R_ARROW,
                'angle': ANGLE_RIGHT_ARROW
            },
            'tree4_L_arrow': {
                'origin': self.tree4,
                'destination': self.bush4,
                'coords': COORDS_TREE4_L_ARROW,
                'angle': ANGLE_LEFT_ARROW
            },
            'tree3_R_arrow': {
                'origin': self.tree3,
                'destination': self.bush4,
                'coords': COORDS_TREE3_R_ARROW,
                'angle': ANGLE_RIGHT_ARROW
            },
            'bush4_L_arrow': {
                'origin': self.bush4,
                'destination': self.cave,
                'coords': COORDS_BUSH4_L_ARROW,
                'angle': ANGLE_LEFT_ARROW
            },
            'bush3_R_arrow': {
                'origin': self.bush3,
                'destination': self.cave,
                'coords': COORDS_BUSH3_R_ARROW,
                'angle': ANGLE_RIGHT_ARROW
            }
        }   
        for name, data in arrows.items():
            #print("arrow name: " + name)
            #print("data.loc: " + str(data['coords']))
            setattr(data['origin'], name, Arrow(data['coords'], data['angle'], self.path_sprites, data['destination']))
        
        #arrows = Data.arrow_data(States.current_adventure) #curre adventure warrows
        #self.arrow_objects = [Arrow((arr["xpos"], arr["ypos"]), int(arr["angle"]), self.path_sprites, arr["desc"]) for arr in arrows.values()]

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            paths = [("left", self.current_location.left.content, self.current_location.left), 
                    ("right", self.current_location.right.content, self.current_location.right)]
            for path, content, location in paths:
                if location.rect.collidepoint(pg.mouse.get_pos()):
                    if location == self.city:
                        pass
                    else:
                        States.room_monsters = content
                        self.current_location = location
                        self.done = True
        try:
            if self.current_location.l_arrow.dest.rect.collidepoint(pg.mouse.get_pos()) == True: 
                self.red_left = True
            else:
                self.red_left = False

            if self.current_location.r_arrow.dest.rect.collidepoint(pg.mouse.get_pos()) == True: 
                self.red_right = True
            else:
                self.red_right = False
        except AttributeError:
            pass
    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.path_sprites.draw(self.screen)

        if self.red_left == True and self.current_location.l_arrow != None:
            self.screen.blit(self.current_location.l_arrow.r_image, self.current_location.l_arrow.rect)
        if self.red_right == True and self.current_location.r_arrow != None:
            self.screen.blit(self.current_location.r_arrow.r_image, self.current_location.r_arrow.rect)

        pg.draw.circle(self.screen, (self.red), (self.current_location.xpos, self.current_location.ypos), 20)