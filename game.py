import pygame as pg
import sys
import csv
import random
from states import States
from objects import Hero

class Game(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'map'
    def cleanup(self):
        self.names = []
    def startup(self):
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.selection_sprites = pg.sprite.Group()
        self.selectable_heroes = 8
        self.selection = []
        
        bubble = pg.image.load('./ab_images/menu_bubble.png')
        self.bubble = pg.transform.scale(bubble, ((bubble.get_width() / 8), (bubble.get_height() / 8)))
        self.bubble_rect = self.bubble.get_rect(bottomleft=(self.width * 0.12, self.height * 0.85))
        hood = pg.image.load('./ab_images/hood.png')
        self.hood = pg.transform.scale(hood, ((hood.get_width() / 8), (hood.get_height() / 8)))
        self.hood_rect = self.hood.get_rect(topleft=(self.width * 0.05, self.height * 0.80))

        def name_data():
            with open('./ab_data/names.csv', "r") as name:
                name_reader = csv.reader(name)
                self.names = list(tuple(row) for row in name_reader)
        name_data()
        self.available = random.sample(self.names, self.selectable_heroes)

        hero_xpos = (self.width * 0.20)
        for i in range(0,self.selectable_heroes):
            hero_ypos = (self.height * 0.2)
            if i > 3: #second row
                hero_ypos = (self.height * 0.5)
            self.i = Hero((hero_xpos, hero_ypos), self.hero_sprites, self.available[i][0], self.available[i][1])
            self.selection.append(self.i)
            self.selection_sprites.add(self.i)
            if i == 3:
                hero_xpos -= (self.width * 0.60)
            hero_xpos += (self.width * 0.15)
        
        continue_font = pg.font.SysFont("Arial", 50)
        self.continue_text = continue_font.render("CONTINUE", True, (127, 127, 127))
        self.ready_text = continue_font.render("CONTINUE", True, (0, 0, 0))
        self.continue_rect = self.continue_text.get_rect(center=(self.width * 0.75, self.height * 0.88))
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_rect.collidepoint(pg.mouse.get_pos()) and len(States.party_heroes) == self.max_party_size:
                self.done = True

            for s_hero in self.selection:
                if s_hero.rect.collidepoint(pg.mouse.get_pos()):
                    if s_hero.spot_frame == True:
                        s_hero.spot_frame = False
                        States.party_heroes.remove(s_hero) 
                    else:
                        s_hero.spot_frame = True
                        States.party_heroes.append(s_hero)

    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.selection_sprites.draw(self.screen)
        self.screen.blit(self.bubble, self.bubble_rect)
        self.screen.blit(self.hood, self.hood_rect)

        [pg.draw.rect(self.screen, self.red, [f_hero.xpos, f_hero.ypos, f_hero.width, f_hero.height], 2) for f_hero in self.selection if f_hero.spot_frame == True]
        
        if len(States.party_heroes) == self.max_party_size:
            self.screen.blit(self.ready_text, self.continue_rect)    
        else:
            self.screen.blit(self.continue_text, self.continue_rect)
        
        for shero in self.selection:
            if shero.rect.collidepoint(pg.mouse.get_pos()):
                info = shero.name.capitalize() + ", " + shero.type.capitalize()
                info_text = self.info_font.render(info, True, (0, 0, 0))
                info_text_rect = info_text.get_rect(topleft=((shero.xpos), (shero.ypos + (self.height / 7.1))))
                self.screen.blit(info_text, info_text_rect)
