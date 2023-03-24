import pygame as pg
import sys
from states import States
from objects import Loc, Arrow

class Path(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'combat'
        self.path_sprites = pg.sprite.Group()
        self.unused_sprites = pg.sprite.Group()
        self.rooms_done = 0
        self.red_arrows = []
        #if path not cleared: next=combat and mob list = Loc mob lsit
        #next adventure_path 'path' need to give combat state monster information
    def cleanup(self):
        pass 
    def startup(self):
        self.ground = pg.image.load('./ab_kuvat/game_bg.png')
        self.screen.blit(self.ground, (0,0))

        #these as data files
        self.city = Loc(((self.width * 0.50), (self.height * 0.80)), self.path_sprites, "city", "city")
        self.tree1 = Loc(((self.width * 0.30), (self.height * 0.70)), self.path_sprites, "tree1", "tree")
        self.tree1.content = ["goblin", "goblin"]
        self.bush1 = Loc(((self.width * 0.70), (self.height * 0.70)), self.path_sprites, "bush1", "bush")
        self.bush1.content = ["goblin"]
        self.tree2 = Loc(((self.width * 0.17), (self.height * 0.45)), self.path_sprites, "tree2", "tree")
        self.tree2.content = ["goblin"]
        self.bush2 = Loc(((self.width * 0.43), (self.height * 0.45)), self.path_sprites, "bush2", "bush")
        self.bush2.content = ["goblin"]
        self.tree3 = Loc(((self.width * 0.57), (self.height * 0.45)), self.path_sprites, "tree3", "tree")
        self.tree3.content = ["goblin"]
        self.tree4 = Loc(((self.width * 0.83), (self.height * 0.45)), self.path_sprites, "tree4", "tree")
        self.tree4.content = ["goblin"]
        self.bush3 = Loc(((self.width * 0.30), (self.height * 0.20)), self.path_sprites, "bush3", "bush")
        self.bush3.content = ["goblin"]
        self.bush4 = Loc(((self.width * 0.70), (self.height * 0.20)), self.path_sprites, "bush4", "bush")
        self.bush4.content = ["goblin"]
        self.cave = Loc(((self.width * 0.50), (self.height * 0.10)), self.path_sprites, "cave", "cave")
        self.cave.content = ["troll"]

        self.city.left = self.tree1
        self.city.right = self.bush1

        self.tree1.left = self.tree2
        self.tree1.right = self.bush2

        self.bush1.left = self.tree3
        self.bush1.right = self.tree4

        self.tree2.right = self.bush3
        self.tree2.left = self.city

        self.bush2.left = self.bush3
        self.bush2.right = self.city

        self.tree3.right = self.bush4
        self.tree3.left = self.city
        
        self.tree4.left = self.bush4
        self.tree4.right = self.city

        self.bush3.right = self.cave
        self.bush3.left = self.city

        self.bush4.left = self.cave
        self.bush4.right = self.city
        
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

        self.bush3.rwarrow = Arrow(((self.width * 0.39), (self.height * 0.15)), -64, self.path_sprites, self.cave, "warrow")
        self.bush3.rrarrow = Arrow(((self.width * 0.39), (self.height * 0.15)), -64, self.unused_sprites, self.cave, "rarrow")
        self.red_arrows.append(self.bush3.rrarrow)

        self.bush4.lwarrow = Arrow(((self.width * 0.61), (self.height * 0.15)), 64, self.path_sprites, self.cave, "warrow")
        self.bush4.lrarrow = Arrow(((self.width * 0.61), (self.height * 0.15)), 64, self.unused_sprites, self.cave, "rarrow")
        self.red_arrows.append(self.bush4.lrarrow)
        
        path_font = pg.font.SysFont("Arial", 20)
        self.city_text = path_font.render("Start City", True, (0, 0, 0))
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
        pg.draw.circle(self.screen, (255,0,0), (self.current_location.xpos, self.current_location.ypos), 20)
    