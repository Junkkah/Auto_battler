"""
LevelUp module for managing hero level-ups and talent selection.

Contains:
    - LevelUp: Handles the display and selection of new talents when heroes gain a level.
"""

import pygame as pg
import sys
import random
import pandas as pd
from config_ab import Config
from data_ab import get_data, get_talent_data
from sprites_ab import Button, TalentCard
from battle_ab import BattleManager
from sounds_ab import play_sound_effect
from talents_ab import TalentsManager

class LevelUp(Config): 
    """
    Manages hero level-ups and talent selection.

    This class displays a selection of two viable talents for each hero to choose from 
    when they gain a level.
    """
    
    def __init__(self):
        """Initialize levelup with default settings and set next state to 'path'."""
        super().__init__()
        self.next = 'path'
        self.levelup_hero_sprites = pg.sprite.Group()
        self.levelup_sprites = pg.sprite.Group()
        self.exp_df = get_data('experience')

    def cleanup(self):
        """Reset class-specific variables and clear associated sprites."""
        for selected_talent in self.talents_selected:
            hero_to_add = selected_talent.hero
            talent_name = selected_talent.name
            talent_type = selected_talent.type
            TalentsManager.add_talent(talent_name, talent_type, hero_to_add)
        
        for cleanup_hero in Config.party_heroes:
            if cleanup_hero.reroll_count > 1:
                cleanup_hero.reroll_count -= 1

        self.talent_buttons = []
        self.talents_selected = []
        self.reroll_rect_list = []
        self.reroll_texts= {}
        self.levelup_hero_sprites.empty()
        self.levelup_sprites.empty()
        self.talent_cards = {}
        Config.map_next = False

  
    
    def gain_level(self, hero):
        """Increase the hero's level and update their attributes."""
        hero.level += 1
        hero.next_level = self.exp_df.loc[self.exp_df['level'] == hero.level, 'exp'].iloc[0]
        hero.gain_max_health(hero.level_health)
        hero.gain_health(hero.level_health)  
    
    def create_reroll_images(self):
        """Create images for rerolling talents for each hero."""
        reroll_path = './ab_images/reroll.png'
        reroll_size_scalar = 10
        reroll_image_offset = 35
        reroll_y = self.screen_height * 0.45

        self.reroll_image = self.load_and_scale_image(reroll_path, reroll_size_scalar) 
        self.reroll_rect_list = [
            self.reroll_image.get_rect(topleft=(hero.pos_x + reroll_image_offset, reroll_y))
            for hero in Config.party_heroes
            ]
    
    def create_reroll_texts(self, idx, text_hero):
        """Create text for cost of talent reroll for each hero."""
        reroll_text_height = self.screen_height * 0.50

        info_coords = (text_hero.pos_x, reroll_text_height)
        info_text = f"Reroll {text_hero.name}'s Talents"
        reroll_info_text = self.create_text_and_rect(self.info_font, info_text, self.black, info_coords)
        cost_coords = (text_hero.pos_x, reroll_text_height + reroll_info_text[1].height)
            
        cost_of_reroll = text_hero.reroll_count * text_hero.reroll_cost
        cost_text = f'Cost {cost_of_reroll} Gold coins'
            
        reroll_cost_text = self.create_text_and_rect(self.info_font, cost_text, self.black, cost_coords)
        self.reroll_texts[idx] = {'info': reroll_info_text, 'cost': reroll_cost_text}

    def create_talent_sample(self, hero) -> pd.DataFrame:
        """Create a sample DataFrame of two available talents for a hero."""
        talent_df = get_talent_data(hero.type)
        # Filter out talents the hero already has
        talent_df = talent_df[~talent_df['name'].isin(hero.talents)]
        # Filter out too high level talents
        talent_df = talent_df[talent_df['min_level'] <= hero.level]
        # Filter out talents if their requirements are not met
        talent_df = talent_df[talent_df['req1'].isin(hero.talents) | talent_df['req1'].isnull()]
        talent_df = talent_df[talent_df['req2'].isin(hero.talents) | talent_df['req2'].isnull()]

        # Hero is spellcaster
        if hero.spells:
            hero_spell_types = [spell['type'] for spell in hero.spells]
            mastery_mask = talent_df['type'] == 'spell_mastery'
            # Spell_mastery talent 'effect' is the spell type of the mastery
            effect_mask = talent_df['effect'].isin(hero_spell_types)
            # Filter to include only 'spell_mastery' talents for spell types that the hero possesses
            combined_mask = mastery_mask & ~effect_mask
            talent_df = talent_df[~combined_mask]

        # Hero already has aura talent
        if hero.aura:
            aura_mask = talent_df['type'] == 'aura'
            upgrade_mask = talent_df['req1'].isnull()
            # Filter out other non-upgrade auras
            combined_mask = aura_mask & upgrade_mask
            talent_df = talent_df[~combined_mask]

        # Due to limited number of talenrs for each class,
        # choosing talents in specific order can result in one row talent_df
        if len(talent_df) < 2:
            print('Talent Error: ', hero.type, hero.level)
            exit()

        random_rows = talent_df.sample(n=2)
        new_df = pd.DataFrame(random_rows)
        return new_df

    def create_talent_cards(self, hero, idx):
        """Create two talent card objects for a hero."""
        pos_y = (self.screen_height * 0.15)
        gap = (self.screen_height * 0.15)
        font_name = self.default_font
        font_size = self.default_font_size
        font = pg.font.SysFont(font_name, font_size)

        sample = self.create_talent_sample(hero)
        df1 = sample.iloc[[0]].reset_index(drop=True)
        df2 = sample.iloc[[1]].reset_index(drop=True)

        pos_x = hero.pos_x
        card1 = TalentCard(self.levelup_sprites, df1, pos_x, pos_y, hero, font)
        pos_y_2 = pos_y + card1.height + gap
        card2 = TalentCard(self.levelup_sprites, df2, pos_x, pos_y_2, hero, font)
        self.talent_cards[idx] = (card1, card2)

    def startup(self):
        """Initialize resources and set up the levelup state."""
        self.talent_buttons = []
        self.talents_selected = []
        self.talent_cards = {}
        self.reroll_texts = {}
        
        self.continue_button = Button(self.levelup_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)

        battle_instance = BattleManager()
        battle_instance.position_heroes()

        for idx, leveling_hero in enumerate(Config.party_heroes):
            self.levelup_hero_sprites.add(leveling_hero)
            self.gain_level(leveling_hero)
            self.create_talent_cards(leveling_hero, idx)
            self.create_reroll_texts(idx, leveling_hero)

        self.numer_of_heroes = len(Config.party_heroes)
        
        self.reroll_info_texts = []
        self.reroll_cost_texts = []
        self.create_reroll_images()

    def get_event(self, event): 
        """Handle user input events for the levelup state."""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = pg.mouse.get_pos()
            if self.continue_button.rect.collidepoint(mouse_pos) and len(self.talents_selected) == self.numer_of_heroes:
                play_sound_effect('click')
                if Config.map_next:
                    self.next = 'map'
                else:
                    self.next = 'path'
                    #Config.map_next = False
                self.done = True
            elif self.continue_button.rect.collidepoint(mouse_pos):
                play_sound_effect('error')
            
            for i, reroll_rect in enumerate(self.reroll_rect_list):
                if reroll_rect.collidepoint(mouse_pos):
                    reroll_hero = Config.party_heroes[i]
                    cost_of_reroll = reroll_hero.reroll_count * (reroll_hero.reroll_cost + reroll_hero.level)
                    if Config.gold_count >= cost_of_reroll:
                        Config.gold_count -= cost_of_reroll
                        reroll_hero.reroll_count += 1
                        
                        self.create_reroll_texts(i, reroll_hero)
                        old_card1, old_card2 = self.talent_cards[i]
                        old_card1.kill()  
                        old_card2.kill()
                        
                        self.create_talent_cards(reroll_hero, i)
                        play_sound_effect('click')
                    else:
                        play_sound_effect('error')
                    break

            for key, talent_card in self.talent_cards.items():
                if talent_card[0].rect.collidepoint(mouse_pos):
                    play_sound_effect('click')
                    talent_card[0].selected = not talent_card[0].selected
                    talent_card[1].selected = False

                elif talent_card[1].rect.collidepoint(mouse_pos):
                    play_sound_effect('click')
                    talent_card[1].selected = not talent_card[1].selected
                    talent_card[0].selected = False

            self.talents_selected = []
            for key, talent_card in self.talent_cards.items():
                if talent_card[0].selected:
                    self.talents_selected.append(talent_card[0])

                if talent_card[1].selected:
                    self.talents_selected.append(talent_card[1])

    def update(self, screen, dt):
        """Update the levelup state based on user input and game events."""
        self.draw(screen)

    def draw(self, screen):
        """Draw the levelup state to the screen."""
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.levelup_hero_sprites.draw(self.screen)
        self.levelup_sprites.draw(self.screen)

        for texts in self.reroll_texts.values():
            self.screen.blit(*texts['info'])
            self.screen.blit(*texts['cost'])

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        for reroll_rect in self.reroll_rect_list:
            self.screen.blit(self.reroll_image, reroll_rect)

        if len(self.talents_selected) == self.numer_of_heroes:
            self.continue_button.border_color = self.black 
            self.continue_button.draw_border()
        else:
            self.continue_button.border_color = self.grey
            self.continue_button.draw_border()
        
        for key, drawn_card in self.talent_cards.items():
            for card in drawn_card:  
                if card.selected:
                    card.border_color = self.red
                else:
                    card.border_color = self.black
                card.draw_border()

        new_level = Config.party_heroes[0].level
        INFO = f'Your heroes leveled up to {new_level}. Choose new talents'
        INFO_TEXT = self.med_info_font.render(INFO, True, self.black)
        COORDS_INFO = (self.screen_width * 0.35, self.screen_height * 0.09)
        INFO_RECT = INFO_TEXT.get_rect(topleft = COORDS_INFO)
        self.screen.blit(INFO_TEXT, INFO_RECT)