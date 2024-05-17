import pygame as pg
import pandas as pd
import random
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Button
from data_ab import get_data, enter_simulation_result, get_talent_data, get_monster_encounters
from battle_ab import BattleManager
from sounds_ab import play_sound_effect
from path_ab import Path
from overworld_ab import WorldMap
from levelup_ab import LevelUp

class Simulator(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'menu'

    def cleanup(self):
        self.party = []
        self.results_list = []
        self.simu_paths = []
        Config.party_heroes = []
        Config.completed_adventures = []
        Config.party_backpack = {}
        Config.party_followers = []
        Config.backpack_slots = []
        Config.equipment_slots = []
        Config.current_adventure = None
        Config.current_location = None
        Config.acting_character = None
        Config.scout_active = False
        Config.gold_count = 50
        self.party_exp = 0
        self.exp_reward = 0
        self.aura_bonus_speed = 0
        self.aura_bonus_damage = 0
        self.aura_bonus_armor = 0
        self.bosses_defeated = 0
        self.simulation_sprites.empty()
        self.help_sprites.empty()
        

    def startup(self):
        self.simulation_hero_sprites = pg.sprite.Group()
        self.simulation_sprites = pg.sprite.Group()
        self.simulation_monster_sprites = pg.sprite.Group()
        self.help_sprites = pg.sprite.Group()
        self.party_exp = 0
        self.exp_reward = 0
        self.bosses_defeated = 0
        self.party_size = 3
        self.simu_paths = []
        self.names_df = get_data('names')
        self.talent_lists = get_data('talents')
        self.COUNT = 5
        self.results_list = []
        self.sim_done = False
        self.aura_bonus_speed = 0
        self.aura_bonus_damage = 0
        self.aura_bonus_armor = 0

        FONT_NAME = 'Arial'
        COORDS_START = (self.screen_width * 0.50, self.screen_height * 0.40)
        COORDS_DONE = (self.screen_width * 0.50, self.screen_height * 0.50)
        START = 'Start'
        DONE = 'Done'

        self.start_button = Button(self.simulation_sprites, START, FONT_NAME, self.big_font_size, self.black, COORDS_START)
        self.done_button = Button(self.help_sprites, DONE, FONT_NAME, self.medium_font_size, self.black, COORDS_DONE)

        info = 'Simulation is running'
        self.info_text = self.info_font.render(info, True, self.black)
        self.info_text_rect = self.info_text.get_rect(center=COORDS_DONE)
        
    def reset_variables(self):
        self.party = []
        Config.party_heroes = []
        Config.current_adventure = None
        Config.completed_adventures = []
        Config.party_backpack = {}
        Config.party_followers = []
        Config.backpack_slots = []
        Config.equipment_slots = []
        self.simu_paths = []
        self.fallen_heroes = []
        self.sim_loc_df = None
        self.party_exp = 0 
        self.exp_reward = 0
        self.bosses_defeated = 0
        self.simulation_monster_sprites.empty()
        self.simulation_hero_sprites.empty()
        self.aura_bonus_speed = 0
        self.aura_bonus_damage = 0
        self.aura_bonus_armor = 0
        #missing variables that need to reset
    
    def navigate_path(self, start_node):
        random_path = [start_node]
        current_node = start_node
        #correct condition? not 'node13_1'?
        #cause of infinite loop?
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
        
        #encapsulate
        for created_hero in Config.party_heroes:
            created_hero.equip_starting_weapon()
            
            if created_hero.type == 'wizard':
                wizard_df = (get_talent_data('wizard'))
                wizard_spells = wizard_df[(wizard_df['type'] == 'spell') & (wizard_df['min_level'] == 1)]
                random_row = wizard_spells.sample(n=1)
                talent_name = random_row['name'].iloc[0]  
                talent_type = 'spell'
                created_hero.add_talent(talent_name, talent_type)

            if created_hero.type == 'bard':
                bard_df = (get_talent_data('bard'))
                bard_songs = bard_df[(bard_df['type'] == 'song') & (bard_df['min_level'] == 1)]
                random_row = bard_songs.sample(n=1)
                talent_name = random_row['name'].iloc[0]  
                talent_type = 'song'
                created_hero.add_talent(talent_name, talent_type)
        adventure_df = get_data('adventures')
        adventure_list = adventure_df['name'].tolist()
        simulation_results.append(self.party)

        for adventure in adventure_list:
            Config.current_adventure = adventure
            world_instance = WorldMap()
            self.sim_loc_df = world_instance.generate_random_path(Config.current_adventure)
            start_loc_df = self.sim_loc_df[self.sim_loc_df['parent1'].isna()].copy()
            start_loc_list = start_loc_df['name'].tolist()
            start_loc = random.choice(start_loc_list)

            simulated_path = self.navigate_path(start_loc)
            simulated_monsters = []
        
            #simulation_results.append(simulated_path)
            #talent_dicts = {}
            #for p in range(self.party_size):
            #    talent_dicts[simulation_results[1][p][0]] = []
            #simulation_results.append(talent_dicts)

            monsters = []
            path_instance = Path()
            for location in simulated_path:
                row = self.sim_loc_df[self.sim_loc_df['name'] == location].iloc[0]
                #skipping over shopping for now
                if row['type'] == 'shop':
                    pass
                else:
                    tier = int(row['tier'])
                    monsters = path_instance.create_encounter(tier)
                    simulated_monsters.append(monsters)
        #take first monster list in simulated_monsters and loop battle
        #rooms_done += 1 to count final room
            for monster_list in simulated_monsters:
                Config.room_monsters = monster_list
                #monster objects
                monster_count = len(Config.room_monsters)
                monster_names = Config.room_monsters
                Config.room_monsters = []
                BattleManager().create_monsters(monster_count, monster_names) 

                self.actions_unordered = []
                
                for room_monster in Config.room_monsters:
                    self.actions_unordered.append(room_monster)
                for party_hero in Config.party_heroes:
                    self.actions_unordered.append(party_hero)
                for follower in Config.party_followers:
                    self.actions_unordered.append(follower)

                for activation_hero in Config.party_heroes:
                    activation_hero.activate_talent_group('location')
                    activation_hero.activate_item_stats()
                    #activation_hero.acticate_item_effects()
                    activation_hero.activate_aura()

                self.actions_ordered = BattleManager().order_sort(self.actions_unordered)
                self.fallen_heroes = []

                while Config.party_heroes and Config.room_monsters: #loop combat 
                    Config.acting_character = self.actions_ordered[0] 
                    if not Config.acting_character.is_monster:
                        if Config.acting_character.attack_type == 'spell':
                            Config.acting_character.activate_talent_group('combat')
                            Config.acting_character.spell_attack(Config.acting_character.evaluate_spells())
                        elif Config.acting_character.attack_type == 'song':
                            Config.acting_character.activate_talent_group('song')
                            Config.acting_character.song_attack()
                        else:
                            Config.acting_character.activate_talent_group('combat')
                            Config.acting_character.melee_attack()

                        for fighting_monster in Config.room_monsters:
                            if fighting_monster.health <=0:
                                self.actions_ordered.remove(fighting_monster)
                                self.exp_reward += fighting_monster.exp
                                Config.room_monsters.remove(fighting_monster)

                    elif Config.acting_character.is_monster:
                    #elif not Config.acting_character.is_player and not Config.acting_character.is_follower:
                        Config.acting_character.melee_attack()
                        for fighting_hero in Config.party_heroes:
                            if fighting_hero.health <=0:
                                self.actions_ordered.remove(fighting_hero)
                                Config.party_heroes.remove(fighting_hero)
                                self.fallen_heroes.append(fighting_hero)
                                #revive fallen hero for next node

                    self.actions_ordered.append(self.actions_ordered.pop(0))

                Config.aura_bonus = {key: 0 for key in Config.aura_bonus}
                for map_talent_hero in Config.party_heroes:
                    map_talent_hero.activate_talent_group('map')

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
                        #simulation_results[2][hero.name].append(talent_name)
            if Config.party_heroes:
                Config.completed_adventures.append(Config.current_adventure)
                self.bosses_defeated += 1
            else:
                break

        simulation_results.append(self.exp_reward)
        simulation_results.append(self.bosses_defeated)
        self.reset_variables() #cleanup 
        return simulation_results 

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.start_button.rect.collidepoint(mouse_pos):
                self.sim_done = False
                play_sound_effect('click')
                for _ in range(self.COUNT):
                    result = self.run_simulation()
                    print(result)
                    self.results_list.append(result)
                    self.screen.blit(self.info_text, self.info_text_rect)

                columns = ['heroes', 'exp', 'bosses']
                results_df = pd.DataFrame(self.results_list, columns=columns)
                
                for _, row in results_df.iterrows():
                    enter_simulation_result(row)
                self.sim_done = True

            elif self.done_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.sim_done = False

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        screen.fill(self.grey)
        #display simulation results

        self.simulation_sprites.draw(self.screen)

        if self.sim_done:
            self.help_sprites.draw(self.screen)
