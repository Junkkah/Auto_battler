import pygame as pg
from states import States
from hero_ab import Hero
from objects import Monster
from animation import Stab, Slash, Blast, Smash


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
        #adjust in settings
        self.animation_speed = 0.3
 
    def cleanup(self):
        self.animation_sprites.empty()
        self.combat_hero_sprites.empty()
        self.combat_mob_sprites.empty()
        self.actions_unordered = []
        self.temp_stats = []
        States.room_monsters = []
        for cleanup_hero in States.party_heroes:
            cleanup_hero.exp += self.exp_reward 
        self.exp_reward = 0
        #Victory screen
        #loot here
        #pg.time.wait(2000)

    #gets called from inv
    #create helper functio in helpers.py
    #or hero method, get len(States.party_heroes), check find self.name position in States.party
    #for i in range len(S.party): S.party[i].get_into_position(i + 1) pos1,2,3,4
    def position_heroes(self, heroes: list):

        #adjust for variable hero count
        HEROPOS_X = (self.screen_width * 0.3)
        HEROPOS_Y = (self.screen_height * 0.6)
        HERO_GAP = (self.screen_width * 0.2)
        for phero in States.party_heroes:
           phero.rect = phero.image.get_rect(topleft = (HEROPOS_X, HEROPOS_Y)) 
           phero.pos_x = HEROPOS_X
           phero.pos_y = HEROPOS_Y
           HEROPOS_X += HERO_GAP
    
    def create_monsters(self):

        #define monster spots as function of n
        MONSTER_COUNT = len(States.room_monsters)
        MONSTER_NAMES = []
        MONSTER_NAMES.extend(States.room_monsters)
        MONSTERPOS_Y = self.screen_height * 0.2
        ONE_MONSTER_COORDS = (self.screen_width * 0.5, MONSTERPOS_Y)
        TWO_MONSTERS_COORDS = ((self.screen_width * 0.33, MONSTERPOS_Y), (self.screen_width * 0.66, MONSTERPOS_Y))
        THREE_MONSTERS_COORDS = ((self.screen_width * 0.25, MONSTERPOS_Y), (self.screen_width * 0.50, MONSTERPOS_Y), (self.screen_width * 0.75, MONSTERPOS_Y))

        if MONSTER_COUNT == 1:
            self.monster1 = Monster(self.monster_sprites, ONE_MONSTER_COORDS, MONSTER_NAMES[0]) 
            States.room_monsters = [self.monster1]
        elif MONSTER_COUNT == 2:
            self.monster1 = Monster(self.monster_sprites, TWO_MONSTERS_COORDS[0], MONSTER_NAMES[0]) 
            self.monster2 = Monster(self.monster_sprites, TWO_MONSTERS_COORDS[1], MONSTER_NAMES[1])
            States.room_monsters = [self.monster1, self.monster2]
        elif MONSTER_COUNT == 3:
            self.monster1 = Monster(self.monster_sprites, THREE_MONSTERS_COORDS[0], MONSTER_NAMES[0]) 
            self.monster2 = Monster(self.monster_sprites, THREE_MONSTERS_COORDS[1], MONSTER_NAMES[1])
            self.monster3 = Monster(self.monster_sprites, THREE_MONSTERS_COORDS[2], MONSTER_NAMES[2])
            States.room_monsters = [self.monster1, self.monster2, self.monster3]

    #tie breaker, first in hero/mob list > lower, hero > mob, class prios
    def order_sort(self, incombat: list):
        def speed_order(par: object): 
            return par.speed
        return sorted(incombat, key=speed_order, reverse=True)
        
    def startup(self):
        self.screen.fill((self.white))
        self.screen.blit(self.ground, (0,0))
        DELAY_AT_START = 400 #milliseconds

        self.position_heroes(States.party_heroes)
        self.create_monsters()

        for room_monster in States.room_monsters:
            self.combat_mob_sprites.add(room_monster)
            self.actions_unordered.append(room_monster)
        for party_hero in States.party_heroes:
            self.combat_hero_sprites.add(party_hero)
            self.actions_unordered.append(party_hero)
        
        MONSTERS_NAMES = [monster.type.capitalize() for monster in States.room_monsters]
        MONSTERS_TEXT = "Enemies: " + ", ".join(MONSTERS_NAMES)
        self.MONSTERS_TEXT = self.info_font.render(MONSTERS_TEXT, True, self.black)
        COORDS_MONSTERS_TEXT = (self.screen_width * 0.50, self.screen_height * 0.45)
        self.MONSTERS_RECT = self.MONSTERS_TEXT.get_rect(topleft=COORDS_MONSTERS_TEXT)

        self.combat_hero_sprites.draw(self.screen)
        self.combat_mob_sprites.draw(self.screen)
        self.screen.blit(self.MONSTERS_TEXT, self.MONSTERS_RECT)
        pg.display.update()
        #Use pg.time.wait(DELAY_AT_START)
        #pg.time.delay(DELAY_AT_START)
        
        self.actions_ordered = self.order_sort(self.actions_unordered)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            pass
            #pause button
        elif event.type == pg.MOUSEBUTTONDOWN:
            pass

    def update(self, screen, dt):

        #self.paused = True until press start button

        States.acting = self.actions_ordered[0]
        if States.acting.animation == False: #animation hasn't started yet
            if States.acting.player == True: #Attacker is hero
                if States.acting.attack_type == "weapon" or States.acting.spells == []:
                    self.combat_animation = Stab(States.acting.pos_x, States.acting.pos_y)
                else:
                    #hero always cast index 0 spell in self.spells
                    #create hero method for choosing spell to cast
                    self.combat_animation = Blast(States.acting.pos_x, States.acting.pos_y, States.acting.spells[0])
            elif States.acting.player == False:
                self.combat_animation = Smash((States.acting.pos_x + States.acting.width), (States.acting.pos_y + States.acting.height))
                #self.combat_animation = Slash((States.acting.pos_x + self.screen_width * 0.1), (States.acting.pos_y + self.screen_height * 0.1))
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

        for live_monster in States.room_monsters:
            live_monster.draw_health_bar()

        for live_hero in States.party_heroes:
            live_hero.draw_health_bar()

        if States.acting.animation == True: 
            self.animation_sprites.draw(screen)

        #move to update
        if self.combat_animation.animate(self.animation_speed) == True:
            #States.acting.melee_attack(States.room_monsters[0]) way to be correct attack type?
            self.animation_sprites.remove(self.combat_animation)
            self.actions_ordered.append(self.actions_ordered.pop(0))
            
            if States.acting.player == True:
                for fighting_monster in States.room_monsters:
                    if fighting_monster.health <=0:
                        self.combat_mob_sprites.remove(fighting_monster)
                        self.actions_ordered.remove(fighting_monster)
                        self.exp_reward += fighting_monster.exp
                        if self.exp_reward + States.party_heroes[0].exp >= States.party_heroes[0].next_level:
                            self.next = 'levelup' #problem if level up from last node?
                        else:
                            self.next = 'path'
                        States.room_monsters.remove(fighting_monster)
                        if States.room_monsters == []:
                            self.done = True

            elif States.acting.player == False:    
                for fighting_hero in States.party_heroes:
                    if fighting_hero.health <=0:
                        self.combat_hero_sprites.remove(fighting_hero)
                        self.actions_ordered.remove(fighting_hero)
                        States.party_heroes.remove(fighting_hero)
                        if States.party_heroes == []: #do loss screen
                            States.current_location = None
                            self.next = 'menu'
                            self.done = True