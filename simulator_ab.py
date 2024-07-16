"""
Simulator Module.

This module contains the Simulator and DummyLocation classes.

The Simulator class runs a set number of game simulations with random choices, 
gathers data for analysis, and serves as an automated testing tool to identify 
potential outliers in the game.

The DummyLocation class creates dummy objects needed for the the simulator.

Classes:
    Simulator: Runs game simulations and collects data for analysis and testing.
    DummyLocation: Creates dummy objects for use in simulations.
"""

import pygame as pg
import pandas as pd
import random
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Button
from data_ab import get_data, enter_simulation_result, get_talent_data, get_monster_encounters, get_monster_sim_stats, update_monster_sim_stats
from battle_ab import BattleManager
from sounds_ab import play_sound_effect
from path_ab import Path
from overworld_ab import WorldMap
from levelup_ab import LevelUp
from items_ab import ItemManager
from talents_ab import TalentsManager
import json

class Simulator(Config):
    """Runs game simulations with random choices and gathers data for analysis."""

    def __init__(self):
        """Initialize simulator with default settings and set next state to 'menu'."""
        super().__init__()
        self.next = 'menu'

    def cleanup(self):
        """Reset class-specific and global variables and clear associated sprites."""
        self.party = []
        self.results_list = []
        self.simu_paths = []
        self.item_loot = []
        self.fallen_heroes = []
        self.monster_stats = []
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
        self.target = None
        Config.gold_count = 50
        self.party_exp = 0
        self.exp_reward = 0
        self.aura_bonus_speed = 0
        self.aura_bonus_damage = 0
        self.aura_bonus_armor = 0
        self.bosses_defeated = 0
        self.gold_loot = 0
        self.simulation_sprites.empty()
        self.help_sprites.empty()
        
    def startup(self):
        """Initialize resources and set up the simulator state."""
        self.simulation_hero_sprites = pg.sprite.Group()
        self.simulation_sprites = pg.sprite.Group()
        self.simulation_monster_sprites = pg.sprite.Group()
        self.help_sprites = pg.sprite.Group()
        self.party_exp = 0
        self.exp_reward = 0
        self.bosses_defeated = 0
        #self.party_size = 3
        self.simu_paths = []
        self.names_df = get_data('names')
        self.talent_lists = get_data('talents')
        self.COUNT = 1
        self.results_list = []
        self.sim_done = False
        self.aura_bonus_speed = 0
        self.aura_bonus_damage = 0
        self.aura_bonus_armor = 0
        self.target = None

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
        """Reset various variables to their default or empty states between simulation runs."""
        self.party = []
        Config.party_heroes = []
        Config.current_adventure = None
        Config.completed_adventures = []
        Config.party_backpack = {}
        Config.party_followers = []
        Config.backpack_slots = []
        Config.equipment_slots = []
        Config.combat_log = []
        Config.gold_count = 50
        Config.current_location = None
        self.simu_paths = []
        self.fallen_heroes = []
        self.item_loot = []
        self.monster_stats = []
        self.sim_loc_df = None
        self.target = None
        self.party_exp = 0 
        self.exp_reward = 0
        self.bosses_defeated = 0
        self.simulation_monster_sprites.empty()
        self.simulation_hero_sprites.empty()
        self.aura_bonus_speed = 0
        self.aura_bonus_damage = 0
        self.aura_bonus_armor = 0
        self.gold_loot = 0
    
    def navigate_path(self, start_node):
        """Return a random route from start_node to 'cave' as a list."""
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
        """Return a list of monsters for an encounter based on the adventure tier."""
        loc_tier = tier
        adv = Config.current_adventure 
        encounters_df = get_monster_encounters(adv, tier)
        probs = encounters_df['Probability'].tolist()
        mob_lists = encounters_df.apply(lambda row: [value for value in row[4:].tolist() if value is not None], axis=1).tolist()
        encounter = random.choices(mob_lists, weights=probs, k=1)[0]
        return encounter

    def smallest_mod(self, slot):
        """Return the hero with the smallest item modifier tier and the tier value."""
        small_tier = 18 #max tier 17
        small_hero = None
        for hero in Config.party_heroes:
            if hero.worn_items[slot] is not None:
                current_modifier_tier = hero.worn_items[slot].modifier_tier

                if current_modifier_tier < small_tier:
                    small_tier = current_modifier_tier
                    small_hero = hero
        return small_hero, small_tier

    def smart_equip_item(self, new_item):
        """Equip an item to the hero with the smallest modifier tier for the item's slot."""
        for smart_hero in Config.party_heroes:
            for item_slot, item in smart_hero.worn_items.items():
                if item is None and new_item.slot_type == item_slot:
                    smart_hero.equip_item(new_item)
                    return

        new_item_slot = new_item.slot_type
        equip_hero, tier = self.smallest_mod(new_item_slot)
        if equip_hero:
            if equip_hero.worn_items[new_item_slot].modifier_tier < tier:
                equip_hero.drop_item(slot_to_drop)
                equip_hero.equip_item(new_item)
        #handle book

    def run_simulation(self): 
        """Run a full game simulation until heroes are defeated or complete all adventures."""
        simulation_results = []
        self.names = [tuple(row) for row in self.names_df[['name', 'type']].values]
        selection = random.sample(self.names, 8)
        self.party = random.sample(selection, 3)

        monster_df = get_data('monsters')
        monster_name_list = monster_df['name'].tolist()
        stats_columns = ['dam_in', 'dam_out', 'count']
        self.monster_stats = {}
        for data_monster in monster_name_list:
            self.monster_stats[data_monster] = {column: 0 for column in stats_columns}

        for simulated_hero in range(self.max_party_size):
            SIMU_X = 0
            SIMU_Y = 0
            self.simulated_hero = Hero(self.simulation_hero_sprites, (SIMU_X, SIMU_Y), self.party[simulated_hero][0], self.party[simulated_hero][1])
            Config.party_heroes.append(self.simulated_hero)
            self.simulation_hero_sprites.add(self.simulated_hero)
        
        simulation_results.append(self.party)
        talent_dict = {}
        for name_hero in Config.party_heroes:
            talent_dict[name_hero.name] = []
        simulation_results.append(talent_dict)

        for created_hero in Config.party_heroes:
            created_hero.equip_starting_weapon()

            if created_hero.type == 'wizard':
                wizard_df = (get_talent_data('wizard'))
                wizard_spells = wizard_df[(wizard_df['type'] == 'spell') & (wizard_df['min_level'] == 1)]
                random_row = wizard_spells.sample(n=1)
                talent_name = random_row['name'].iloc[0]  
                talent_type = 'spell'
                TalentsManager.add_talent(talent_name, talent_type, created_hero)
                simulation_results[1][created_hero.name].append(talent_name)   

            if created_hero.type == 'bard':
                talent_type = 'song'
                talent_name = 'Loud Tune'
                TalentsManager.add_talent(talent_name, talent_type, created_hero)
                simulation_results[1][created_hero.name].append(talent_name)  

        adventure_df = get_data('adventures')
        adventure_list = adventure_df['name'].tolist()
        Config.current_location = DummyLocation(1)

        for adventure in adventure_list:
            Config.current_adventure = adventure
            world_instance = WorldMap()
            self.sim_loc_df = world_instance.generate_random_path(Config.current_adventure)
            start_loc_df = self.sim_loc_df[self.sim_loc_df['parent1'].isna()].copy()
            start_loc_list = start_loc_df['name'].tolist()
            start_loc = random.choice(start_loc_list)

            simulated_path = self.navigate_path(start_loc)
            simulated_locations = []
            Config.combat_log = []
            monsters = []
            path_instance = Path()

            #encapsulate
            for location in simulated_path:
                row = self.sim_loc_df[self.sim_loc_df['name'] == location].iloc[0]
                #skipping over shopping for now
                if row['type'] == 'shop':
                    pass
                    #create item selection
                    #buy random item if enough gold
                    #equip_item()
                else:
                    tier = int(row['tier'])
                    monsters = path_instance.create_encounter(tier)

                    loc_entry = (monsters, tier)
                    simulated_locations.append(loc_entry)

        #take first monster list in simulated_locations and loop battle
            for entry in simulated_locations:
                if not Config.party_heroes:
                    break
                #if list_item == 'shop':
                #do shopping
                #else:

                Config.room_monsters = entry[0]
                location_tier = entry[1]
                Config.current_location.tier = location_tier

                #monster objects
                monster_count = len(Config.room_monsters)
                monster_names = Config.room_monsters
                Config.room_monsters = []
                BattleManager().create_monsters(monster_count, monster_names) 

                #create loot           
                self.gold_loot = BattleManager().create_gold_loot()
                self.item_loot = ItemManager.create_item_loot()

                self.actions_unordered = []
                
                for room_monster in Config.room_monsters:
                    self.actions_unordered.append(room_monster)
                    self.monster_stats[room_monster.name]['count'] += 1
                for party_hero in Config.party_heroes:
                    self.actions_unordered.append(party_hero)
                for follower in Config.party_followers:
                    self.actions_unordered.append(follower)

                for activation_hero in Config.party_heroes:
                    activation_hero.activate_talent_group('location')
                    activation_hero.activate_item_stats()
                    activation_hero.activate_aura()

                self.actions_ordered = BattleManager().order_sort(self.actions_unordered)
                self.fallen_heroes = []

                combat_rounds = 0
                while Config.party_heroes and Config.room_monsters: #loop combat 
                    combat_rounds += 1
                    if combat_rounds > 750:
                        print(self.exp_reward, simulation_results[0], Config.room_monsters[0].name, len(Config.room_monsters))
                        error_talents = simulation_results[1]
                        filename = './ab_data/json_data/sim_error.json'
                        with open(filename, 'w') as json_file:
                            json.dump(error_talents, json_file, indent=4)
                        exit()

                    Config.acting_character = self.actions_ordered[0] 
                    self.target = Config.acting_character.get_target()
                    start_health = self.target.health

                    if not Config.acting_character.is_monster:
                        if Config.acting_character.attack_type == 'spell':
                            Config.acting_character.activate_talent_group('combat')
                            Config.acting_character.spell_attack(Config.acting_character.evaluate_spells(), self.target)
                        elif Config.acting_character.attack_type == 'song':
                            Config.acting_character.activate_talent_group('song')
                            Config.acting_character.song_attack()
                        else:
                            Config.acting_character.activate_talent_group('combat')
                            Config.acting_character.melee_attack(self.target)

                        damage_in = start_health - self.target.health
                        if damage_in > 0:
                            self.monster_stats[self.target.name]['dam_in'] += int(damage_in)

                        for fighting_monster in Config.room_monsters:
                            if fighting_monster.health <=0:
                                self.actions_ordered.remove(fighting_monster)
                                self.exp_reward += fighting_monster.exp
                                Config.room_monsters.remove(fighting_monster)

                    elif Config.acting_character.is_monster:
                    #elif not Config.acting_character.is_player and not Config.acting_character.is_follower:
                        Config.acting_character.melee_attack(self.target)

                        damage_out = start_health - self.target.health
                        if damage_out > 0:
                            self.monster_stats[Config.acting_character.name]['dam_out'] += int(damage_out)

                        for fighting_hero in Config.party_heroes:
                            if fighting_hero.health <=0:
                                self.actions_ordered.remove(fighting_hero)
                                Config.party_heroes.remove(fighting_hero)
                                self.fallen_heroes.append(fighting_hero)
                                #revive fallen hero for next node
                        Config.combat_log = []
                    self.target = None
                    self.actions_ordered.append(self.actions_ordered.pop(0))

                #encapsulate combat cleanup
                #disable for hardcore mode
                if Config.party_heroes:
                    if self.fallen_heroes:
                        for reviving_hero in self.fallen_heroes:
                            Config.party_heroes.append(reviving_hero)
                            reviving_hero.health = reviving_hero.max_health // Config.revive_divisor
                    self.fallen_heroes = []

                Config.aura_bonus = {key: 0 for key in Config.aura_bonus}
                for map_talent_hero in Config.party_heroes:
                    map_talent_hero.activate_talent_group('map')

                for found_item in self.item_loot:
                    self.smart_equip_item(found_item)
                self.item_loot = []
                Config.gold_count += self.gold_loot
                self.gold_loot = 0

                levelup_instance = LevelUp()

                if Config.party_heroes and self.exp_reward + Config.party_heroes[0].exp >= Config.party_heroes[0].next_level:
                    for leveling_hero in Config.party_heroes:
                        levelup_instance.gain_level(leveling_hero)

                    samples = []
                    self.numer_of_heroes = len(Config.party_heroes)
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
                        
                        TalentsManager.add_talent(talent_name, talent_type, hero)
                        simulation_results[1][hero.name].append(talent_name)

            if Config.party_heroes:
                Config.completed_adventures.append(Config.current_adventure)
                self.bosses_defeated += 1
            else:
                break

        simulation_results.append(self.exp_reward)
        simulation_results.append(self.bosses_defeated)

        update_df = pd.DataFrame.from_dict(self.monster_stats, orient='index')
        self.monster_stats = []
        old_df = get_monster_sim_stats()
        result_df = old_df.add(update_df, fill_value=0)
        update_monster_sim_stats(result_df)

        #for item_hero in Config.party_heroes:
        #    item_list = [item.desc for item in item_hero.worn_items.values() if item is not None]
        #    item_str = ' '.join(desc_list)
        self.reset_variables() 
        return simulation_results 

    def get_event(self, event):
        """Handle user input events for the simulator state."""
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
                    talent_dict = result[1]
                    del result[1]

                    for i in range(self.max_party_size):
                        talents = talent_dict[result[0][i][0]]
                        result.append(talents)

                    columns = ['heroes', 'exp', 'bosses', 'talents1', 'talents2', 'talents3']
                    result_df = pd.DataFrame([result], columns=columns)
                    for _, row in result_df.iterrows():
                        enter_simulation_result(row)

                self.sim_done = True

            elif self.done_button.rect.collidepoint(mouse_pos):
                play_sound_effect('click')
                self.sim_done = False

    def update(self, screen, dt):
        """Update the simulator state based on game events."""
        self.draw(screen)

    def draw(self, screen):
        """Draw the simulator state to the screen."""
        screen.fill(self.grey)
        self.simulation_sprites.draw(self.screen)
        if self.sim_done:
            self.help_sprites.draw(self.screen)

class DummyLocation(Config):
    """Creates dummy objects needed for the simulator's operation."""
    
    def __init__(self, tier):
        """Initialize dummylocation with default settings."""
        super().__init__()
        self.tier = tier
