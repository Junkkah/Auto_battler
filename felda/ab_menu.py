import pygame
from ab_asetukset import *
from ab_toimi import Toimi

#meni object has no attribute pelaa
#eli minne napit johtaa
#menu musat

class Menu:
    def __init__(self):
        self.naytto = pygame.display.set_mode((LEVEYS, KORKEUS))
        self.leveys = LEVEYS
        self.korkeus = KORKEUS
        self.toimi = Toimi()

    def alku(self):
        pygame.display.set_caption("Menu Screen")
        self.naytto.fill((102, 102, 255))
        #pygame.mixer.music.load('auto_battle/synth.mp3')
        #pygame.mixer.music.play(-1)
        #Failed loading libmpg123-0.dll
        while True: #LOOP
            menu_hiiri = pygame.mouse.get_pos()
            menu_fontti = pygame.font.SysFont("Arial", 50)
            otsikko_fontti = pygame.font.SysFont("Arial", 75)
            otsikko_teksti = otsikko_fontti.render("Ukko Advantures", True, (0, 0, 0))
            otsikko_rect = otsikko_teksti.get_rect(center=(self.leveys / 2, self.korkeus / 6))

            pelaa_teksti = menu_fontti.render("Pelaamaan", True, (0, 0, 0))
            pelaa_rect = pelaa_teksti.get_rect(center=(self.leveys / 2, self.korkeus / 3))

            info_teksti = menu_fontti.render("Info", True, (0, 0, 0))
            info_rect = info_teksti.get_rect(center=(self.leveys / 2, self.korkeus / 2))

            lopeta_teksti = menu_fontti.render("Lopeta", True, (0, 0, 0))
            lopeta_rect = lopeta_teksti.get_rect(center=(self.leveys / 2, self.korkeus / 1.5))
                
            self.naytto.blit(pelaa_teksti, pelaa_rect)
            self.naytto.blit(otsikko_teksti, otsikko_rect)
            self.naytto.blit(info_teksti, info_rect)
            self.naytto.blit(lopeta_teksti, lopeta_rect)
            pygame.display.flip()
        
            for tapahtuma in pygame.event.get():
                if tapahtuma.type == pygame.QUIT:
                    exit()
                if tapahtuma.type == pygame.MOUSEBUTTONDOWN:
                    if pelaa_rect.collidepoint(menu_hiiri):
                        self.naytto.fill((0, 0, 0))
                        pygame.display.flip()
                        self.toimi.selection_screen() #pelin pääruutu
                    if info_rect.collidepoint(menu_hiiri):
                        self.naytto.fill((0, 0, 0,))
                        pygame.display.flip()
                        self.toimi.info_screen()
                    if lopeta_rect.collidepoint(menu_hiiri):
                        exit()
                            