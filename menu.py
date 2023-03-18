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
        self.menu_mouse = pg.mouse.get_pos()
        menu_font = pg.font.SysFont("Arial", 50)
        title_font = pg.font.SysFont("Arial", 75)
        
        title_text = title_font.render("Ukko Advantures", True, (0, 0, 0))
        self.title_rect = title_text.get_rect(center=(self.width / 2, self.height / 6)) 

        play_text = menu_font.render("Play", True, (0, 0, 0))
        self.play_rect = play_text.get_rect(center=(self.width / 2, self.height / 3)) 

        info_text = menu_font.render("Info", True, (0, 0, 0))
        self.info_rect = info_text.get_rect(center=(self.width / 2, self.height / 2))

        quit_text = menu_font.render("Quit", True, (0, 0, 0))
        self.quit_rect = quit_text.get_rect(center=(self.width / 2, self.height / 1.5))
                
        self.screen.blit(play_text, self.play_rect)
        self.screen.blit(title_text, self.title_rect)
        self.screen.blit(info_text, self.info_rect)
        self.screen.blit(quit_text, self.quit_rect)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            print('Menu State keydown')
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.quit_rect.collidepoint(self.menu_mouse):
                exit()
            else:
                self.done = True