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

    def cleanup(self):
        self.path_sprites.empty()
        self.loc_objects = []
    def startup(self):
        self.screen.blit(self.ground, (0,0))

        locations = Data.location_data(States.current_adventure)
        self.loc_objects = [Location((loc["pos_x"], loc["pos_y"]), self.path_sprites, loc["desc"], 
            loc["name"], loc["content"]) for loc in locations.values()]
        loc_names = [loc["desc"] for loc in locations.values()]
        for name, value in zip(loc_names, self.loc_objects):
            setattr(self, name, value)
        
        STARTING_LOCATION = self.loc_objects[0]

        loc_tree = Data.loc_tree_data(States.current_adventure)
        for parent, children in loc_tree.items():
            for dir, child_str in children.items():
                child_obj = getattr(self, child_str)
                setattr(getattr(self, parent), dir, child_obj)
        
        if States.current_location == None:
            States.current_location = STARTING_LOCATION
            #States.current_location = self.city
            self.current_location = States.current_location
        
        self.current_location = next((loc_object for loc_object in self.loc_objects if loc_object.desc == self.current_location.desc), None)

        self.arrows = Data.arrow_data(States.current_adventure)
        self.arrows = {name: {**data, 'origin': getattr(self, data['origin']), 'destination': getattr(self, data['destination'])} 
            for name, data in self.arrows.items()}
        [setattr(data['origin'], name, Arrow((data['pos_x'], data['pos_y']), data['angle'], self.path_sprites, data['destination'])) 
            for name, data in self.arrows.items()]

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

        for key, data in self.arrows.items():
            loc_instance = getattr(data['origin'], key)
            collides = data["destination"].rect.collidepoint(pg.mouse.get_pos())
            loc_instance.image = loc_instance.r_image if collides and self.current_location == data['origin'] else loc_instance.w_image

    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.path_sprites.draw(self.screen)
        pg.draw.circle(self.screen, (self.red), (self.current_location.pos_x, self.current_location.pos_y), 20)