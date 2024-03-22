import pygame as pg
import sys
from config_ab import Config
from sounds_ab import play_sound_effect, set_sfx_volume, set_music_volume, get_sfx_volume, get_music_volume
from sprites_ab import Button
from data_ab import get_json_data

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

    def cleanup(self):
        self.volume_button_sprites.empty()
        self.volume_buttons = []
    
    def startup(self):
        MENU_FONT = self.default_font
        PLUS_TEXT = "+"
        MINUS_TEXT = "-"
        volume_button_data = get_json_data('volume_buttons')

        self.volume_buttons = []
        for button_name, (x, y) in volume_button_data.items():
            button_text = PLUS_TEXT if len(self.volume_buttons) % 2 == 0 else MINUS_TEXT
            button = Button(
                self.volume_button_sprites,
                button_text,
                MENU_FONT,
                self.big_font_size,
                self.black,
                (self.screen_width * x, self.screen_height * y)
            )
            setattr(self, button_name, button)
            self.volume_buttons.append(button)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
                
        if event.type == pg.MOUSEMOTION:
            for sounds_button in self.volume_buttons:
                if sounds_button.rect.collidepoint(pg.mouse.get_pos()):
                    sounds_button.border_color = (self.white)
                    sounds_button.draw_border()
                else:
                    sounds_button.border_color = (self.black)
                    sounds_button.draw_border()
        
        # Button press increases sound effect volume
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.sfx_plus_button.rect.collidepoint(pg.mouse.get_pos()):
                play_sound_effect('click')
                vol = get_sfx_volume()
                if vol < self.maximum_volume:
                    vol += 0.1
                    vol = min(1.0, round(vol, 1))
                    set_sfx_volume(vol)

            # Button press decreases sound effect volume
            elif self.sfx_minus_button.rect.collidepoint(pg.mouse.get_pos()):
                play_sound_effect('click')
                vol = get_sfx_volume()
                if vol > self.minimum_volume:
                    vol -= 0.1
                    vol = max(0.0, round(vol, 1))
                    set_sfx_volume(vol)

            elif self.music_plus_button.rect.collidepoint(pg.mouse.get_pos()):
                play_sound_effect('click')
                vol = get_music_volume()
                if vol < self.maximum_volume:
                    vol += 0.1
                    vol = min(1.0, round(vol, 1))
                    set_music_volume(vol)
            
            elif self.music_minus_button.rect.collidepoint(pg.mouse.get_pos()):
                play_sound_effect('click')
                vol = get_music_volume()
                if vol > self.minimum_volume:
                    vol -= 0.1
                    vol = max(0.0, round(vol, 1))
                    set_music_volume(vol)

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        self.screen.fill(self.grey)
        self.volume_button_sprites.draw(self.screen)

        SFX_TEXT = "Sound effect volume"
        MUSIC_TEXT = "Music volume"
        SFX_TEXT_X = self.screen_width * 0.30
        SFX_TEXT_Y = self.screen_height * 0.33
        MUSIC_TEXT_X = self.screen_width * 0.30
        MUSIC_TEXT_Y = self.screen_height * 0.63
        COORDS_SFX_TEXT = (SFX_TEXT_X, SFX_TEXT_Y)
        COORDS_MUSIC_TEXT = (MUSIC_TEXT_X, MUSIC_TEXT_Y)

        font = pg.font.SysFont('Arial', 30)
        sfx_text_surface = font.render(SFX_TEXT, True, self.black) 
        music_text_surface = font.render(MUSIC_TEXT, True, self.black) 
        self.screen.blit(sfx_text_surface, COORDS_SFX_TEXT)
        self.screen.blit(music_text_surface, COORDS_MUSIC_TEXT)

        VOLUMES_VALUE_X = self.screen_width * 0.65
        sfx_volume_text = f"{get_sfx_volume():.1f}" 
        music_volume_text = f"{get_music_volume():.1f}" 
        VOLUME_FONT_SIZE = 30

        font = pg.font.SysFont('Verdana', VOLUME_FONT_SIZE)
        sfx_volume_text_surface = font.render(sfx_volume_text, True, self.green) 
        music_volume_text_surface = font.render(music_volume_text, True, self.green) 
        self.screen.blit(sfx_volume_text_surface, (VOLUMES_VALUE_X, SFX_TEXT_Y))
        self.screen.blit(music_volume_text_surface, (VOLUMES_VALUE_X, MUSIC_TEXT_Y))