import pygame as pg
import sys
import random
from states import States
from stats import Data,Stats
from objects import TalentInfo, TalentName

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
                self.stats.add_talent(States.party_heroes[s_talent.hero], s_talent.a_name, s_talent.a_type)
            elif s_talent.b_selected == True:
                self.stats.add_talent(States.party_heroes[s_talent.hero], s_talent.b_name, s_talent.b_type)

        self.name_text = []
        self.talent_lists = []
        self.talent_text = []
        self.talents_selected = []
        
    def startup(self):
        for inv_hero in States.party_heroes:
            self.inventory_hero_sprites.add(inv_hero)
            self.stats.levelup(inv_hero)

        self.talent_lists = [Data.talent_data(thero.type) for thero in States.party_heroes]

            #if thero.type == "cleric": which sample
                #sample = domain1 and domain2
            #filter lists if hero does not meet requirements
            #fireball requires wizard to learn burn and fire gush first
            
            #for i in range(0,3):
                #for talent in self.talent_lists[i]:
                    #if talent in States.party_heroes[0].talents:
                        #continue #skip for req
                    #for req in talent["reqs"]:
                        #if req not in States.party_heroes[0].talents:
                            #self.talent_lists[0].remove(talent)
        #breaks if less than 3 heroes
        #1 fixed to pos 1 hero, check pos of surviving heroes
        sample_1 = random.sample(self.talent_lists[0].items(), 2)
        sample_2 = random.sample(self.talent_lists[1].items(), 2)
        sample_3 = random.sample(self.talent_lists[2].items(), 2)

        continue_font = pg.font.SysFont("Arial", 50)
        self.continue_text = continue_font.render("CONTINUE", True, (127, 127, 127))
        self.ready_text = continue_font.render("CONTINUE", True, (0, 0, 0))
        self.continue_rect = self.continue_text.get_rect(center=(self.width * 0.75, self.height * 0.88))

        self.name_1 = TalentName(sample_1, (self.width * 0.3), (self.height * 0.15), (self.height * 0.30), self.info_font, 0)
        self.info_1 = TalentInfo(sample_1, (self.width * 0.3), (self.height * 0.20), (self.height * 0.35), self.info_font)
        self.name_2 = TalentName(sample_2, (self.width * 0.5), (self.height * 0.15), (self.height * 0.30), self.info_font, 1)
        self.info_2 = TalentInfo(sample_2, (self.width * 0.5), (self.height * 0.20), (self.height * 0.35), self.info_font)
        self.name_3 = TalentName(sample_3, (self.width * 0.7), (self.height * 0.15), (self.height * 0.30), self.info_font, 2)
        self.info_3 = TalentInfo(sample_3, (self.width * 0.7), (self.height * 0.20), (self.height * 0.35), self.info_font)
        self.talent_text.append(self.name_1)
        self.name_text.append(self.name_1)
        self.talent_text.append(self.info_1)
        self.talent_text.append(self.name_2)
        self.name_text.append(self.name_2)
        self.talent_text.append(self.info_2)
        self.talent_text.append(self.name_3)
        self.name_text.append(self.name_3)
        self.talent_text.append(self.info_3)
    
    def get_event(self, event): 

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_rect.collidepoint(pg.mouse.get_pos()) and len(self.talents_selected) == len(States.party_heroes):
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

        if len(self.talents_selected) == len(States.party_heroes):
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
        
       