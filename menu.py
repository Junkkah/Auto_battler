import pygame as pg
import sys
from states import States

class Menu(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'game' 
    def cleanup(self):
        pass
        #musa = pg.mixer.music.load('auto_battle/synth.wav')
        #pg.mixer.music.play()
    def startup(self):
        pass
    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.fill((0,0,255))
        menu_font = pg.font.SysFont("Arial", 50)
        title_font = pg.font.SysFont("Arial", 75)
        
        self.title_text = title_font.render("Ukko Advantures", True, (0, 0, 0))
        self.title_rect = self.title_text.get_rect(center=(self.width / 2, self.height / 6)) 

        self.play_text = menu_font.render("Play", True, (0, 0, 0))
        self.play_rect = self.play_text.get_rect(center=(self.width / 2, self.height / 3)) 

        self.settings_text = menu_font.render("Settings", True, (0, 0, 0))
        self.info_rect = self.settings_text.get_rect(center=(self.width / 2, self.height / 2))

        self.quit_text = menu_font.render("Quit", True, (0, 0, 0))
        self.quit_rect = self.quit_text.get_rect(center=(self.width / 2, self.height / 1.5))
                
        self.screen.blit(self.play_text, self.play_rect)
        self.screen.blit(self.title_text, self.title_rect)
        self.screen.blit(self.settings_text, self.info_rect)
        self.screen.blit(self.quit_text, self.quit_rect)
    
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            pass
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.quit_rect.collidepoint(pg.mouse.get_pos()):
                exit()
            elif self.play_rect.collidepoint(pg.mouse.get_pos()):
                self.done = True
            else:
                pass    