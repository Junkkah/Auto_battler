import pygame as pg
import sys
import random
from states import States
from stats import Data,Stats
from objects import TalentInfo, TalentName
from combat import Combat

class Inv(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'path'
        self.inventory_hero_sprites = pg.sprite.Group()
        self.talents_selected = []
        self.talent_text = []
        self.talent_lists = []
        self.name_text = []
        self.stats = Stats()

    def cleanup(self):
        for s_talent in self.talents_selected:
            if s_talent.a_selected == True:
                self.stats.add_talent(s_talent.hero, s_talent.a_name, s_talent.a_type)
            elif s_talent.b_selected == True:
                self.stats.add_talent(s_talent.hero, s_talent.b_name, s_talent.b_type)

        self.name_text = []
        self.talent_lists = []
        self.talent_text = []
        self.talents_selected = []
        
    def startup(self):

        continue_font = pg.font.SysFont("Arial", self.big_font_size)
        self.continue_text = continue_font.render("CONTINUE", True, self.grey)
        self.ready_text = continue_font.render("CONTINUE", True, self.black)
        COORDS_CONTINUE = (self.width * 0.75, self.height * 0.88)
        self.continue_rect = self.continue_text.get_rect(center=COORDS_CONTINUE)

        combat_instance = Combat()
        combat_instance.position_heroes(States.party_heroes)
        for inv_hero in States.party_heroes:
            self.inventory_hero_sprites.add(inv_hero)
            self.stats.levelup(inv_hero)

        self.talent_lists = [Data.talent_data(thero.type) for thero in States.party_heroes]
        self.numer_of_heroes = len(States.party_heroes)
        samples = [random.sample(t.items(), 2) for t in self.talent_lists]
    
        SAMPLE1_POS_X = (self.width * 0.3)
        SAMPLE2_POS_X = (self.width * 0.5)
        SAMPLE3_POS_X = (self.width * 0.7)
        SAMPLES_POS_X = (self.width * 0.3), (self.width * 0.5), (self.width * 0.7)
        NAME_POS_Y1Y2 = (self.height * 0.15), (self.height * 0.30)
        INFO_POS_Y1Y2 = (self.height * 0.20), (self.height * 0.35)

        for i in range(self.numer_of_heroes):
            sample = samples[i]
            hero = States.party_heroes[i] 
            name_value = TalentName(sample, SAMPLES_POS_X[i], NAME_POS_Y1Y2, self.info_font, hero)
            info_value = TalentInfo(sample, SAMPLES_POS_X[i], INFO_POS_Y1Y2, self.info_font)
            setattr(self, f"name_{i+1}", name_value)
            setattr(self, f"info_{i+1}", info_value)
            self.name_text.append(name_value)
            self.talent_text.append(name_value)
            self.talent_text.append(info_value)
    
    def get_event(self, event): 
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_rect.collidepoint(pg.mouse.get_pos()) and len(self.talents_selected) == self.numer_of_heroes:
                self.done = True

            for name in self.name_text:
                if name.a_rect.collidepoint(pg.mouse.get_pos()):
                    if name.a_selected == True:
                        name.a_selected = False
                    else:
                        if name.b_selected == True:
                            name.b_selected = False
                        name.a_selected = True
                
                elif name.b_rect.collidepoint(pg.mouse.get_pos()):
                    if name.b_selected == True:
                        name.b_selected = False
                    else:
                        if name.a_selected == True:
                            name.a_selected = False
                        name.b_selected = True
            self.talents_selected = []
            for c_name in self.name_text:
                if c_name.a_selected or c_name.b_selected == True:
                    self.talents_selected.append(c_name)

    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.inventory_hero_sprites.draw(self.screen)

        if len(self.talents_selected) == self.numer_of_heroes:
            self.screen.blit(self.ready_text, self.continue_rect)    
        else:
            self.screen.blit(self.continue_text, self.continue_rect)

        for text in self.talent_text:
            self.screen.blit(text.a_text, text.a_rect)
            self.screen.blit(text.b_text, text.b_rect)
        
        for n_text in self.name_text:
            if n_text.a_selected == True:
                pg.draw.rect(self.screen, self.red, n_text.a_rect, 2)
            elif n_text.b_selected == True:
                pg.draw.rect(self.screen, self.red, n_text.b_rect, 2)
        
       