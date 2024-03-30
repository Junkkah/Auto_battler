import pygame as pg
import sys
import random
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Button, EquipmentSlot
from inventory_ab import Inventory
from data_ab import get_data, get_talent_data
from sounds_ab import play_sound_effect
import pandas as pd


class Shop(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'map'

    def cleanup(self):
        self.names = []
        self.selection = []
        self.selection_buttons = []
        self.backpack_items = []
        self.selection_sprites.empty()
        self.selection_button_sprites.empty()
        self.shop_icon_sprites.empty()
        if not Config.current_adventure:
            for starting_hero in Config.party_heroes:
                starting_hero.equip_starting_weapon()

    def startup(self):
        self.selection = []
        self.selection_buttons = []
        self.backpack_items = []
        self.selection_sprites = pg.sprite.Group()
        self.selection_button_sprites = pg.sprite.Group()
        self.shop_icon_sprites = pg.sprite.Group()
        SELECTABLE_HEROES = 8

        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        self.coords_dialogue = ((self.screen_width * 0.12, self.screen_height * 0.72))
        COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
        SCALAR_HOOD = ((hood.get_width() / self.npc_size_scalar), (hood.get_height() / self.npc_size_scalar))
        
        self.shop_dialogue_1 = ['Choose three heroes', 'and press CONTINUE']
        self.hood = pg.transform.smoothscale(hood, SCALAR_HOOD)
        self.hood_rect = self.hood.get_rect(topleft=COORDS_HOOD)

        #raise rows to make room for hire buttons
        if not Config.current_adventure:
            names_df = get_data('Names')
            self.names = [tuple(row) for row in names_df[['name', 'type']].values]
            self.available = random.sample(self.names, SELECTABLE_HEROES)

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
            
            wizard_df = (get_talent_data('wizard'))
            bard_df = (get_talent_data('bard'))
            wizard_spells = wizard_df[wizard_df['type'] == 'spell']
            bard_spells = bard_df[bard_df['type'] == 'spell']

            for created_hero in self.selection:
                if created_hero.type == 'wizard':
                    random_row = wizard_spells.sample(n=1)
                    talent_name = random_row['name'].iloc[0]  
                    talent_type = 'spell'
                    created_hero.add_talent(talent_name, talent_type)

                if created_hero.type == 'bard':
                    random_row = bard_spells.sample(n=1)
                    talent_name = random_row['name'].iloc[0]  
                    talent_type = 'spell'
                    created_hero.add_talent(talent_name, talent_type)

        if Config.current_adventure:
            inventory_instance = Inventory()
            inventory_instance.backpack_to_slots(self.backpack_items, self.shop_icon_sprites)
        
        self.continue_button = Button(self.selection_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)
        self.selection_buttons.append(self.continue_button)
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(pg.mouse.get_pos()) and len(Config.party_heroes) == self.max_party_size:
                play_sound_effect('click')
                if Config.current_adventure is None:
                    self.next = 'map'
                else:
                    self.next = 'path'
                self.done = True

            elif self.continue_button.rect.collidepoint(pg.mouse.get_pos()):
                play_sound_effect('error')

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
        self.selection_button_sprites.draw(self.screen)
        self.screen.blit(self.hood, self.hood_rect)

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        if Config.current_adventure:
            COORDS_SHOP = (self.screen_width * 0.50, self.screen_height * 0.10)
            shop = 'Shop'
            shop_text = self.large_info_font.render(shop, True, self.black)
            shop_text_rect = shop_text.get_rect(center=COORDS_SHOP)
            self.screen.blit(shop_text, shop_text_rect)

            for backpack_slot in Config.backpack_slots:
                backpack_slot.draw_border()
            self.shop_icon_sprites.draw(self.screen)

        if not Config.current_adventure:
            self.selection_sprites.draw(self.screen)

            for i, dia_line in enumerate(self.shop_dialogue_1):
                dia_line_text = self.dialogue_font.render(dia_line, True, self.black)
                dia_line_rect = dia_line_text.get_rect(center=(self.coords_dialogue[0], self.coords_dialogue[1] + i * self.medium_font_size))
                self.screen.blit(dia_line_text, dia_line_rect)

            for frame_hero in self.selection:
                if frame_hero.spot_frame:
                    frame_hero.draw_frame()
            
            for shero in self.selection:
                if shero.rect.collidepoint(pg.mouse.get_pos()):
                    OFFSET = self.screen_height / 7.1
                    COORDS_INFO_X = shero.pos_x
                    COORDS_INFO_Y = shero.pos_y + OFFSET
                    info = shero.name.capitalize() + ', ' + shero.type.capitalize()
                    info_text = self.info_font.render(info, True, self.black)
                    info_text_rect = info_text.get_rect(topleft=(COORDS_INFO_X, COORDS_INFO_Y))
                    self.screen.blit(info_text, info_text_rect)
                    if shero.talents:
                        TALENT_OFFSET = info_text.get_height()
                        COORDS_TALENT_X = COORDS_INFO_X
                        COORDS_TALENT_Y = COORDS_INFO_Y + TALENT_OFFSET
                        talent_info = shero.talents[0].capitalize()
                        talent_text = self.info_font.render(talent_info, True, self.black)
                        talent_text_rect = info_text.get_rect(topleft=(COORDS_TALENT_X, COORDS_TALENT_Y))
                        self.screen.blit(talent_text, talent_text_rect)

        if len(Config.party_heroes) == self.max_party_size:
            self.continue_button.border_color = self.black 
            self.continue_button.draw_border()
        else:
            self.continue_button.border_color = self.grey
            self.continue_button.draw_border()