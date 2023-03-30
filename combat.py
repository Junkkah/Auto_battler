import pygame as pg
import sys
from states import States
from objects import Hero, Monster
from animation import Stab, Slash, Blast
from path import Path
from stats import Stats
from inv import Inv

class Combat(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'path' 
        self.actions_unordered = []
        self.combat_hero_sprites = pg.sprite.Group()
        self.combat_mob_sprites = pg.sprite.Group()
        self.animation_sprites = pg.sprite.Group()
        self.exp_reward = 0
        self.temp_stats = [] #buffs etc
 
    def cleanup(self):
        self.animation_sprites.empty()
        self.combat_hero_sprites.empty()
        self.combat_mob_sprites.empty()
        self.actions_unordered = []
        self.temp_stats = []
        States.room_monsters = []
        for ehero in States.party_heroes:
            ehero.exp += self.exp_reward 
        self.exp_reward = 0
        #Victory screen
        #loot here
        #pg.time.wait(2000)
        
    def startup(self):
        self.screen.fill((self.white))
        self.screen.blit(self.ground, (0,0))

        MONSTER_COUNT = len(States.room_monsters)
        MONSTER_NAMES = []
        MONSTER_NAMES.extend(States.room_monsters)
        MONSTER_YPOS = self.height * 0.2
        ONE_MONSTER_COORDS = (self.width * 0.5, MONSTER_YPOS)
        TWO_MONSTERS_COORDS = ((self.width * 0.33, MONSTER_YPOS), (self.width * 0.66, MONSTER_YPOS))
        THREE_MONSTERS_COORDS = ((self.width * 0.25, MONSTER_YPOS), (self.width * 0.50, MONSTER_YPOS), (self.width * 0.75, MONSTER_YPOS))

        if MONSTER_COUNT == 1:
            self.monster1 = Monster(ONE_MONSTER_COORDS, self.monster_sprites, MONSTER_NAMES[0]) 
            States.room_monsters = [self.monster1]
        elif MONSTER_COUNT == 2:
            self.monster1 = Monster(TWO_MONSTERS_COORDS[0], self.monster_sprites, MONSTER_NAMES[0]) 
            self.monster2 = Monster(TWO_MONSTERS_COORDS[1], self.monster_sprites, MONSTER_NAMES[1])
            States.room_monsters = [self.monster1, self.monster2]
        elif MONSTER_COUNT == 3:
            self.monster1 = Monster(THREE_MONSTERS_COORDS[0], self.monster_sprites, MONSTER_NAMES[0]) 
            self.monster2 = Monster(THREE_MONSTERS_COORDS[1], self.monster_sprites, MONSTER_NAMES[1])
            self.monster3 = Monster(THREE_MONSTERS_COORDS[2], self.monster_sprites, MONSTER_NAMES[2])
            States.room_monsters = [self.monster1, self.monster2, self.monster3]

        HERO_XPOS = (self.width * 0.3)
        HERO_YPOS = (self.height * 0.6)
        HERO_GAP = (self.width * 0.2)
        for phero in States.party_heroes:
           phero.rect = phero.image.get_rect(topleft = (HERO_XPOS, HERO_YPOS)) 
           phero.xpos = HERO_XPOS
           phero.ypos = HERO_YPOS
           HERO_XPOS += HERO_GAP

        for room_monster in States.room_monsters:
            self.combat_mob_sprites.add(room_monster)
            self.actions_unordered.append(room_monster)
        for party_hero in States.party_heroes:
            self.combat_hero_sprites.add(party_hero)
            self.actions_unordered.append(party_hero)
        
        MONSTERS_NAMES = [monster.type.capitalize() for monster in States.room_monsters]
        MONSTERS_TEXT = "Enemies: " + ", ".join(MONSTERS_NAMES)
        self.MONSTERS_TEXT = self.info_font.render(MONSTERS_TEXT, True, self.black)
        COORDS_MONSTERS_TEXT = (self.width * 0.50, self.height * 0.45)
        self.MONSTERS_RECT = self.MONSTERS_TEXT.get_rect(topleft=COORDS_MONSTERS_TEXT)

        self.combat_hero_sprites.draw(self.screen)
        self.combat_mob_sprites.draw(self.screen)
        self.screen.blit(self.MONSTERS_TEXT, self.MONSTERS_RECT)
        pg.display.update()
        pg.time.delay(300)
        
        #tie breaker, first in hero/mob list > lower, hero > mob, class prios
        def order_sort(incombat: list):
            def speed_order(par: object):
                return par.data["speed"]
            return sorted(incombat, key=speed_order, reverse=True)
        self.actions_ordered = order_sort(self.actions_unordered)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            pass
            #pause button
        elif event.type == pg.MOUSEBUTTONDOWN:
            pass
    
    #hero target is always mob[0] and mob target is hero[0]
    #Needs targeting algo
    def update(self, screen, dt):
        States.acting = self.actions_ordered[0]
        if States.acting.animation == False: #animation hasn't started yet
            if States.acting.player == True: #Attacker is hero
                if States.acting.attack_type == "weapon" or States.acting.spells == []:
                    self.combat_animation = Stab(States.acting.xpos, States.acting.ypos)
                else:
                    self.combat_animation = Blast(States.acting.xpos, States.acting.ypos, States.acting.spells[0])#passing 1st spell
            elif States.acting.player == False:
                self.combat_animation = Slash((States.acting.xpos + self.width * 0.1), (States.acting.ypos + self.height * 0.1))
            else:
                pass
            self.animation_sprites.add(self.combat_animation)
            States.acting.animation = True
            self.combat_animation.animation_start()

        self.draw(screen)
    def draw(self, screen):
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.combat_hero_sprites.draw(self.screen)
        self.combat_mob_sprites.draw(self.screen)
        
        if States.acting.animation == True: 
            self.animation_sprites.draw(screen)

        #Advance animation
        if self.combat_animation.animate(1) == True:
            self.animation_sprites.remove(self.combat_animation)
            self.actions_ordered.append(self.actions_ordered.pop(0))
            
            if States.acting.player == True:
                for health_check in States.room_monsters:
                    if health_check.health <=0:#get target instead of [0] #data["health"]
                        self.combat_mob_sprites.remove(health_check)
                        self.actions_ordered.remove(health_check)
                        self.exp_reward += health_check.exp
                        
                        if self.exp_reward + States.party_heroes[0].exp >= States.party_heroes[0].next_level:
                            self.next = 'inv'
                        else:
                            self.next = 'path'
                        States.room_monsters.remove(health_check)
                        if States.room_monsters == []:
                            self.done = True

            elif States.acting.player == False:    
                if States.party_heroes[0].health <=0: #data["health"]
                    self.combat_hero_sprites.remove(States.party_heroes[0])
                    self.actions_ordered.remove(States.party_heroes[0])
                    States.party_heroes.remove(States.party_heroes[0])
                    if States.party_heroes == []: #do loss screen
                        self.next = 'menu'
                        self.done = True
            
