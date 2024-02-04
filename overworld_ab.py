import pygame as pg
import sys
from config_ab import Config
from sprites_ab import Adventure
from data_ab import get_data, row_to_dict

class WorldMap(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path'
        self.error = False

    def cleanup(self):
        self.map_objects = []
        self.map_sprites.empty()

    def startup(self):
        #similar method in locations
        map_data = get_data('adventures')
        self.map_objects = []
        for index, row in map_data.iterrows():
            name = row['name']
            coords = (row['pos_x'], row['pos_y'])
            desc = row['desc']
            adventure = Adventure(coords, self.map_sprites, desc, name)
            self.map_objects.append(adventure)

        bubble = pg.image.load('./ab_images/map_bubble.png').convert_alpha()
        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        COORDS_BUBBLE  = (self.screen_width * 0.12, self.screen_height * 0.85)
        COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
        SCALAR_BUBBLE = ((bubble.get_width() / 7), (bubble.get_height() / 7))
        SCALAR_HOOD = ((hood.get_width() / 8), (hood.get_height() / 8))

        self.bubble = pg.transform.smoothscale(bubble, SCALAR_BUBBLE)
        self.hood = pg.transform.smoothscale(hood, SCALAR_HOOD)
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
                        Config.current_adventure = obj.name
                        self.done = True

                    else:
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