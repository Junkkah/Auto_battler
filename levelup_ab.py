import pygame as pg
import sys
import random
import pandas as pd
from config_ab import Config
from data_ab import get_data, get_talent_data
from sprites_ab import Button, TalentCard
from battle_ab import BattleManager
from sounds_ab import play_sound_effect

class LevelUp(Config): 
    def __init__(self):
        Config.__init__(self)
        self.next = 'path'
        self.levelup_hero_sprites = pg.sprite.Group()
        self.levelup_sprites = pg.sprite.Group()
    
    def create_talent_sample(self, hero) -> pd.DataFrame:
        talent_df = get_talent_data(hero.type)
        #Filter out talents hero already has
        talent_df = talent_df[~talent_df['name'].isin(hero.talents)]
        while True:
            discard_sample = False
            random_rows = talent_df.sample(n=2)
            new_df = pd.DataFrame(random_rows)
            talent1_req1 = new_df['req1'].iloc[0]
            talent2_req1 = new_df['req1'].iloc[1]
            
            if talent1_req1 and talent1_req1 not in hero.talents:
                discard_sample = True
            if talent2_req1 and talent2_req1 not in hero.talents:
                discard_sample = True

            min1 = new_df['min_level'].iloc[0]
            min2 = new_df['min_level'].iloc[1]
            if min1 > hero.level or min2 > hero.level:
                discard_sample = True
            
            # Effect is in spell_types if it is a spell mastery
            # Fail sample if hero does not have spell that matches masterys type
            #hero will still only cast spells[0]
            effect1 = new_df['effect'].iloc[0].split()[0]
            effect2 = new_df['effect'].iloc[1].split()[0]
            for effect in [effect1, effect2]:
                if effect in self.spell_types:
                    hero_spell_types = [spell['type'] for spell in hero.spells]
                    if effect not in hero_spell_types:
                        discard_sample = True

            # Fail sample if it has aura, hero already has aura and sample aura does not have requirement
            # Hero can have only one aura. Only valid aura talents are upgrades for the existing aura
            if ('aura' in new_df['type'].values) and hero.aura:
                if new_df['type'].iloc[0] == 'aura' and talent1_req1 is None:
                    discard_sample = True
                if new_df['type'].iloc[1] == 'aura' and talent2_req1 is None:
                    discard_sample = True
            
            if discard_sample:
                continue
                
            return new_df

    def cleanup(self):
        for selected_talent in self.talents_selected:
            selected_talent.hero.add_talent(selected_talent.name, selected_talent.type)

        self.talent_buttons = []
        self.talents_selected = []
        self.levelup_hero_sprites.empty()
        self.levelup_sprites.empty()
    
    def startup(self):
        self.talent_buttons = []
        self.talents_selected = []
        self.talent_cards = []

        self.continue_button = Button(self.levelup_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)

        #position heroes 
        battle_instance = BattleManager()
        battle_instance.position_heroes(Config.party_heroes)
        for leveling_hero in Config.party_heroes:
            self.levelup_hero_sprites.add(leveling_hero)
            leveling_hero.gain_level()


        self.numer_of_heroes = len(Config.party_heroes)
        samples = []

        for sample_hero in Config.party_heroes:
            sample = self.create_talent_sample(sample_hero)
            samples.append(sample)

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
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()


        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = pg.mouse.get_pos()
            if self.continue_button.rect.collidepoint(mouse_pos) and len(self.talents_selected) == self.numer_of_heroes:
                play_sound_effect('click')
                self.done = True
            elif self.continue_button.rect.collidepoint(mouse_pos):
                play_sound_effect('error')

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
        self.draw(screen)

    def draw(self, screen):
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
        
        INFO = 'Your heroes leveled up. Choose new talents'
        INFO_TEXT = self.med_info_font.render(INFO, True, self.black)
        COORDS_INFO = (self.screen_width * 0.35, self.screen_height * 0.09)
        INFO_RECT = INFO_TEXT.get_rect(topleft = COORDS_INFO)
        self.screen.blit(INFO_TEXT, INFO_RECT)
            
        
       