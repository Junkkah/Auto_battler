import pygame as pg
import sys
from config_ab import Config
from sounds_ab import play_sound_effect, set_sfx_volume, set_music_volume, get_sfx_volume, get_music_volume
from sprites_ab import Button
from data_ab import get_json_data
from animations_ab import set_animation_speed, get_animation_speed

class MainMenu(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'shop' 

    def cleanup(self):
        self.menu_buttons = []
        self.menu_button_sprites.empty()

    def startup(self):
        menu_bg = pg.image.load('./ab_images/background/menu_bg_og.png').convert()
        self.menu_bg = pg.transform.scale(menu_bg, (self.screen_width, self.screen_height))
        MENU_FONT = self.default_font

        COORDS_TITLE = (self.screen_width * 0.50, self.screen_height * 0.16)
        TITLE = 'Auto Battler'
        title_font = pg.font.SysFont(MENU_FONT, self.title_font_size)
        self.title_text = title_font.render(TITLE, True, self.black)
        self.title_rect = self.title_text.get_rect(center=COORDS_TITLE)

        menu_button_data = volume_button_data = get_json_data('menu_buttons')
        button_texts = ['New Game', 'Settings', 'Simulator', 'Quit']
        self.menu_buttons = []
        for i, (button_name, (x, y)) in enumerate(menu_button_data.items()):
            button_text = button_texts[i]
            button = Button(
                self.menu_button_sprites,
                button_text,
                MENU_FONT,
                self.big_font_size,
                self.black,
                (self.screen_width * x, self.screen_height * y)
            )
            setattr(self, button_name, button)
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
                self.next = 'initialize'
                self.done = True

            elif self.settings_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'settings'
                self.done = True

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

class SettingsMenu(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'menu' 
        self.maximum_volume = 1.0
        self.minimum_volume =  0.0
        self.minimum_animation_speed = 0.1
        self.maximum_animation_speed = 1.0

    def cleanup(self):
        self.settings_button_sprites.empty()
        self.settings_buttons = []
    
    def startup(self):
        MENU_FONT = self.default_font
        PLUS_TEXT = '+'
        MINUS_TEXT = '-'
        settings_button_data = get_json_data('settings_buttons')

        self.settings_buttons = []
        for button_name, (x, y) in settings_button_data.items():
            button_text = PLUS_TEXT if len(self.settings_buttons) % 2 == 0 else MINUS_TEXT
            button = Button(
                self.settings_button_sprites,
                button_text,
                MENU_FONT,
                self.big_font_size,
                self.black,
                (self.screen_width * x, self.screen_height * y)
            )
            setattr(self, button_name, button)
            self.settings_buttons.append(button)
        self.continue_button = Button(self.settings_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)
        self.settings_buttons.append(self.continue_button)

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()

        if event.type == pg.MOUSEMOTION:
            for settings_button in self.settings_buttons:
                if settings_button.rect.collidepoint(mouse_pos):
                    settings_button.border_color = (self.white)
                    settings_button.draw_border()
                else:
                    settings_button.border_color = (self.black)
                    settings_button.draw_border()
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.done = True

            elif self.sfx_plus_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                vol = get_sfx_volume()
                if vol < self.maximum_volume:
                    vol += 0.1
                    vol = min(1.0, round(vol, 1))
                    set_sfx_volume(vol)

            elif self.sfx_minus_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                vol = get_sfx_volume()
                if vol > self.minimum_volume:
                    vol -= 0.1
                    vol = max(0.0, round(vol, 1))
                    set_sfx_volume(vol)

            elif self.music_plus_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                vol = get_music_volume()
                if vol < self.maximum_volume:
                    vol += 0.1
                    vol = min(1.0, round(vol, 1))
                    set_music_volume(vol)
            
            elif self.music_minus_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                vol = get_music_volume()
                if vol > self.minimum_volume:
                    vol -= 0.1
                    vol = max(0.0, round(vol, 1))
                    set_music_volume(vol)
            
            elif self.speed_plus_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                spd = get_animation_speed()
                if spd < self.maximum_animation_speed:
                    spd += 0.1
                    spd = min(1.0, round(spd, 1))
                    set_animation_speed(spd)

            elif self.speed_minus_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                spd = get_animation_speed()
                if spd > self.minimum_animation_speed:
                    spd -= 0.1
                    spd = max(0.0, round(spd, 1))
                    set_animation_speed(spd)

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        self.screen.fill(self.grey)
        self.settings_button_sprites.draw(self.screen)

        SETTINGS = [
            ('Sound effect volume', self.screen_height * 0.22, lambda: f'{get_sfx_volume():.1f}'),
            ('Music volume', self.screen_height * 0.47, lambda: f'{get_music_volume():.1f}'),
            ('Animation speed', self.screen_height * 0.72, lambda: f'{get_animation_speed():.1f}')
            ]
        TEXT_X = self.screen_width * 0.30
        VALUE_X = self.screen_width * 0.65
        TEXT_COLOR = self.black
        VALUE_COLOR = self.green
        TEXT_FONT_NAME = 'Arial'
        VALUE_FONT_NAME = 'Verdana'
        FONT_SIZE = 30

        text_font = pg.font.SysFont(TEXT_FONT_NAME, FONT_SIZE)
        value_font = pg.font.SysFont(VALUE_FONT_NAME, FONT_SIZE)

        for setting in SETTINGS:
            text, y, get_value = setting
            text_surface = text_font.render(text, True, TEXT_COLOR)
            value_surface = value_font.render(get_value(), True, VALUE_COLOR)
            self.screen.blit(text_surface, (TEXT_X, y))
            self.screen.blit(value_surface, (VALUE_X, y))