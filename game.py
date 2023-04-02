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
        self.selection = []
        SELECTABLE_HEROES = 8
        
        bubble = pg.image.load('./ab_images/menu_bubble.png').convert_alpha()
        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        COORDS_BUBBLE  = (self.width * 0.12, self.height * 0.85)
        COORDS_HOOD = (self.width * 0.05, self.height * 0.80)
        SCALAR_BUBBLE = ((bubble.get_width() / 8), (bubble.get_height() / 8))
        SCALAR_HOOD = ((hood.get_width() / 8), (hood.get_height() / 8))
        
        self.bubble = pg.transform.scale(bubble, SCALAR_BUBBLE)
        self.hood = pg.transform.scale(hood, SCALAR_HOOD)
        self.bubble_rect = self.bubble.get_rect(bottomleft=COORDS_BUBBLE)
        self.hood_rect = self.hood.get_rect(topleft=COORDS_HOOD)

        def name_data():
            with open('./ab_data/names.csv', "r") as name:
                name_reader = csv.reader(name)
                self.names = list(tuple(row) for row in name_reader)
        name_data()
        self.available = random.sample(self.names, SELECTABLE_HEROES)

        HEROPOS_X = (self.width * 0.20)
        HEROPOS_Y_ROW1 = (self.height * 0.20)
        HEROPOS_Y_ROW2 = (self.height * 0.50)
        HERO_GAP = (self.width * 0.15)
        HERO_ROW_LENGTH = (self.width * 0.60)
        NEXT_ROW = 3

        for spot_hero in range(SELECTABLE_HEROES):
            HEROPOS_Y = HEROPOS_Y_ROW1
            if spot_hero > NEXT_ROW: 
                HEROPOS_Y = HEROPOS_Y_ROW2
            self.spot_hero = Hero((HEROPOS_X, HEROPOS_Y), self.hero_sprites, self.available[spot_hero][0], self.available[spot_hero][1])
            self.selection.append(self.spot_hero)
            self.selection_sprites.add(self.spot_hero)
            if spot_hero == NEXT_ROW:
                HEROPOS_X -= HERO_ROW_LENGTH
            HEROPOS_X += HERO_GAP
        
        CONTINUE_FONT = pg.font.SysFont("Arial", self.big_font_size)
        self.continue_text = CONTINUE_FONT.render("CONTINUE", True, self.grey)
        self.ready_text = CONTINUE_FONT.render("CONTINUE", True, self.black)
        COORDS_CONTINUE = (self.width * 0.75, self.height * 0.88)
        self.continue_rect = self.continue_text.get_rect(center=COORDS_CONTINUE)
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_rect.collidepoint(pg.mouse.get_pos()) and len(States.party_heroes) == self.max_party_size:
                self.done = True

            for selected_hero in self.selection:
                if selected_hero.rect.collidepoint(pg.mouse.get_pos()):
                    if selected_hero.spot_frame == True:
                        selected_hero.spot_frame = False
                        States.party_heroes.remove(selected_hero) 
                    else:
                        selected_hero.spot_frame = True
                        States.party_heroes.append(selected_hero)

    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.selection_sprites.draw(self.screen)
        self.screen.blit(self.bubble, self.bubble_rect)
        self.screen.blit(self.hood, self.hood_rect)

        [pg.draw.rect(self.screen, self.red, [f_hero.pos_x, f_hero.pos_y, f_hero.width, f_hero.height], 2) for f_hero in self.selection if f_hero.spot_frame == True]
        
        if len(States.party_heroes) == self.max_party_size:
            self.screen.blit(self.ready_text, self.continue_rect)    
        else:
            self.screen.blit(self.continue_text, self.continue_rect)
        
        for shero in self.selection:
            if shero.rect.collidepoint(pg.mouse.get_pos()):
                COORDS_INFO = ((shero.pos_x), (shero.pos_y + (self.height / 7.1)))
                info = shero.name.capitalize() + ", " + shero.type.capitalize()
                info_text = self.info_font.render(info, True, self.black)
                info_text_rect = info_text.get_rect(topleft=COORDS_INFO)
                self.screen.blit(info_text, info_text_rect)
