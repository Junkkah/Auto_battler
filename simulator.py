import pygame as pg
import sys
import csv
import random
from states import States
from objects import Hero, TalentName
from stats import Data, Stats, get_data
from combat import Combat

class Simulator(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'menu'
       
    def cleanup(self):
        self.party = []
        States.party_heroes = []
        self.simu_paths = []
        self.party_exp = 0
        self.exp_reward = 0

    def startup(self):
        self.screen.fill(self.white)
        self.simulation_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.party_exp = 0
        self.exp_reward = 0
        self.party_size = 3
        self.simu_paths = []
        self.names = get_data('names')
        #self.names = Stats().names
        self.COUNT = 10

    def reset_variables(self):
        self.party = []
        States.party_heroes = []
        self.simu_paths = []
        self.party_exp = 0 #not used?
        self.exp_reward = 0
        self.simulation_sprites.empty()
        self.monster_sprites.empty()

    def run_simulation(self): #Full dark forest adventure
        simulation_results = []
        selection = random.sample(self.names, 8)
        self.party = random.sample(selection, 3)

        for simulated_hero in range(self.party_size):
            SIMU_X = 0
            SIMU_Y = 0
            self.simulated_hero = Hero((SIMU_X, SIMU_Y), self.simulation_sprites, self.party[simulated_hero][0], self.party[simulated_hero][1])
            States.party_heroes.append(self.simulated_hero)
            self.simulation_sprites.add(self.simulated_hero)
        
        States.current_adventure = "dark_forest"
        #get_data(States.current_adventure)
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

        simulation_results.append(simulated_path)
        simulation_results.append(self.party)
        
        talent_dicts = {}
        for p in range(self.party_size):
            talent_dicts[simulation_results[1][p][0]] = []
            
        simulation_results.append(talent_dicts)

        for location in simulated_path:
            monsters = []
            monsters = simulation_locations[location]['content'].split(" ")
            simulated_monsters.append(monsters)

        for monster_list in simulated_monsters: #Fight monsters in four locations
            States.room_monsters = monster_list
            
            Combat().create_monsters() #monster objects

            self.actions_unordered = []
            
            for room_monster in States.room_monsters:
                self.actions_unordered.append(room_monster)
            for party_hero in States.party_heroes:
                self.actions_unordered.append(party_hero)

            self.actions_ordered = Combat().order_sort(self.actions_unordered)

            while States.party_heroes and States.room_monsters: #loop combat 
                States.acting = self.actions_ordered[0] 
                if States.acting.player == True:
                    if States.acting.attack_type == "weapon" or not States.acting.spells:
                        States.acting.melee_attack()
                    else:
                        States.acting.spell_attack(States.acting.spells[0]) #passing 1st spell
                    
                    for fighting_monster in States.room_monsters:
                        if fighting_monster.health <=0:
                            self.actions_ordered.remove(fighting_monster)
                            self.exp_reward += fighting_monster.exp

                            States.room_monsters.remove(fighting_monster)
                elif States.acting.player == False:
                    States.acting.melee_attack()
                    for fighting_hero in States.party_heroes:
                        if fighting_hero.health <=0:
                            self.actions_ordered.remove(fighting_hero)
                            States.party_heroes.remove(fighting_hero)

                self.actions_ordered.append(self.actions_ordered.pop(0))

            if States.party_heroes and self.exp_reward + States.party_heroes[0].exp >= States.party_heroes[0].next_level:
                for leveling_hero in States.party_heroes:
                    #Class for leveling up
                    Stats().levelup(leveling_hero)

                #talent_data = get_data('talents')
                #self.talent_lists = get_data('talents')
                self.talent_lists = [Data.talent_data(thero.type) for thero in States.party_heroes]
                self.numer_of_heroes = len(States.party_heroes)
                samples = [random.sample(t.items(), 2) for t in self.talent_lists]
                talents = []

                for i in range(self.numer_of_heroes):
                    X = 1 
                    Y = 1,1
                    sample = samples[i]
                    hero = States.party_heroes[i] 
                    name_value = TalentName(sample, X, Y, self.info_font, hero)
                    talents.append(name_value)
                    simulation_results[2][hero.name].append(name_value.a_name)

                for s_talent in talents: #always adds a talents - randomize between a and b
                    Stats().add_talent(s_talent.hero, s_talent.a_name, s_talent.a_type)

        #write results into dataframe and store as sql table?
        simulation_results.append(self.exp_reward)
        if States.party_heroes:
            simulation_results.append(
                'True')
        else:
            simulation_results.append(
                'False')

        with open('simulation_results.csv', 'a', newline='') as sim_data:
            writer = csv.writer(sim_data)
            writer.writerow(simulation_results)

        self.reset_variables() #cleanup  

    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        screen.fill(self.white)
        #display simulation results
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
        elif event.type == pg.MOUSEBUTTONDOWN: #add button press effect
            if self.start_rect.collidepoint(pg.mouse.get_pos()):
                for _ in range(self.COUNT):
                    self.run_simulation()
            else:
                pass
