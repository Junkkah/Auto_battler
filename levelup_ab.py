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

        self.talent_buttons = []
        self.talents_selected = []
        self.levelup_hero_sprites.empty()
        self.levelup_sprites.empty()
        Config.map_next = False
    
    def gain_level(self, hero):
        """Increase the hero's level and update their attributes."""
        hero.level += 1
        hero.next_level = self.exp_df.loc[self.exp_df['level'] == hero.level, 'exp'].iloc[0]
        hero.gain_max_health(hero.level_health)
        hero.gain_health(hero.level_health)  
    
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

        # Error handling
        # Choosing talents in specific order can result in one row talent_df
        if len(talent_df) < 2:
            print('Talent Error: ', hero.type, hero.level)
            exit()

        random_rows = talent_df.sample(n=2)
        new_df = pd.DataFrame(random_rows)
        return new_df
    
    def startup(self):
        """Initialize resources and set up the levelup state."""
        self.talent_buttons = []
        self.talents_selected = []
        self.talent_cards = []

        self.continue_button = Button(self.levelup_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)

        #position heroes 
        battle_instance = BattleManager()
        battle_instance.position_heroes()
        for leveling_hero in Config.party_heroes:
            self.levelup_hero_sprites.add(leveling_hero)
            #leveling_hero.gain_level()
            self.gain_level(leveling_hero)

        self.numer_of_heroes = len(Config.party_heroes)
        samples = []

        for sample_hero in Config.party_heroes:
            sample = self.create_talent_sample(sample_hero)
            samples.append(sample)
        
        #button for rerolling talent sample

        #def initialize_talent_cards(self):
        TALENTCARD_POS_Y = (self.screen_height * 0.15)
        TALENTCARD_GAP = (self.screen_height * 0.15)
        INFO_FONT_NAME = self.default_font
        INFO_FONT_SIZE = self.default_font_size
        INFO_FONT = pg.font.SysFont(INFO_FONT_NAME, INFO_FONT_SIZE)

        for i in range(self.numer_of_heroes):
            sample = samples[i]
            hero = Config.party_heroes[i] 
            df1 = sample.iloc[[0]].reset_index(drop=True)
            df2 = sample.iloc[[1]].reset_index(drop=True)

            card1 = TalentCard(self.levelup_sprites, df1, hero.pos_x, TALENTCARD_POS_Y, hero, INFO_FONT)
            CARD2_POS_Y = TALENTCARD_POS_Y + card1.height + TALENTCARD_GAP
            card2 = TalentCard(self.levelup_sprites, df2, hero.pos_x, CARD2_POS_Y, hero, INFO_FONT)
            cards = (card1, card2)
            self.talent_cards.append(cards)

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
            
            #elif reroll1_button:
                #if party_gold >= reroll_cost:
                    #self.reroll_sample(hero)
                    #party_gold -= reroll_cost
                    #play_sound_effect('click')
                #else:
                    #play_sound_effect('error)

            for talent_card in self.talent_cards:
                if talent_card[0].rect.collidepoint(mouse_pos):
                    play_sound_effect('click')
                    talent_card[0].selected = not talent_card[0].selected
                    talent_card[1].selected = False

                elif talent_card[1].rect.collidepoint(mouse_pos):
                    play_sound_effect('click')
                    talent_card[1].selected = not talent_card[1].selected
                    talent_card[0].selected = False

            self.talents_selected = []
            for talent_card in self.talent_cards:
                if talent_card[0].selected:
                    self.talents_selected.append(talent_card[0])

                if talent_card[1].selected:
                    self.talents_selected.append(talent_card[1])

    def update(self, screen, dt):
        """Update the lvelup state based on user input and game events."""
        self.draw(screen)

    def draw(self, screen):
        """Draw the levelup state to the screen."""
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.levelup_hero_sprites.draw(self.screen)
        self.levelup_sprites.draw(self.screen)

        if len(self.talents_selected) == self.numer_of_heroes:
            self.continue_button.border_color = self.black 
            self.continue_button.draw_border()
        else:
            self.continue_button.border_color = self.grey
            self.continue_button.draw_border()
        
        for drawn_card in self.talent_cards:
            for i in range(len(drawn_card)):
                if drawn_card[i].selected == True:
                    drawn_card[i].border_color = (self.red)
                    drawn_card[i].draw_border()
                else:
                    drawn_card[i].border_color = (self.black)
                    drawn_card[i].draw_border()
        
        new_level = Config.party_heroes[0].level
        INFO = f'Your heroes leveled up to {new_level}. Choose new talents'
        INFO_TEXT = self.med_info_font.render(INFO, True, self.black)
        COORDS_INFO = (self.screen_width * 0.35, self.screen_height * 0.09)
        INFO_RECT = INFO_TEXT.get_rect(topleft = COORDS_INFO)
        self.screen.blit(INFO_TEXT, INFO_RECT)