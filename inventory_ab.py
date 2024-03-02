import pygame as pg
import sys
from config_ab import Config
from sounds_ab import sound_effect
from sprites_ab import Button, MagicItem
from hero_ab import Hero
from battle_ab import BattleManager

class Inventory(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path' 

    def cleanup(self):
        #reorder party_heroes to match spots
        self.inventory_buttons = []
        self.hero_spots = []
        self.inventory_sprites.empty()
        self.inventory_button_sprites.empty()
        self.dragging = False
        self.dragged_hero = None
        self.original_spot = None
        self.spot_found = False

    def startup(self):
        self.inventory_buttons = []
        self.inventory_sprites = pg.sprite.Group()
        self.inventory_button_sprites = pg.sprite.Group()
        self.dragging = False
        self.dragged_hero = None
        self.original_spot = None
        self.spot_found = False

        CONT_TEXT = 'CONTINUE'
        CONT_FONT = self.default_font
        CONT_SIZE = self.big_font_size
        CONT_COL = self.black
        COORDS_CONT = (self.screen_width * 0.75, self.screen_height * 0.90)

        self.continue_button = Button(self.inventory_button_sprites, CONT_TEXT, CONT_FONT, CONT_SIZE, CONT_COL, COORDS_CONT)

        #position heroes 
        battle_instance = BattleManager()
        battle_instance.position_heroes(Config.party_heroes)
        for inv_hero in Config.party_heroes:
            self.inventory_sprites.add(inv_hero)
        
        self.hero_spots = []
        for pos_hero in Config.party_heroes:
            hero_rect = pos_hero.rect
            hero_spot_rect = pg.Rect(hero_rect.x - 5, hero_rect.y - 5, hero_rect.width + 10, hero_rect.height + 10)
            self.hero_spots.append(hero_spot_rect)

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(mouse_pos):
                sound_effect('click')
                self.next = 'path'
                self.done = True
        
            if event.button == self.primary_mouse_button:
                for i in range(len(Config.party_heroes)): 
                    if Config.party_heroes[i].rect.collidepoint(mouse_pos) and not self.dragging:
                        self.dragging = True
                        self.dragged_hero = Config.party_heroes[i]
                        self.original_spot = i
                        self.offset_x = mouse_pos[0] - self.dragged_hero.rect.x
                        self.offset_y = mouse_pos[1] - self.dragged_hero.rect.y
                        

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == self.primary_mouse_button:  
                if self.dragging:
                    for hero_spot in self.hero_spots:
                        if hero_spot.colliderect(self.dragged_hero.rect):
                            self.dragged_hero.rect.x = hero_spot.x
                            self.dragged_hero.rect.y = hero_spot.y
                            self.spot_found = True
                            #bump currect occupant to self.original_spot
                    if not self.spot_found:    
                        self.dragged_hero.rect.x = self.hero_spots[self.original_spot].x
                        self.dragged_hero.rect.y = self.hero_spots[self.original_spot].y
                    self.dragging = False
                    self.spot_found = False
                    

    def update(self, screen, dt):
        if self.dragging:
            mouse_x, mouse_y = pg.mouse.get_pos()
            self.dragged_hero.rect.x = mouse_x - self.offset_x
            self.dragged_hero.rect.y = mouse_y - self.offset_y
        self.draw(screen)

    def draw(self, screen):
        self.screen.fill(self.grey)
        self.inventory_sprites.draw(self.screen)
        self.inventory_button_sprites.draw(self.screen)
        #self.screen.blit(backpack_item_image, backpack_item_rect)

        for spot in self.hero_spots:
            pg.draw.rect(self.screen, self.black, spot, 3)

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        if self.dragging:
            pass
        #draw rects of the drop points
        #highlight correct drop point if collide?