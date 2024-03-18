import pygame as pg
import sys
from config_ab import Config
from sounds_ab import play_sound_effect
from sprites_ab import Button

class Menu(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'shop' 

    def cleanup(self):
        self.menu_buttons = []
        self.menu_button_sprites.empty()

    def startup(self):
        menu_bg = pg.image.load('./ab_images/background/menu_bg_og.png').convert()
        self.menu_bg = pg.transform.scale(menu_bg, (self.screen_width, self.screen_height))
        self.menu_buttons = []
        MENU_BUTTON_XPOS = self.screen_width * 0.50
        MENU_BUTTON_YPOS = self.screen_height * 0.16
        MENU_FONT = self.default_font

        COORDS_TITLE = (MENU_BUTTON_XPOS, MENU_BUTTON_YPOS)
        COORDS_PLAY = (MENU_BUTTON_XPOS, MENU_BUTTON_YPOS * 2)
        COORDS_SETTINGS = (MENU_BUTTON_XPOS, MENU_BUTTON_YPOS * 3)
        COORDS_SIMULATOR = (MENU_BUTTON_XPOS, MENU_BUTTON_YPOS * 4)
        COORDS_QUIT = (MENU_BUTTON_XPOS, MENU_BUTTON_YPOS * 5)

        TITLE = 'Auto Battler' 
        PLAY_TEXT = 'New Game'
        SETTINGS_TEXT = 'Settings'
        SIMULATOR_TEXT = 'Simulator'
        QUIT_TEXT = 'Quit'

        title_font = pg.font.SysFont(MENU_FONT, self.title_font_size)
        self.title_text = title_font.render(TITLE, True, self.black)
        self.title_rect = self.title_text.get_rect(center=COORDS_TITLE)

        self.play_button = Button(self.menu_button_sprites, PLAY_TEXT, MENU_FONT, self.big_font_size, self.black, COORDS_PLAY)
        self.settings_button = Button(self.menu_button_sprites, SETTINGS_TEXT, MENU_FONT, self.big_font_size, self.black, COORDS_SETTINGS)
        self.simulator_button = Button(self.menu_button_sprites, SIMULATOR_TEXT, MENU_FONT, self.big_font_size, self.black, COORDS_SIMULATOR)
        self.quit_button = Button(self.menu_button_sprites, QUIT_TEXT, MENU_FONT, self.big_font_size, self.black, COORDS_QUIT)

        for button in [self.play_button, self.settings_button, self.simulator_button, self.quit_button]:
            self.menu_buttons.append(button)

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        if event.type == pg.MOUSEMOTION:
            for menu_button in self.menu_buttons:
                if menu_button.rect.collidepoint(mouse_pos):
                    menu_button.border_color = (self.white)
                    menu_button.draw_border()
                else:
                    menu_button.border_color = (self.black)
                    menu_button.draw_border()
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.play_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'shop'
                self.done = True

            elif self.settings_button.rect.collidepoint(mouse_pos):
                play_sound_effect('error')
                #self.next = 'settings'
                #self.done = True

            elif self.simulator_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'simulator'
                self.done = True

            elif self.quit_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                exit()    

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        self.screen.blit(self.menu_bg, (0,0))
        self.screen.blit(self.title_text, self.title_rect)
        self.menu_button_sprites.draw(self.screen)