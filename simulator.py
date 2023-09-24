import pygame as pg
import sys
import csv
import random
from states import States
from objects import Hero
from stats import Data, Stats
from combat import Combat

class Simulator(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'menu'
       
    def cleanup(self):
        #reset variables to initial values at end of loop
        self.party = []
        States.party_heroes = []
        self.simu_paths = []
        self.party_exp = 0

    def startup(self):
        self.screen.fill(self.white)
        self.simulation_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.party_exp = 0
        self.exp_reward = 0
        self.party_size = 3
        self.simu_paths = []
        self.names = Stats().names
    #could load all data on startup and store in States

    def reset_variables(self):
        self.party = []
        States.party_heroes = []
        self.simu_paths = []
        self.party_exp = 0
        self.party_exp = 0
        self.exp_reward = 0
        self.simulation_sprites.empty()
        self.monster_sprites.empty()

    def run_simulation(self, count: int):
        self.number_of_simulations = count
        self.party = random.sample(self.names, 3)
        #needs to be random 8, choose 3 for ml model
        for simulated_hero in range(self.party_size):
            SIMU_X = 0
            SIMU_Y = 0
            self.simulated_hero = Hero((SIMU_X, SIMU_Y), self.simulation_sprites, self.party[simulated_hero][0], self.party[simulated_hero][1])
            States.party_heroes.append(self.simulated_hero)
            self.simulation_sprites.add(self.simulated_hero)
        
        States.current_adventure = "dark_forest"
        simulation_locations = Data.location_data(States.current_adventure)
        
        path1 = ['tree1', 'tree2', 'bush2', 'cave']
        path2 = ['tree1', 'bush2', 'bush3', 'cave']
        path3 = ['bush1', 'tree3', 'bush4', 'cave']
        path4 = ['bush1', 'tree4', 'bush4', 'cave']
        self.simu_paths.append(path1)
        self.simu_paths.append(path2)
        self.simu_paths.append(path3)
        self.simu_paths.append(path4)
        
        simulated_path = random.choice(self.simu_paths)
        simulated_monsters = []

        for location in simulated_path:
            monsters = []
            monsters = simulation_locations[location]['content'].split(" ")
            simulated_monsters.append(monsters)
        
        for monster_list in simulated_monsters:
            States.room_monsters = monster_list
            
            Combat().create_monsters()

            self.actions_unordered = []
            
            for room_monster in States.room_monsters:
                self.actions_unordered.append(room_monster)
            for party_hero in States.party_heroes:
                self.actions_unordered.append(party_hero)

            self.actions_ordered = Combat().order_sort(self.actions_unordered)

            while States.party_heroes and States.room_monsters:
                States.acting = self.actions_ordered[0] 
                if States.acting.player == True:
                    if States.acting.attack_type == "weapon" or not States.acting.spells:
                        States.acting.melee_attack()
                    else:
                        spell_attack(States.acting.spells[0]) #passing 1st spell
                    
                    for fighting_monster in States.room_monsters:
                        if fighting_monster.health <=0:
                            self.actions_ordered.remove(fighting_monster)
                            self.exp_reward += fighting_monster.exp
                            if self.exp_reward + States.party_heroes[0].exp >= States.party_heroes[0].next_level:
                                pass #do levelup

                            States.room_monsters.remove(fighting_monster)
                elif States.acting.player == False:
                    States.acting.melee_attack()
                    for fighting_hero in States.party_heroes:
                        if fighting_hero.health <=0:
                            self.actions_ordered.remove(fighting_hero)
                            States.party_heroes.remove(fighting_hero)

                self.actions_ordered.append(self.actions_ordered.pop(0))
        self.reset_variables #cleanup
        #Not running multiple times, cleanup problem?    
    if States.party_heroes:
        print("Win")
    else:
        print("Loss")
    
        #after each fight, check exp, goto inv if level
        #reduce self.number_of_simualtions =- 1
        #do cleanup

    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        screen.fill(self.white)

        SIMULATION_FONT_NAME = "Arial"
        simu_big_font = pg.font.SysFont(SIMULATION_FONT_NAME, self.big_font_size)
        MIDDLE = self.width * 0.50
        HEIGHT_GAP = self.height * 0.20
        COORDS_START = (MIDDLE, HEIGHT_GAP)
        START = 'Start'
        self.start_text = simu_big_font.render(START, True, self.black)
        self.start_rect = self.start_text.get_rect(center=COORDS_START) 
        self.screen.blit(self.start_text, self.start_rect)
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.start_rect.collidepoint(pg.mouse.get_pos()):
                self.run_simulation(1) #number of simulations as argument
            else:
                pass
    #save simulation result