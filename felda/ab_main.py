
#scannaa korteista kuvapohja
#menuscreen LOOP tänne ja rakenna state machine
#yhdenmukaista language
#NEED SPRITE GROUPS
#party selection screen -> map screen -> choose room in path -> combat screen -> combat resolution

#toimi toimintojen funktiot
#kortit korttien tiedot
#mättö ruutu oma tiedosto?
#missä ajetaan sankarien importtaaminen
import pygame as pg
import sys
from ab_asetukset import *
from ab_toimi import Toimi
from ab_menu import Menu
from ab_map import Map
from ab_kortit import Sankarit

class Peli:
    def __init__(self):
        pg.init()
        self.naytto = pg.display.set_mode((LEVEYS, KORKEUS))
        self.kello = pg.time.Clock()
        self.toimi = Toimi()
        self.ab_menu = Menu()
        pg.display.set_caption("Ukko Advantures")
        #generate sankarit
    
    def pelaa(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                    #sys.exit()
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    pass

                if event.type == pg.KEYDOWN:
                    pass
            
            self.naytto.fill((0, 0, 0))
            self.ab_menu.alku()
            #self.toimi.aja() tämä sit kun menusta mennään pelaamaan
            #pg.display.flip()
            #tarpeetin out of combat?
            #self.kello.tick(FPS)

if __name__ == "__main__":
    peli = Peli()
    peli.pelaa()