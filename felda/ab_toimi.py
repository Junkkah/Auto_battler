import pygame as pg
from ab_asetukset import *
#mitä täällä?
#spritet turhii?
#roskan piirtäminen täällä, ajetaan joka frame?

#travel toiminto
#combat toiminto
#non combat encounter
#leveling toiminto

#12.10 video level.run

class Toimi:
    def __init__(self):
        self.naytto = pg.display.set_mode((LEVEYS, KORKEUS))
        self.leveys = LEVEYS
        self.korkeus = KORKEUS
        #?
        self.display_surface = pg.display.get_surface()
        self.hero_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.map_sprites = pg.sprite.Group()

    def selection_screen(self):
        pg.display.set_caption("Main Screen")
        self.naytto.fill((255, 0, 255))
        pg.display.flip()
        #press m for map, in map hover over
    
    def info_screen(self):
        pg.display.set_caption("Tosimiehet ei tarvii ohjeita")
        self.naytto.fill((255, 255, 255))
        pg.display.flip()
    
    def map_screen(self):
        pass

    def combat_screen(self):
        pass


    def aja(self): #no custom draw
        pass
        #update and draw the game
        #self.visible_sprites.custom_draw(self.player)
        #self.visible_sprites.update() #miät halutaan piirtää
    
    #combat animation functiot tääl?
    #combatille oma tila jossain. tarvii olla kellotettu
    #def combat_animation(tekijä, attacktype?, self)
        