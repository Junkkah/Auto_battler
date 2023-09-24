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
        self.screen.fill(self.blue)
        
        TITLE_FONT_NAME = "Arial"
        MENU_FONT_NAME = "Arial"
        menu_font = pg.font.SysFont(MENU_FONT_NAME, self.big_font_size)
        title_font = pg.font.SysFont(TITLE_FONT_NAME, self.title_font_size)
        TITLE = "Ukko Advantures"
        PLAY = "Play"
        SETTINGS = "Settings"
        SIMULATOR = "Simulator"
        QUIT = "Quit"
        MIDDLE = self.width * 0.50
        HEIGHT_GAP = self.height * 0.16
        COORDS_TITLE = (MIDDLE, HEIGHT_GAP)
        COORDS_PLAY = (MIDDLE, HEIGHT_GAP * 2)
        COORDS_SETTINGS = (MIDDLE, HEIGHT_GAP * 3)
        COORDS_SIMULATOR = (MIDDLE, HEIGHT_GAP *4)
        COORDS_QUIT = (MIDDLE, HEIGHT_GAP * 5)

        self.title_text = title_font.render(TITLE, True, self.black)
        self.play_text = menu_font.render(PLAY, True, self.black)
        self.settings_text = menu_font.render(SETTINGS, True, self.black)
        self.simulator_text = menu_font.render(SIMULATOR, True, self.black)
        self.quit_text = menu_font.render(QUIT, True, self.black)
        
        self.title_rect = self.title_text.get_rect(center=COORDS_TITLE) 
        self.play_rect = self.play_text.get_rect(center=COORDS_PLAY) 
        self.info_rect = self.settings_text.get_rect(center=COORDS_SETTINGS)
        self.simulator_rect = self.simulator_text.get_rect(center=COORDS_SIMULATOR)
        self.quit_rect = self.quit_text.get_rect(center=COORDS_QUIT)
     
        self.screen.blit(self.play_text, self.play_rect)
        self.screen.blit(self.title_text, self.title_rect)
        self.screen.blit(self.settings_text, self.info_rect)
        self.screen.blit(self.simulator_text, self.simulator_rect)
        self.screen.blit(self.quit_text, self.quit_rect)
    
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            pass
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.quit_rect.collidepoint(pg.mouse.get_pos()):
                exit()
            elif self.simulator_rect.collidepoint(pg.mouse.get_pos()):
                self.next = 'simu'
                self.done = True
            elif self.play_rect.collidepoint(pg.mouse.get_pos()):
                self.next = 'game'
                self.done = True
            else:
                pass    