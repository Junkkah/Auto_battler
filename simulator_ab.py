import pygame as pg
import pandas as pd
import random
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Button
from data_ab import get_data, enter_simulation_result
from battle_ab import BattleManager
from sounds_ab import sound_effect
from path_ab import Path
from levelup_ab import LevelUp

# Simulation runtime for self.COUNT = 5000 estimated 4h 30mins

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
        self.results_list = []
        self.simulation_sprites.empty()
        self.help_sprites.empty()

    def startup(self):
        self.simulation_hero_sprites = pg.sprite.Group()
        self.simulation_sprites = pg.sprite.Group()
        self.simulation_monster_sprites = pg.sprite.Group()
        self.help_sprites = pg.sprite.Group()
        self.party_exp = 0
        self.exp_reward = 0
        self.party_size = 3
        self.simu_paths = []
        self.names_df = get_data('names')
        self.talent_lists = get_data('talents')
        self.COUNT = 1000
        self.results_list = []
        self.sim_done = False

        FONT_NAME = "Arial"
        COORDS_START = (self.screen_width * 0.50, self.screen_height * 0.40)
        COORDS_FOREST = (self.screen_width * 0.50, self.screen_height * 0.20)
        COORDS_DONE = (self.screen_width * 0.50, self.screen_height * 0.50)
        START = 'Start'
        FOREST = 'Set: Dark Forest'
        DONE = 'Done'

        self.start_button = Button(self.simulation_sprites, START, FONT_NAME, self.big_font_size, self.black, COORDS_START)
        self.forest_button = Button(self.simulation_sprites, FOREST, FONT_NAME, self.medium_font_size, self.black, COORDS_FOREST)
        self.done_button = Button(self.help_sprites, DONE, FONT_NAME, self.medium_font_size, self.black, COORDS_DONE)

        info = "Simulation is running"
        self.info_text = self.info_font.render(info, True, self.black)
        self.info_text_rect = self.info_text.get_rect(center=COORDS_DONE)
        
    def reset_variables(self):
        self.party = []
        Config.party_heroes = []
        self.simu_paths = []
        self.fallen_heroes = []
        self.sim_loc_df = None
        self.party_exp = 0 
        self.exp_reward = 0
        self.simulation_monster_sprites.empty()
        self.simulation_hero_sprites.empty()
    
    def generate_random_path(self, start_node):
        random_path = [start_node]
        current_node = start_node

        while current_node != 'cave':
            current_row = self.sim_loc_df[self.sim_loc_df['name'] == current_node].iloc[0]
            
            has_child1 = current_row['child1'] is not None
            has_child2 = current_row['child2'] is not None
            
            if has_child1 and has_child2:
                next_node = random.choice([current_row['child1'], current_row['child2']])
            elif has_child1:
                next_node = current_row['child1']
            else:
                break
            
            current_node = next_node
            random_path.append(current_node)
        
        return random_path

    def create_encounter(self, tier) -> list:
        loc_tier = tier
        adv = Config.current_adventure 
        encounters_df = get_monster_encounters(adv, tier)
        probs = encounters_df['Probability'].tolist()
        mob_lists = encounters_df.apply(lambda row: [value for value in row[4:].tolist() if value is not None], axis=1).tolist()
        encounter = random.choices(mob_lists, weights=probs, k=1)[0]

        return encounter


    def run_simulation(self): 
        simulation_results = []
        self.names = [tuple(row) for row in self.names_df[['name', 'type']].values]
        selection = random.sample(self.names, 8)
        self.party = random.sample(selection, 3)


        for simulated_hero in range(self.party_size):
            SIMU_X = 0
            SIMU_Y = 0
            self.simulated_hero = Hero(self.simulation_hero_sprites, (SIMU_X, SIMU_Y), self.party[simulated_hero][0], self.party[simulated_hero][1])
            Config.party_heroes.append(self.simulated_hero)
            self.simulation_hero_sprites.add(self.simulated_hero)
        
        self.sim_loc_df = get_data(Config.current_adventure)

        #create adventure independent starting location list
        start_loc = random.choice(['tree1', 'tree2', 'tree3'])

        simulated_path = self.generate_random_path(start_loc)
        simulated_monsters = []
        
        simulation_results.append(simulated_path)
        simulation_results.append(self.party)

        talent_dicts = {}
        for p in range(self.party_size):
            talent_dicts[simulation_results[1][p][0]] = []
            
        simulation_results.append(talent_dicts)

        monsters = []
        path_instance = Path()
        for location in simulated_path:
            row = self.sim_loc_df[self.sim_loc_df['name'] == location].iloc[0]
            #skipping over shopping for now
            if row['type'] == 'shop':
                pass
            tier = int(row['tier'])
            monsters = path_instance.create_encounter(tier)

            simulated_monsters.append(monsters)

        #take first monster list in simulated_monsters and loop battle
        #rooms_done += 1 to count final room
        for monster_list in simulated_monsters:
            Config.room_monsters = monster_list
            #monster objects
            BattleManager().create_monsters() 

            self.actions_unordered = []
            
            for room_monster in Config.room_monsters:
                self.actions_unordered.append(room_monster)
            for party_hero in Config.party_heroes:
                self.actions_unordered.append(party_hero)

            self.actions_ordered = BattleManager().order_sort(self.actions_unordered)
            self.fallen_heroes = []

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
                            self.fallen_heroes.append(fighting_hero)
                            #revive fallen hero for next node

                self.actions_ordered.append(self.actions_ordered.pop(0))

            if Config.party_heroes and self.exp_reward + Config.party_heroes[0].exp >= Config.party_heroes[0].next_level:
                if self.fallen_heroes:
                    for reviving_hero in self.fallen_heroes:
                        Config.party_heroes.append(reviving_hero)
                        reviving_hero.health = reviving_hero.max_health // 2
                for leveling_hero in Config.party_heroes:
                    leveling_hero.gain_level()

                samples = []
                self.numer_of_heroes = len(Config.party_heroes)
                levelup_instance = LevelUp()
                for sample_hero in Config.party_heroes:
                    sample = levelup_instance.create_talent_sample(sample_hero)
                    samples.append(sample)

                talents = []
                for talent_df in samples:
                    random_row = talent_df.sample(n=1)
                    talents.append(random_row)

                
                for i in range(self.numer_of_heroes):
                    talent = talents[i]
                    hero = Config.party_heroes[i] 

                    talent_name = talent['name'].iloc[0]
                    talent_type = talent['type'].iloc[0]
                    
                    hero.add_talent(talent_name, talent_type)
                    simulation_results[2][hero.name].append(talent_name)

        simulation_results.append(self.exp_reward)
        if Config.party_heroes:
            simulation_results.append('True')
        else:
            simulation_results.append('False')
        

        self.reset_variables() #cleanup 
        return simulation_results 
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.start_button.rect.collidepoint(pg.mouse.get_pos()):
                if Config.current_adventure:  
                    self.sim_done = False
                    sound_effect('click')
                    for _ in range(self.COUNT):
                        result = self.run_simulation()
                        self.results_list.append(result)
                        self.screen.blit(self.info_text, self.info_text_rect)

                    columns = ['nodes', 'heroes', 'talents', 'exp', 'boss_defeated']
                    results_df = pd.DataFrame(self.results_list, columns=columns)
                    
                    for _, row in results_df.iterrows():
                        enter_simulation_result(row)
                    self.sim_done = True

                else:
                    sound_effect('error')

            elif self.forest_button.rect.collidepoint(pg.mouse.get_pos()):
                sound_effect('click')
                Config.current_adventure = 'dark_forest'
            
            elif self.done_button.rect.collidepoint(pg.mouse.get_pos()):
                sound_effect('click')
                self.sim_done = False

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        screen.fill(self.grey)
        #display simulation results

        self.simulation_sprites.draw(self.screen)

        if self.sim_done:
            self.help_sprites.draw(self.screen)
