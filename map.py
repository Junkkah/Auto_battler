import pygame as pg
import sys
from states import States
from objects import Adventure
from stats import Stats

class Map(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'path'
        self.stats = Stats()
        self.map_sprites = pg.sprite.Group()
        self.error = False
    def cleanup(self):
        pass 
    def startup(self):
        adventures = self.stats.map
        self.map_objects = [Adventure((adv["pos_x"], adv["pos_y"]), self.map_sprites, adv["desc"], adv["name"]) for adv in adventures.values()]

        bubble = pg.image.load('./ab_images/map_bubble.png').convert_alpha()
        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        COORDS_BUBBLE  = (self.width * 0.12, self.height * 0.85)
        COORDS_HOOD = (self.width * 0.05, self.height * 0.80)
        SCALAR_BUBBLE = ((bubble.get_width() / 7), (bubble.get_height() / 7))
        SCALAR_HOOD = ((hood.get_width() / 8), (hood.get_height() / 8))

        self.bubble = pg.transform.scale(bubble, SCALAR_BUBBLE)
        self.hood = pg.transform.scale(hood, SCALAR_HOOD)
        self.bubble_rect = self.bubble.get_rect(bottomleft=COORDS_BUBBLE)
        self.hood_rect = self.hood.get_rect(topleft=COORDS_HOOD)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            for obj in self.map_objects:
                if obj.rect.collidepoint(pg.mouse.get_pos()):
                    if obj.name == "dark_forest":
                        States.current_adventure = obj.name
                        self.done = True
                    elif obj.name != "dark_forest":
                        error = "Inaccessible"
                        self.error_text = self.info_font.render((error), True, (self.red))
                        self.error_text_rect = self.error_text.get_rect(topleft=((obj.pos_x), (obj.pos_y)))
                        self.error = True
    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.map_sprites.draw(self.screen)

        self.screen.blit(self.bubble, self.bubble_rect)
        self.screen.blit(self.hood, self.hood_rect)

        collided_objects = [obj for obj in self.map_objects if obj.rect.collidepoint(pg.mouse.get_pos())]
        if collided_objects:
            obj = collided_objects[0]
            info_text = self.info_font.render(obj.desc, True, self.black)
            info_text_rect = info_text.get_rect(bottomleft=(obj.pos_x, obj.pos_y + 5))
            self.screen.blit(info_text, info_text_rect)
            if obj.name == "dark_forest":
                pg.draw.rect(self.screen, self.red, [obj.pos_x, obj.pos_y, obj.width, obj.height], 2)
        
        if self.error == True:
            self.screen.blit(self.error_text, self.error_text_rect)