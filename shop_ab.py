import pygame as pg
import sys
import random
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Button
from data_ab import get_data
from sounds_ab import sound_effect

#class Selection / HeroHire / Shop
#if Config.party_heroes not:
#show bubble
#else: coming to shop from path

#needs hire buttons

#HeroManager
class Shop(Config):
    def __init__(self):
        Config.__init__(self)
        #self.next = path if Config.current_adventure
        self.next = 'map'

    def cleanup(self):
        self.names = []
        self.selection = []
        self.selection_buttons = []
        self.selection_sprites.empty()
        self.selection_button_sprites.empty()

    def startup(self):
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.selection_button_sprites = pg.sprite.Group()
        self.selection_sprites = pg.sprite.Group()
        self.selection_buttons = []
        self.selection = []
        SELECTABLE_HEROES = 8
        
        bubble = pg.image.load('./ab_images/menu_bubble.png').convert_alpha()
        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        COORDS_BUBBLE  = (self.screen_width * 0.12, self.screen_height * 0.85)
        COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
        SCALAR_BUBBLE = ((bubble.get_width() / 8), (bubble.get_height() / 8))
        SCALAR_HOOD = ((hood.get_width() / 8), (hood.get_height() / 8))
        
        self.bubble = pg.transform.smoothscale(bubble, SCALAR_BUBBLE)
        self.hood = pg.transform.smoothscale(hood, SCALAR_HOOD)
        self.bubble_rect = self.bubble.get_rect(bottomleft=COORDS_BUBBLE)
        self.hood_rect = self.hood.get_rect(topleft=COORDS_HOOD)

        names_df = get_data('Names')
        self.names = [tuple(row) for row in names_df[['name', 'type']].values]
        self.available = random.sample(self.names, SELECTABLE_HEROES)

        #raise upper row to make room for hire buttons
        HEROPOS_X = (self.screen_width * 0.20)
        HEROPOS_Y_ROW1 = (self.screen_height * 0.20)
        HEROPOS_Y_ROW2 = (self.screen_height * 0.50)
        HERO_GAP = (self.screen_width * 0.15)
        HERO_ROW_LENGTH = (self.screen_width * 0.60)
        NEXT_ROW = 3

        for spot_hero in range(SELECTABLE_HEROES):
            HEROPOS_Y = HEROPOS_Y_ROW1
            if spot_hero > NEXT_ROW: 
                HEROPOS_Y = HEROPOS_Y_ROW2
            self.spot_hero = Hero(self.hero_sprites, (HEROPOS_X, HEROPOS_Y), self.available[spot_hero][0], self.available[spot_hero][1])
            self.selection.append(self.spot_hero)
            self.selection_sprites.add(self.spot_hero)
            if spot_hero == NEXT_ROW:
                HEROPOS_X -= HERO_ROW_LENGTH
            HEROPOS_X += HERO_GAP

        CONT_TEXT = "CONTINUE"
        CONT_FONT = self.default_font
        CONT_SIZE = self.big_font_size
        CONT_COL = self.black
        COORDS_CONT = (self.screen_width * 0.75, self.screen_height * 0.88)

        self.continue_button = Button(self.selection_button_sprites, CONT_TEXT, CONT_FONT, CONT_SIZE, CONT_COL, COORDS_CONT)
        self.selection_buttons.append(self.continue_button)
        

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(pg.mouse.get_pos()) and len(Config.party_heroes) == self.max_party_size:
                sound_effect('click')
                self.done = True
            elif self.continue_button.rect.collidepoint(pg.mouse.get_pos()):
                sound_effect('error')

            for selected_hero in self.selection:
                if selected_hero.rect.collidepoint(pg.mouse.get_pos()):
                    if selected_hero.spot_frame == True:
                        selected_hero.spot_frame = False
                        Config.party_heroes.remove(selected_hero) 
                    else:
                        selected_hero.spot_frame = True
                        Config.party_heroes.append(selected_hero)

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.selection_sprites.draw(self.screen)
        self.selection_button_sprites.draw(self.screen)
        self.screen.blit(self.bubble, self.bubble_rect)
        self.screen.blit(self.hood, self.hood_rect)

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        for frame_hero in self.selection:
            if frame_hero.spot_frame:
                frame_hero.draw_frame()
        
        if len(Config.party_heroes) == self.max_party_size:
            self.continue_button.border_color = self.black 
            self.continue_button.draw_border()
        else:
            self.continue_button.border_color = self.grey
            self.continue_button.draw_border()


        for shero in self.selection:
            if shero.rect.collidepoint(pg.mouse.get_pos()):
                COORDS_INFO = ((shero.pos_x), (shero.pos_y + (self.screen_height / 7.1))) # ?
                info = shero.name.capitalize() + ", " + shero.type.capitalize()
                info_text = self.info_font.render(info, True, self.black)
                info_text_rect = info_text.get_rect(topleft=COORDS_INFO)
                self.screen.blit(info_text, info_text_rect)