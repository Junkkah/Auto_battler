import pygame as pg
import sys
from config_ab import Config
from sounds_ab import play_sound_effect
from sprites_ab import Button
from hero_ab import Hero
from data_ab import get_data, get_json_data


class CharacterInfo(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path' 

    def cleanup(self):
        self.info_buttons = []
        self.info_lines = []
        self.talent_lists = []
        self.info_sprites.empty()
        self.info_button_sprites.empty()
        self.display_hero = None
        self.display_index = None
        for cleanup_hero in Config.party_heroes:
            cleanup_hero.item_stats_dict = {item_key: 0 for item_key in cleanup_hero.item_stats_dict}
        Config.aura_bonus = {aura_key: 0 for aura_key in Config.aura_bonus}
    
    def set_display_hero(self, display_hero):
        self.info_sprites.empty()
        display_hero_coords = (self.screen_width * 0.10, self.screen_height * 0.05)
        display_hero.rect = display_hero.image.get_rect(topleft = display_hero_coords)
        self.display_hero = display_hero
        self.info_sprites.add(display_hero)
        self.info_lines = [
        ('Name: ', self.display_hero.name),
        ('Class: ', self.display_hero.type),
        ('Level: ', self.display_hero.level),
        ('', ''),
        ('Attributes:', ''),
        ('Health: ', self.display_hero.max_health),
        ('Damage: ', self.display_hero.total_stat('damage')),
        ('Speed: ', self.display_hero.total_stat('speed')),
        ('Armor: ', self.display_hero.total_stat('armor')),
        ('Menace: ', self.display_hero.total_stat('menace')),
        ('Critical: ', self.display_hero.total_stat('critical') * 0.10),
        ('Evasion: ', self.display_hero.total_stat('evasion') * 0.05),
        ('Magic Power: ', self.display_hero.total_stat('magic_power')),
        ]

    def startup(self):
        self.info_buttons = []
        self.info_sprites = pg.sprite.Group()
        self.info_button_sprites = pg.sprite.Group()
        for activation_hero in Config.party_heroes:
            activation_hero.activate_item_stats()
            activation_hero.activate_aura()

        self.set_display_hero(Config.party_heroes[0])
        self.display_index = 0
        self.attribute_overview = get_json_data('attribute_overview')

        self.talent_lists = []
        talent_df = get_data('talents')
        for talent_hero in Config.party_heroes:
            talent_tuple_list = []
            for talent in talent_hero.talents:
                desc = talent_df[talent_df['name'] == talent]
                desc = talent_df.loc[talent_df['name'] == talent, 'desc'].values
                talent_tuple = (f'{talent}:', desc[0])
                talent_tuple_list.append(talent_tuple)
            self.talent_lists.append(talent_tuple_list)


        arrow = pg.image.load('./ab_images/right_arrow.png').convert_alpha()
        COORDS_ARROW = (self.screen_width * 0.20, self.screen_height * 0.10)
        arrow_size_scalar = 15
        SCALAR_ARROW = ((arrow.get_width() / arrow_size_scalar), (arrow.get_height() / arrow_size_scalar))
        self.arrow_image = pg.transform.smoothscale(arrow, SCALAR_ARROW)
        self.arrow_rect = self.arrow_image.get_rect(topleft=COORDS_ARROW)
        
        self.continue_button = Button(self.info_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)
    
    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
            if event.key == pg.K_f:
                self.next = 'path'
                self.done = True
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.next = 'path'
                self.done = True
            
            if self.arrow_rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.display_index = (self.display_index + 1) % len(Config.party_heroes)
                self.set_display_hero(Config.party_heroes[self.display_index])

    
    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        mouse_pos = pg.mouse.get_pos()
        self.screen.fill(self.grey)
        self.info_sprites.draw(self.screen)
        self.info_button_sprites.draw(self.screen)

        self.screen.blit(self.arrow_image, self.arrow_rect)

        COORDS_INFO = (self.screen_width * 0.10, self.screen_height * 0.24)
        COORDS_TALENTS = (self.screen_width * 0.35, self.screen_height * 0.08)

        for i, info in enumerate(self.info_lines):
            if i < 5:
                info_line = '{}{}'.format(info[0].capitalize().ljust(15), str(info[1]).capitalize())
            else:
                info_line = '{}{}'.format(info[0].capitalize().ljust(15), str(info[1]))

            info_line_text = self.stats_font.render(info_line, True, self.black)
            info_line_rect = info_line_text.get_rect(topleft=(COORDS_INFO[0], COORDS_INFO[1] + i * self.medium_font_size))
            self.screen.blit(info_line_text, info_line_rect)
        
        COORDS_TITLE = (self.screen_width * 0.35, self. screen_height * 0.08 - self.medium_font_size)
        talents_title = 'Talents:'
        talents_title_text = self.stats_font.render(talents_title, True, self.black)
        talents_title_rect = talents_title_text.get_rect(topleft=(COORDS_TITLE[0], COORDS_TITLE[1]))
        self.screen.blit(talents_title_text, talents_title_rect)

        for i, talent in enumerate(self.talent_lists[self.display_index]):
            talent_line = '{} {}'.format(talent[0].capitalize().ljust(22), talent[1])
            talent_line_text = self.stats_font.render(talent_line, True, self.black)
            talent_line_rect = talent_line_text.get_rect(topleft=(COORDS_TALENTS[0], COORDS_TALENTS[1] + i * self.medium_font_size))
            self.screen.blit(talent_line_text, talent_line_rect)

        COORDS_OVER = (self.screen_width * 0.10, self.screen_height * 0.70)
        over_title = 'Hero Attributes Overview:'
        over_title_text = self.stats_font.render(over_title, True, self.black)
        over_title_rect = over_title_text.get_rect(topleft=(COORDS_OVER[0], COORDS_OVER[1] - self.medium_font_size))
        self.screen.blit(over_title_text, over_title_rect)

        for i, (key, value) in enumerate(self.attribute_overview.items()):
            overview_line = '{} {}'.format(key.capitalize().ljust(12), value[0])
            overview_line_text = self.stats_font.render(overview_line, True, self.black)
            overview_line_rect = overview_line_text.get_rect(topleft=(COORDS_OVER[0], COORDS_OVER[1] + i * self.medium_font_size))
            self.screen.blit(overview_line_text, overview_line_rect)