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
        self.unused_sprites = pg.sprite.Group()
        self.rooms_done = 0
        self.red_arrows = []

    def cleanup(self):
        pass 
    def startup(self):
        self.screen.blit(self.ground, (0,0))
        locations = Data.location_data(States.current_adventure)
        self.loc_objects = [Location((loc["xpos"], loc["ypos"]), self.path_sprites, loc["desc"], loc["name"], loc["content"]) for loc in locations.values()]
        self.city, self.tree1, self.bush1, self.tree2, self.bush2, self.tree3, self.tree4, self.bush3, self.bush4, self.cave = self.loc_objects
 
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
        
        self.city.lwarrow = Arrow(((self.width * 0.38), (self.height * 0.77)), 50, self.path_sprites, self.tree1, "warrow")
        self.city.lrarrow = Arrow(((self.width * 0.38), (self.height * 0.77)), 50, self.unused_sprites, self.tree1, "rarrow")
        self.red_arrows.append(self.city.lrarrow)

        self.city.rwarrow = Arrow(((self.width * 0.62), (self.height * 0.77)), -50, self.path_sprites, self.bush1, "warrow")
        self.city.rrarrow = Arrow(((self.width * 0.62), (self.height * 0.77)), -50, self.unused_sprites, self.bush1, "rarrow")
        self.red_arrows.append(self.city.rrarrow)

        self.tree1.lwarrow = Arrow(((self.width * 0.24), (self.height * 0.57)), 50, self.path_sprites, self.tree2, "warrow")
        self.tree1.lrarrow = Arrow(((self.width * 0.24), (self.height * 0.57)), 50, self.unused_sprites, self.tree2, "rarrow")
        self.red_arrows.append(self.tree1.lrarrow)

        self.tree1.rwarrow = Arrow(((self.width * 0.36), (self.height * 0.57)), -50, self.path_sprites, self.bush2, "warrow")
        self.tree1.rrarrow = Arrow(((self.width * 0.36), (self.height * 0.57)), -50, self.unused_sprites, self.bush2, "rarrow")
        self.red_arrows.append(self.tree1.rrarrow)

        self.bush1.lwarrow = Arrow(((self.width * 0.64), (self.height * 0.57)), 50, self.path_sprites, self.tree3, "warrow")
        self.bush1.lrarrow = Arrow(((self.width * 0.64), (self.height * 0.57)), 50, self.unused_sprites, self.tree3, "rarrow")
        self.red_arrows.append(self.bush1.lrarrow)

        self.bush1.rwarrow = Arrow(((self.width * 0.76), (self.height * 0.57)), -50, self.path_sprites, self.tree4, "warrow")
        self.bush1.rrarrow = Arrow(((self.width * 0.76), (self.height * 0.57)), -50, self.unused_sprites, self.tree4, "rarrow")
        self.red_arrows.append(self.bush1.rrarrow)

        self.tree2.rwarrow = Arrow(((self.width * 0.24), (self.height * 0.33)), -50, self.path_sprites, self.bush3, "warrow")
        self.tree2.rrarrow = Arrow(((self.width * 0.24), (self.height * 0.33)), -50, self.unused_sprites, self.bush3, "rarrow")
        self.red_arrows.append(self.tree2.rrarrow)

        self.bush2.lwarrow = Arrow(((self.width * 0.36), (self.height * 0.33)), 50, self.path_sprites, self.bush3,  "warrow")
        self.bush2.lrarrow = Arrow(((self.width * 0.36), (self.height * 0.33)), 50, self.unused_sprites, self.bush3, "rarrow")
        self.red_arrows.append(self.bush2.lrarrow)

        self.tree3.rwarrow = Arrow(((self.width * 0.64), (self.height * 0.33)), -50, self.path_sprites, self.bush4, "warrow")
        self.tree3.rrarrow = Arrow(((self.width * 0.64), (self.height * 0.33)), -50, self.unused_sprites, self.bush4, "rarrow")
        self.red_arrows.append(self.tree3.rrarrow)

        self.tree4.lwarrow = Arrow(((self.width * 0.76), (self.height * 0.33)), 50, self.path_sprites, self.bush4, "warrow")
        self.tree4.lrarrow = Arrow(((self.width * 0.76), (self.height * 0.33)), 50, self.unused_sprites, self.bush4, "rarrow")
        self.red_arrows.append(self.tree4.lrarrow)

        self.bush3.rwarrow = Arrow(((self.width * 0.39), (self.height * 0.15)), -50, self.path_sprites, self.cave, "warrow")
        self.bush3.rrarrow = Arrow(((self.width * 0.39), (self.height * 0.15)), -50, self.unused_sprites, self.cave, "rarrow")
        self.red_arrows.append(self.bush3.rrarrow)

        self.bush4.lwarrow = Arrow(((self.width * 0.61), (self.height * 0.15)), 50, self.path_sprites, self.cave, "warrow")
        self.bush4.lrarrow = Arrow(((self.width * 0.61), (self.height * 0.15)), 50, self.unused_sprites, self.cave, "rarrow")
        self.red_arrows.append(self.bush4.lrarrow)
        
        self.city_text = self.info_font.render("Start City", True, self.black)
        self.city_text_rect = self.city_text.get_rect(bottomleft=(pg.mouse.get_pos()))

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
   
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.current_location.left.rect.collidepoint(pg.mouse.get_pos()):
                if self.current_location.left == self.city:
                    pass
                else:
                    States.room_monsters = self.current_location.left.content
                    self.current_location = self.current_location.left
                    self.done = True

            elif self.current_location.right.rect.collidepoint(pg.mouse.get_pos()):
                if self.current_location.right == self.city:
                    pass
                else:
                    States.room_monsters = self.current_location.right.content
                    self.current_location = self.current_location.right
                    self.done = True
          
        try:
            if self.current_location.left.rect.collidepoint(pg.mouse.get_pos()) == True:
                if self.current_location.left == self.city or self.current_location.lwarrow == None:
                    pass
                else:
                    self.path_sprites.remove(self.current_location.lwarrow)
                    self.path_sprites.add(self.current_location.lrarrow)
            else:   
                if self.current_location.left == self.city or self.current_location.lwarrow == None:
                    pass
                else:
                    self.path_sprites.remove(self.current_location.lrarrow)
                    self.path_sprites.add(self.current_location.lwarrow)

            if self.current_location.right.rect.collidepoint(pg.mouse.get_pos()) == True:
                if self.current_location.right == self.city or self.current_location.rwarrow == None:
                    pass
                else:
                    self.path_sprites.remove(self.current_location.rwarrow)
                    self.path_sprites.add(self.current_location.rrarrow)
            else:
                if self.current_location.right == self.city or self.current_location.rwarrow == None:
                    pass
                else:
                    self.path_sprites.remove(self.current_location.rrarrow)
                    self.path_sprites.add(self.current_location.rwarrow)
        except AttributeError:
            pass
             
    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.path_sprites.draw(self.screen)
        pg.draw.circle(self.screen, (self.red), (self.current_location.xpos, self.current_location.ypos), 20)
    