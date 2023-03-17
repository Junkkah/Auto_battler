import pygame
from settings import *
#vid@15:25 - 17:32
class Hero(pygame.sprite.Sprite):
    def __init__(self, pos, groups): #ja nimi / numerointi, jolloin voidaan ottaa ab_kuvat/nimi.png
        super().__init__(groups)
        self.image = pygame.image.load('auto_battle/ab_kuvat/ab_naama.png')
        self.rect = self.image.get_rect(topleft = pos)