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
        self.backpack_items = []
        self.selection_sprites.empty()
        self.selection_button_sprites.empty()
        self.shop_icon_sprites.empty()
        self.shopping_sprites.empty()
        self.selling_item = False
        if not Config.current_adventure:
            for starting_hero in Config.party_heroes:
                starting_hero.equip_starting_weapon()

    def create_hero_selection(self, names_df, wizard_df, bard_df):
            SELECTABLE_HEROES = 8
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
                hero_name = self.available[spot_hero][0]
                hero_class = self.available[spot_hero][1]
                self.spot_hero = Hero(self.hero_sprites, (HEROPOS_X, HEROPOS_Y), hero_name, hero_class)
                self.selection.append(self.spot_hero)
                self.selection_sprites.add(self.spot_hero)
                if spot_hero == NEXT_ROW:
                    HEROPOS_X -= HERO_ROW_LENGTH
                HEROPOS_X += HERO_GAP
            
            wizard_spells = wizard_df[wizard_df['type'] == 'spell']
            bard_spells = bard_df[bard_df['type'] == 'spell']

            for created_hero in self.selection:
                if created_hero.type in ['bard', 'wizard']:
                    if created_hero.type == 'bard':
                        random_row = bard_spells.sample(n=1)
                    else:
                        random_row = wizard_spells.sample(n=1)
                    talent_name = random_row['name'].iloc[0]  
                    talent_type = 'spell'
                    created_hero.add_talent(talent_name, talent_type)

    def sell_item(self, sold_item):
        payment = sold_item.sell_value
        Config.gold_count += payment
        slot = sold_item.inventory_spot
        Config.party_backpack[slot.name] = None
        self.backpack_items.remove(sold_item)
        self.shop_icon_sprites.remove(sold_item)

    def startup(self):
        self.selection = []
        self.backpack_items = []
        self.selection_sprites = pg.sprite.Group()
        self.selection_button_sprites = pg.sprite.Group()
        self.shop_icon_sprites = pg.sprite.Group()
        self.shopping_sprites = pg.sprite.Group()
        self.selling_item = False
        
        #raise rows to make room for hire buttons
        if not Config.current_adventure:
            hood = pg.image.load('./ab_images/hood.png').convert_alpha()
            COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
            SCALAR_HOOD = ((hood.get_width() / self.npc_size_scalar), (hood.get_height() / self.npc_size_scalar))

            self.coords_dialogue_1 = ((self.screen_width * 0.12, self.screen_height * 0.72))
            self.shop_dialogue_1 = ['"Choose three heroes', 'and press continue"']
            self.hood_image = pg.transform.smoothscale(hood, SCALAR_HOOD)
            self.hood_rect = self.hood_image.get_rect(topleft=COORDS_HOOD)

            names_df = get_data('Names')
            wizard_df = (get_talent_data('wizard'))
            bard_df = (get_talent_data('bard'))
            self.create_hero_selection(names_df, wizard_df, bard_df)

        if Config.current_adventure:
            inventory_instance = Inventory()
            inventory_instance.backpack_to_slots(self.backpack_items, self.shop_icon_sprites)

            shopkeeper = pg.image.load('./ab_images/shopkeeper.png').convert_alpha()
            sell_cursor = pg.image.load('./ab_images/sell_arrow.png').convert_alpha() 
            COORDS_SHOPKEEPER = (self.screen_width * 0.50, self.screen_height * 0.15)
            SCALAR_SHOPKEEPER = ((shopkeeper.get_width() / self.npc_size_scalar), (shopkeeper.get_height() / self.npc_size_scalar))
            cursor_size_scalar = 30
            SCALAR_CURSOR = ((sell_cursor.get_width() / cursor_size_scalar), (sell_cursor.get_height() / cursor_size_scalar))

            self.coords_dialogue_2 = (self.screen_width * 0.55, self.screen_height * 0.10)
            self.shop_dialogue_2 = '"I have some wares to sell"'
            self.shopkeeper_image = pg.transform.smoothscale(shopkeeper, SCALAR_SHOPKEEPER)
            self.shopkeeper_rect = self.shopkeeper_image.get_rect(topleft=COORDS_SHOPKEEPER)
            self.sell_cursor_image = pg.transform.smoothscale(sell_cursor, SCALAR_CURSOR)
            self.sell_cursor_rect = self.sell_cursor_image.get_rect()

            sell_text = 'Sell Item'
            SELL_COORDS = (self.screen_width * 0.30, self.screen_height * 0.13)
            self.sell_item_button = Button(self.shopping_sprites, sell_text, self.info_font_name, self.info_font_size, self.black, SELL_COORDS)

        self.continue_button = Button(self.selection_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(mouse_pos):
                if len(Config.party_heroes) == self.max_party_size:
                    play_sound_effect('click')
                    if Config.current_adventure is None:
                        self.next = 'map'
                    else:
                        self.next = 'path'
                    self.done = True
                else:
                    play_sound_effect('error')

            for selected_hero in self.selection:
                if selected_hero.rect.collidepoint(mouse_pos):
                    if selected_hero.spot_frame == True:
                        selected_hero.spot_frame = False
                        Config.party_heroes.remove(selected_hero) 
                    else:
                        selected_hero.spot_frame = True
                        Config.party_heroes.append(selected_hero)

            if Config.current_adventure:
                if self.sell_item_button.rect.collidepoint(mouse_pos):
                    self.selling_item = True
                    pg.mouse.set_visible(False)

                if self.selling_item:
                    if event.button == self.secondary_mouse_button:
                        self.selling_item = False
                        pg.mouse.set_visible(True)
                    else:
                        for backpack_item in self.backpack_items:
                                if backpack_item.rect.collidepoint(mouse_pos):
                                    self.sell_item(backpack_item)
                                    self.selling_item = False
                                    pg.mouse.set_visible(True)
                                    play_sound_effect('sell')

        elif event.type == pg.MOUSEMOTION:
            for hover_item in self.backpack_items:
                if hover_item.rect.collidepoint(mouse_pos):
                    self.hovered_item = hover_item
                    break
                else:
                    self.hovered_item = None

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.selection_button_sprites.draw(self.screen)
        
        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        if Config.current_adventure:
            self.screen.blit(self.shopkeeper_image, self.shopkeeper_rect)
            shop_text = self.dialogue_font.render(self.shop_dialogue_2, True, self.black)
            shop_text_rect = shop_text.get_rect(center=self.coords_dialogue_2)
            self.screen.blit(shop_text, shop_text_rect)

            for backpack_slot in Config.backpack_slots:
                backpack_slot.draw_border()
            self.shop_icon_sprites.draw(self.screen)
            self.shopping_sprites.draw(self.screen)

            if self.selling_item:
                mouse_pos = pg.mouse.get_pos()
                self.screen.blit(self.sell_cursor_image, mouse_pos)
                
                offset_y = self.screen_height // 54
                if self.hovered_item:
                    desc_text = self.med_info_font.render(self.hovered_item.desc, True, self.black)
                    self.screen.blit(desc_text, (mouse_pos[0], mouse_pos[1] - offset_y))

        if not Config.current_adventure:
            self.screen.blit(self.hood_image, self.hood_rect)
            self.selection_sprites.draw(self.screen)

            for i, dia_line in enumerate(self.shop_dialogue_1):
                dia_line_text = self.dialogue_font.render(dia_line, True, self.black)
                dia_line_rect = dia_line_text.get_rect(center=(self.coords_dialogue_1[0], self.coords_dialogue_1[1] + i * self.medium_font_size))
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