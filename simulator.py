import pygame as pg
import sys
import csv
import random
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Button, TalentCard
from data_ab import get_data
from battle_ab import BattleManager
from sounds_ab import sound_effect

class Simulator(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'menu'
       
    def cleanup(self):
        self.party = []
        Config.party_heroes = []
        self.simu_paths = []
        self.party_exp = 0
        self.exp_reward = 0

    def startup(self):
        #self.screen.fill(self.white)
        self.simulation_sprites = pg.sprite.Group()
        self.monster_sprites = pg.sprite.Group()
        self.party_exp = 0
        self.exp_reward = 0
        self.party_size = 3
        self.simu_paths = []
        self.names = get_data('names')
        #self.names = Stats().names
        self.COUNT = 10

        FONT_NAME = "Arial"
        COORDS_START = (self.width * 0.50, self.height * 0.20)
        START = 'Start'

        self.start_button = Button(self.simulation_sprites, START, FONT_NAME, self.big_font_size, self.black, COORDS_START)

    def reset_variables(self):
        self.party = []
        Config.party_heroes = []
        self.simu_paths = []
        self.party_exp = 0 
        self.exp_reward = 0
        self.simulation_sprites.empty()
        self.monster_sprites.empty()

    def run_simulation(self): 
        simulation_results = []
        selection = random.sample(self.names, 8)
        self.party = random.sample(selection, 3)

        for simulated_hero in range(self.party_size):
            SIMU_X = 0
            SIMU_Y = 0
            self.simulated_hero = Hero((SIMU_X, SIMU_Y), self.simulation_sprites, self.party[simulated_hero][0], self.party[simulated_hero][1])
            Config.party_heroes.append(self.simulated_hero)
            self.simulation_sprites.add(self.simulated_hero)
        
        Config.current_adventure = "dark_forest"
        simulation_locations = get_data(Config.current_adventure)

        #old paths
        start_loc = random.choice(['tree1', 'tree2', 'tree3'])
        #create location objects
        #set location children
        #traverse: if child2: choose child1 or child2 else: child1
        #result is simulated_path
        #need to call create_ecnounter(loc) for each location
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
            #monsters = path.create_encounter(location)
            monsters = simulation_locations[location]['content'].split(" ")
            simulated_monsters.append(monsters)

        for monster_list in simulated_monsters:
            Config.room_monsters = monster_list
            
            BattleManager().create_monsters() #monster objects

            self.actions_unordered = []
            
            for room_monster in Config.room_monsters:
                self.actions_unordered.append(room_monster)
            for party_hero in Config.party_heroes:
                self.actions_unordered.append(party_hero)

            self.actions_ordered = BattleManager().order_sort(self.actions_unordered)

            while Config.party_heroes and Config.room_monsters: #loop combat 
                Config.acting = self.actions_ordered[0] 
                if Config.acting.player:
                    if Config.acting.attack_type == "weapon" or not Config.acting.spells:
                        Config.acting.melee_attack()
                    else:
                        Config.acting.spell_attack(Config.acting.spells[0]) #passing 1st spell
                    
                    for fighting_monster in Config.room_monsters:
                        if fighting_monster.health <=0:
                            self.actions_ordered.remove(fighting_monster)
                            self.exp_reward += fighting_monster.exp

                            Config.room_monsters.remove(fighting_monster)
                elif not Config.acting.player: # == False
                    Config.acting.melee_attack()
                    for fighting_hero in Config.party_heroes:
                        if fighting_hero.health <=0:
                            self.actions_ordered.remove(fighting_hero)
                            Config.party_heroes.remove(fighting_hero)
                            #fallen_heroes.append(fighting_hero)
                            #revive fallen hero for next node

                self.actions_ordered.append(self.actions_ordered.pop(0))

            if Config.party_heroes and self.exp_reward + Config.party_heroes[0].exp >= Config.party_heroes[0].next_level:
                for leveling_hero in Config.party_heroes:
                    leveling_hero.level_up()

                #get talents code from levelup
                #talent_data = get_data('talents')
                self.talent_lists = get_data('talents')
                #self.talent_lists = [Data.talent_data(thero.type) for thero in Config.party_heroes]
                self.numer_of_heroes = len(Config.party_heroes)
                #samples = [random.sample(t.items(), 2) for t in self.talent_lists]
                samples = []
                for talent_df in self.talent_dfs:
                    random_rows = talent_df.sample(n=2)
                    new_df = pd.DataFrame(random_rows)
                    samples.append(new_df)
                talents = []

                #old talent code
                for i in range(self.numer_of_heroes):
                    X = 1 
                    Y = 1,1
                    sample = samples[i]
                    hero = Config.party_heroes[i] 
                    name_value = TalentName(sample, X, Y, self.info_font, hero)
                    talents.append(name_value)
                    simulation_results[2][hero.name].append(name_value.a_name)

                #old talent code
                for s_talent in talents: #always adds a talents - randomize between a and b
                    Stats().add_talent(s_talent.hero, s_talent.a_name, s_talent.a_type)

        #write results into dataframe
        simulation_results.append(self.exp_reward)
        if Config.party_heroes:
            simulation_results.append(
                'True')
        else:
            simulation_results.append(
                'False')

        with open('simulation_results.csv', 'a', newline='') as sim_data:
            writer = csv.writer(sim_data)
            writer.writerow(simulation_results)

        #where is cleanup between node?
        self.reset_variables() #cleanup  

    def update(self, screen, dt):
        self.draw(screen)
    def draw(self, screen):
        screen.fill(self.grey)
        #display simulation results

        self.simulation_sprites.draw(self.screen)
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.start_button.rect.collidepoint(pg.mouse.get_pos()):
                sound_effect('click')
                for _ in range(self.COUNT):
                    self.run_simulation()
            else:
                pass