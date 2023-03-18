import pygame
import math, sys, os
from pygame.locals import *

RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)

pygame.init()
w, h = 1920, 1080
screen = pygame.display.set_mode((w, h))
running = True

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)
path = os.path.join(path, 'bird.png')

ase = pygame.image.load('auto_battle/ab_kuvat/stab/sword2.png') #path
height = ase.get_height()
width = ase.get_width()
img0 = pygame.transform.scale(ase, ((width / 10), (height / 10)))
img0.convert()


# draw a green border around img0
rect0 = img0.get_rect()
pygame.draw.rect(img0, GREEN, rect0, 1)

center = w//2, h//2
img = img0
rect = img.get_rect()
rect.center = center

angle = 0
scale = 1

mouse = pygame.mouse.get_pos()

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_r:
                if event.mod & KMOD_SHIFT:
                    angle -= 10
                else:
                    angle += 10
                img = pygame.transform.rotozoom(img0, angle, scale)

            elif event.key == K_s:
                if event.mod & KMOD_SHIFT:
                    scale /= 1.1
                else:
                    scale *= 1.1
                img = pygame.transform.rotozoom(img0, angle, scale)

            elif event.key == K_o:
                img = img0
                angle = 0
                scale = 1

            elif event.key == K_h:
                img = pygame.transform.flip(img, True, False)
            
            elif event.key == K_v:
                img = pygame.transform.flip(img, False, True)

            elif event.key == K_l:
                img = pygame.transform.laplacian(img)

            elif event.key == K_2:
                img = pygame.transform.scale2x(img)

            rect = img.get_rect()
            rect.center = center #miten tämän muuttaminen vaikuttaa
    
    screen.fill(GRAY)
    screen.blit(img, rect)
    pygame.draw.rect(screen, RED, rect, 1)
    pygame.draw.line(screen, GREEN, center, mouse, 1)
    pygame.draw.circle(screen, RED, center, 6, 1)
    pygame.draw.circle(screen, RED, mouse, 6, 1)
    pygame.display.update()

pygame.quit()