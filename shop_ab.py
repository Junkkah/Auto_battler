"""
Shop Module.

This module contains class for managing the shop functionality of the game.

Classes:
    Shop: Handles the shop screen when entering a shop.
"""

import pygame as pg
import sys
import random
import itertools
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Button, EquipmentSlot
from inventory_ab import Inventory
from data_ab import get_data, get_talent_data, get_json_data
from sounds_ab import play_sound_effect
from items_ab import ItemManager
from talents_ab import TalentsManager
import pandas as pd

class Shop(Config):
    """
    Shop screen for the game.

    This class handles drawing the shop and hero selection interface 
    and processing events for purchasing, selling and moving items.
    """

    def __init__(self):
        """Initialize Shop with default settings and set next state to 'map'."""
        super().__init__()
        self.next = 'map'

    def cleanup(self):
        """Reset class-specific variables and clear associated sprites."""
        self.names = []
        self.selection = []
        self.backpack_items = []
        self.item_selection = []
        self.buy_buttons = []
        self.selection_sprites.empty()
        self.selection_button_sprites.empty()
        self.shop_icon_sprites.empty()
        self.shopping_sprites.empty()
        self.selling_item = False
        if not Config.current_adventure:
            for starting_hero in Config.party_heroes:
                starting_hero.equip_starting_weapon()

    def create_hero_selection(self, names_df):
        """Create a selection of hero objects from a DataFrame and return them."""
        SELECTABLE_HEROES = 8
        names = [tuple(row) for row in names_df[['name', 'type']].values]
        available = random.sample(names, SELECTABLE_HEROES)
        hero_selection = []
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
            hero_name = available[spot_hero][0]
            hero_class = available[spot_hero][1]
            self.spot_hero = Hero(self.hero_sprites, (HEROPOS_X, HEROPOS_Y), hero_name, hero_class)
            hero_selection.append(self.spot_hero)
            self.selection_sprites.add(self.spot_hero)
            if spot_hero == NEXT_ROW:
                HEROPOS_X -= HERO_ROW_LENGTH
            HEROPOS_X += HERO_GAP
        return hero_selection
            
    def create_starting_spells(self, wizard_df, bard_df, hero_list):
        """Assign starting spells or songs to wizards and bards in the hero list."""
        wizard_spells = wizard_df[(wizard_df['type'] == 'spell') & (wizard_df['min_level'] == 1)]
        bard_songs = bard_df[(bard_df['type'] == 'song') & (bard_df['min_level'] == 1)]

        for created_hero in hero_list:
            if created_hero.type in ['bard', 'wizard']:
                if created_hero.type == 'bard':
                    talent_type = 'song'
                    talent_name = 'Loud Tune'
                else:
                    random_row = wizard_spells.sample(n=1)
                    talent_type = 'spell'
                    talent_name = random_row['name'].iloc[0]  
                TalentsManager.add_talent(talent_name, talent_type, created_hero)

    def create_item_selection(self):
        """Create a selection of items and return them."""
        item_selection = []
        num_items = 3 #random.randint(1, 3)
        item_probabilities = get_json_data('item_probabilities')
        for i in range(num_items):
            item = ItemManager.create_random_item(item_probabilities)
            item.inventory_spot = i + 1
            item_selection.append(item)
        return item_selection

    def position_item_selection(self, item_selection):
        """Set coordinates for items in item selection."""
        y = 0.40
        item_count = len(item_selection)
        pos_y = self.screen_height * y
        denominator = 14
        start = 5
        item_x_coords = [((i * 2) + start) / denominator for i in range(item_count)]

        for j, x in enumerate(item_x_coords):
            pos_x = self.screen_width * x
            item_selection[j].rect.x = pos_x
            item_selection[j].rect.y = pos_y
            self.shop_icon_sprites.add(item_selection[j])

    def sell_item(self, sold_item):
        """Sell the given item to the shopkeeper."""
        payment = sold_item.sell_value
        Config.gold_count += payment
        slot = sold_item.inventory_spot
        Config.party_backpack[slot.name] = None
        self.backpack_items.remove(sold_item)
        self.shop_icon_sprites.remove(sold_item)
    
    def startup(self):
        """Initialize resources and set up the shop state."""
        self.selection = []
        self.backpack_items = []
        self.selection_sprites = pg.sprite.Group()
        self.selection_button_sprites = pg.sprite.Group()
        self.shop_icon_sprites = pg.sprite.Group()
        self.shopping_sprites = pg.sprite.Group()
        self.selling_item = False
        self.hovered_item = None
        
        if not Config.current_adventure:
            self.coords_dialogue_1 = ((self.screen_width * 0.12, self.screen_height * 0.72))
            self.shop_dialogue_1 = ['"Choose three heroes', 'and press continue"']
            COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
            hood_path = './ab_images/hood.png'
            self.hood_image = self.load_and_scale_image(hood_path, self.npc_size_scalar)
            self.hood_rect = self.hood_image.get_rect(topleft=COORDS_HOOD)

            names_df = get_data('names')
            wizard_df = (get_talent_data('wizard'))
            bard_df = (get_talent_data('bard'))
            self.selection = self.create_hero_selection(names_df)
            self.create_starting_spells(wizard_df, bard_df, self.selection)

        if Config.current_adventure:
            Inventory.backpack_to_slots(self.backpack_items, self.shop_icon_sprites)

            COORDS_SHOPKEEPER = (self.screen_width * 0.48, self.screen_height * 0.15)
            shopkeeper_path = './ab_images/shopkeeper.png'
            self.shopkeeper_image = self.load_and_scale_image(shopkeeper_path, self.npc_size_scalar)
            self.shopkeeper_rect = self.shopkeeper_image.get_rect(topleft=COORDS_SHOPKEEPER)

            cursor_path = './ab_images/sell_arrow.png'
            cursor_size_scalar = 30
            self.sell_cursor_image = self.load_and_scale_image(cursor_path, cursor_size_scalar)
            self.sell_cursor_rect = self.sell_cursor_image.get_rect()

            self.coords_dialogue_2 = (self.screen_width * 0.53, self.screen_height * 0.10)
            self.shop_dialogue_2 = '"I have some wares to sell"'

            sell_text = 'Sell Item'
            SELL_COORDS = (self.screen_width * 0.30, self.screen_height * 0.13)
            self.sell_item_button = Button(self.shopping_sprites, sell_text, self.info_font_name, self.info_font_size, self.black, SELL_COORDS)
            self.item_selection = self.create_item_selection()
            self.position_item_selection(self.item_selection)
            
            self.buy_buttons = []
            for i, item in enumerate(self.item_selection):
                #item_type based prices in json
                #weapon x20, armor x15, cons x10
                price_multiplier = 15
                price_var_min = 10
                price_var_max = 25
                item_price = item.modifier_tier * price_multiplier + (random.randint(price_var_min, price_var_max))
                item_price -= Config.party_discount
                item.buy_value = item_price
                buy_text = f'Buy for: {item_price}'
                item_x = self.item_selection[i].rect.x
                item_y = self.item_selection[i].rect.y
                offset_x =  item.image.get_width() // 2
                offset_y =  item.image.get_height() * 2
                COORDS_BUY = (item_x + offset_x, item_y + offset_y)
                buy_button = Button(self.selection_button_sprites, buy_text, self.info_font_name, self.info_font_size, self.black, COORDS_BUY)
                self.buy_buttons.append(buy_button)

        self.continue_button = Button(self.selection_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)

    def get_event(self, event):
        """Handle user input events for the shop state."""
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

                for i, buy_button in enumerate(self.buy_buttons):
                    if buy_button.rect.collidepoint(mouse_pos) and not buy_button.item_sold:
                        can_buy_item = False
                        for item in self.item_selection:
                            if item.inventory_spot == i + 1 and Config.gold_count >= item.buy_value:
                                play_sound_effect('money')
                                buy_button.item_sold = True
                                Config.gold_count -= item.buy_value
                                ItemManager.item_to_backpack(item)
                                self.shop_icon_sprites.remove(item)
                                self.item_selection.remove(item)
                                can_buy_item = True
                                break
                        if not can_buy_item:
                            play_sound_effect('error')
                            break

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
                                    play_sound_effect('money')

        elif event.type == pg.MOUSEMOTION and Config.current_adventure:
            icon_lists = itertools.chain(self.backpack_items, self.item_selection)
            for hover_item in icon_lists:
                if hover_item.rect.collidepoint(mouse_pos):
                    self.hovered_item = hover_item
                    break
                else:
                    self.hovered_item = None

    def update(self, screen, dt):
        """Update the shop state based on user input and game events."""
        self.draw(screen)

    def draw(self, screen):
        """Draw the shop state to the screen."""
        self.screen.blit(self.ground, (0,0))
        self.selection_button_sprites.draw(self.screen)
        
        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        if Config.current_adventure:
            mouse_pos = pg.mouse.get_pos()
            self.screen.blit(self.shopkeeper_image, self.shopkeeper_rect)
            shop_text = self.dialogue_font.render(self.shop_dialogue_2, True, self.black)
            shop_text_rect = shop_text.get_rect(center=self.coords_dialogue_2)
            self.screen.blit(shop_text, shop_text_rect)

            for backpack_slot in Config.backpack_slots:
                backpack_slot.draw_border()
            self.shop_icon_sprites.draw(self.screen)
            self.shopping_sprites.draw(self.screen)

            if self.selling_item:
                self.screen.blit(self.sell_cursor_image, mouse_pos)
                
            if self.hovered_item:
                Inventory.display_item_info(self.screen, self.screen_height, self.hovered_item, self.item_info_font, self.black, self.white)

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
                    OFFSET = self.screen_height / self.offset_divisor
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