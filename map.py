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
        self.map_objects = [Adventure((adv["xpos"], adv["ypos"]), self.map_sprites, adv["desc"], adv["name"]) for adv in adventures.values()]

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
                        self.error_text_rect = self.error_text.get_rect(topleft=((obj.xpos), (obj.ypos)))
                        self.error = True
    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))
        self.map_sprites.draw(self.screen)

        collided_objects = [obj for obj in self.map_objects if obj.rect.collidepoint(pg.mouse.get_pos())]
        if collided_objects:
            obj = collided_objects[0]
            info_text = self.info_font.render(obj.desc, True, (0, 0, 0))
            info_text_rect = info_text.get_rect(bottomleft=(obj.xpos, obj.ypos + 5))
            self.screen.blit(info_text, info_text_rect)
            if obj.name == "dark_forest":
                pg.draw.rect(self.screen, self.red, [obj.xpos, obj.ypos, obj.width, obj.height], 2)
        
        if self.error == True:
            self.screen.blit(self.error_text, self.error_text_rect)