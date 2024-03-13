import pygame as pg
import sys
from config_ab import Config
from sounds_ab import sound_effect
from sprites_ab import Button, EquipmentSlot
from hero_ab import Hero
from battle_ab import BattleManager

class Inventory(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path' 

    def cleanup(self):
        Config.party_heroes.sort(key=lambda hero: hero.inventory_spot)
        self.inventory_buttons = []
        self.hero_spots = []
        self.eq_slots = []
        self.inventory_sprites.empty()
        self.inventory_button_sprites.empty()
        self.inventory_icon_sprites.empty()
        #self.equipment_slot_sprites.empty()
        self.dragging = False
        self.dragged_hero = None
        self.original_spot = None
        self.spot_found = False

    def startup(self):
        self.inventory_buttons = []
        self.eq_slots = []
        self.inventory_sprites = pg.sprite.Group()
        self.inventory_button_sprites = pg.sprite.Group()
        self.inventory_icon_sprites = pg.sprite.Group()
        #self.equipment_slot_sprites = pg.sprite.Group()
        self.dragging = False
        self.dragged_hero = None
        self.original_spot = None
        self.spot_found = False
        # Hardcoded largest hero image width for creating uniform size hero spots
        self.hero_width_scalar = 7.5
        self.max_hero_width = self.screen_height // self.hero_width_scalar #144 with witdth 1080

        self.continue_button = Button(self.inventory_button_sprites, self.CONT_TEXT, self.CONT_FONT, self.CONT_SIZE, self.CONT_COL, self.COORDS_CONT)

        #position heroes 
        battle_instance = BattleManager()
        battle_instance.position_heroes(Config.party_heroes)
        for inv_hero in Config.party_heroes:
            self.inventory_sprites.add(inv_hero)
        
        self.hero_spots = []
        for i in range(len(Config.party_heroes)):
            var_name = f"hero_spot{i + 1}"
            hero_rect = Config.party_heroes[i].rect
            value = pg.Rect(hero_rect.x - 5, hero_rect.y - 5, self.max_hero_width + 10, hero_rect.height + 10)
            setattr(self, var_name, value)
            inv_spot = getattr(self, var_name)
            self.hero_spots.append(inv_spot)
            Config.party_heroes[i].inventory_spot = inv_spot
        
        eq_slot_size_scalar = 30
        head_slot_spot = (self.screen_width *  0.32, self.screen_height * 0.10)
        head_slot_width = self.screen_width // eq_slot_size_scalar
        head_slot_height = self.screen_height // eq_slot_size_scalar
        self.head_slot = EquipmentSlot(head_slot_spot, head_slot_width, head_slot_width)
        self.eq_slots.append(self.head_slot)
        
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
                        self.original_spot = self.dragged_hero.inventory_spot
                        self.offset_x = mouse_pos[0] - self.dragged_hero.rect.x
                        self.offset_y = mouse_pos[1] - self.dragged_hero.rect.y
                        

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == self.primary_mouse_button:  
                if self.dragging:
                    for hero_spot in self.hero_spots:
                        if hero_spot.colliderect(self.dragged_hero.rect):
                            for bumped_hero in Config.party_heroes:
                                if bumped_hero.inventory_spot == hero_spot:
                                    bumped_hero.rect.x = self.original_spot.x
                                    bumped_hero.rect.y = self.original_spot.y
                                    bumped_hero.inventory_spot = self.original_spot
                            self.dragged_hero.rect.x = hero_spot.x
                            self.dragged_hero.rect.y = hero_spot.y
                            self.spot_found = True
                            self.dragged_hero.inventory_spot = hero_spot

                    if not self.spot_found:   
                        self.dragged_hero.rect.x = self.original_spot.x
                        self.dragged_hero.rect.y = self.original_spot.y
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
        #self.equipment_slot_sprites
        self.inventory_icon_sprites.draw(self.screen)
        
        for slot in self.eq_slots:
            slot.draw_border()

        for spot in self.hero_spots:
            pg.draw.rect(self.screen, self.black, spot, 3)

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        if self.dragging:
            pass
        #highlight correct drop point if collide