"""
Battle module for managing combat between heroes and monsters.

This module contains the BattleManager class, which handles the combat mechanics, 
processes hero and monster actions, and manages the end-game conditions.
"""

import pygame as pg
from config_ab import Config
from sprites_ab import Monster, Equipment
from animations_ab import Stab, Blast, Smash, SongAnimation, FollowerAttack, MonsterStab, get_animation_speed
from sounds_ab import play_sound_effect
from data_ab import get_json_data, get_affix
from items_ab import ItemManager
import random
import pygame.mixer

class BattleManager(Config):
    """
    Manages combat between heroes and monsters.

    This class handles the combat mechanics, processes actions of both heroes and monsters, 
    and manages scenarios where all heroes are defeated, resulting in the end of the game.
    """

    def __init__(self):
        super().__init__()
        """Initialize battlemanager with default settings and set next state to 'path'."""
        self.next = 'path' 
        self.actions_unordered = []
        self.defeated_heroes = []
        self.combat_hero_sprites = pg.sprite.Group()
        self.combat_mob_sprites = pg.sprite.Group()
        #self.animation_sprites = pg.sprite.Group()
        self.animation_sprites = pg.sprite.GroupSingle()
        #self.follower_sprites = pg.sprite.GroupSingle()
        self.exp_reward = 0
        self.combat_delay = 1.1
    
    def cleanup(self):
        """
        Reset class-specific variables and clear associated sprites.

        This includes emptying sprite groups, resetting item loot, updating hero states, 
        and handling game state transitions such as resetting the game if the party is 
        defeated or all adventures are completed. If at least one hero survives, 
        defeated heroes are healed to half health and added back to the party.
        """
        self.animation_sprites.empty()
        self.combat_hero_sprites.empty()
        self.combat_mob_sprites.empty()
        #self.follower_sprites.empty()
        self.actions_unordered = []
        Config.room_monsters = []
        Config.combat_log = []
        self.current_target = None
        for loot_item in self.item_loot:
            ItemManager.item_to_backpack(loot_item)
            #handle backpack overflow

        self.item_loot = []
        Config.gold_count += self.gold_loot

        if not self.party_defeated:
            for risen_hero in self.defeated_heroes:
                Config.party_heroes.append(risen_hero)
                risen_hero.health = risen_hero.max_health // Config.revive_divisor
        self.defeated_heroes = []

        for cleanup_hero in Config.party_heroes:
            cleanup_hero.exp += self.exp_reward
            cleanup_hero.item_stats_dict = {item_key: 0 for item_key in cleanup_hero.item_stats_dict}

        self.exp_reward = 0
        self.gold_loot = 0
        self.combat_started = False
        self.delay_timer = 0.0
        Config.aura_bonus = {aura_key: 0 for aura_key in Config.aura_bonus}
        if self.party_defeated or len(Config.completed_adventures) == Config.number_of_adventures:
            self.reset_game()
    
    def create_gold_loot(self):
        """Return amount of gold awarded by location monsters."""
        total_min_gold = 0
        total_max_gold = 0
        for loot_monster in Config.room_monsters:
            total_min_gold += loot_monster.gold_min
            total_max_gold += loot_monster.gold_max
        total_loot = random.randint(total_min_gold, total_max_gold)
        return total_loot
    
    def reset_game(self):
        """Reset the game state to its initial values."""
        Config.party_backpack = {}
        self.defeated_heroes = []
        Config.party_heroes = []
        Config.backpack_slots = []
        Config.party_followers = [] 
        Config.equipment_slots = []
        Config.generated_path = []
        Config.completed_adventures = []
        Config.current_adventure = None
        Config.current_location = None
        Config.acting_character = None
        self.current_target = None
        Config.gold_count = 50
        Config.party_discount = 0
        Config.magic_find = 0
        Config.scout_active = False
        Config.map_next = False
        self.party_defeated = False

    #move to Config?
    def position_heroes(self):
        """Position hero objects."""
        HEROPOS_X = (self.screen_width * 0.3)
        HEROPOS_Y = (self.screen_height * 0.6)
        HERO_GAP = (self.screen_width * 0.2)
        for spot_hero in Config.party_heroes:
           spot_hero.rect = spot_hero.image.get_rect(topleft = (HEROPOS_X, HEROPOS_Y)) 
           spot_hero.pos_x = HEROPOS_X
           spot_hero.pos_y = HEROPOS_Y
           HEROPOS_X += HERO_GAP
    
    def create_monsters(self, monster_count, monster_names):
        """Create and position monster objects."""
        y = 0.2
        pos_y = self.screen_height * y
        monster_x_coords = [(i + 1) / (monster_count + 1) for i in range(monster_count)]

        for j, x in enumerate(monster_x_coords):
            pos_x = self.screen_width * x
            monster = Monster(self.monster_sprites, (pos_x, pos_y), monster_names[j])
            Config.room_monsters.append(monster)

    def order_sort(self, incombat: list):
        """Return a list of combat participants sorted by speed."""
        def speed_order(battle_participant: object):
            participant_speed = battle_participant.total_stat('speed')
            return participant_speed
        # Sort participants by speed in descending order.
        # Tie breaker: first in hero/mob list > lower, hero > mob, class.
        return sorted(incombat, key=speed_order, reverse=True)
    
    def startup(self):
        """Initialize resources and set up the battlemanager state."""
        self.party_defeated = False
        if Config.current_location.type == 'boss' and Config.current_adventure == 'dark_forest':
            play_sound_effect(Config.current_location.name)
        self.combat_started = False
        self.delay_timer = 0.0
        self.current_target = None

        self.position_heroes()
        monster_count = len(Config.room_monsters)
        monster_names = Config.room_monsters
        Config.room_monsters = []
        self.create_monsters(monster_count, monster_names)

        for room_monster in Config.room_monsters:
            self.combat_mob_sprites.add(room_monster)
            self.actions_unordered.append(room_monster)
        for party_hero in Config.party_heroes:
            self.combat_hero_sprites.add(party_hero)
            self.actions_unordered.append(party_hero)
        for follower in Config.party_followers:
            self.actions_unordered.append(follower)

        #group in activation function
        for activation_hero in Config.party_heroes:
            activation_hero.activate_talent_group('location')
            activation_hero.activate_item_stats()
            #activation_hero.acticate_item_effects()
            activation_hero.activate_aura()

        self.gold_loot = self.create_gold_loot()
        self.item_loot = ItemManager.create_item_loot()

        self.actions_ordered = self.order_sort(self.actions_unordered)
        Config.acting_character = self.actions_ordered[0]

    def get_event(self, event):
        """Handle user input events for the battlemanager state."""
        if event.type == pg.KEYDOWN:
            if not Config.room_monsters:
                if Config.current_location.type == 'boss':
                    pg.mixer.stop()
                    Config.completed_adventures.append(Config.current_adventure)
                    Config.current_location = None

                    if self.exp_reward == 0:
                        self.next = 'menu'
                        self.done = True
                        
                    elif self.next == 'levelup':
                        Config.map_next = True
                    else:
                        self.next = 'map'
                self.done = True
            if not Config.party_heroes:
                pg.mixer.stop()
                self.party_defeated = True
                self.next = 'menu'
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            pass

    def update(self, screen, dt):
        """
        Update the battle manager state based on game events.

        Combat is fully automated. This method processes the current action, executes 
        attack animations, applies attack effects, and checks for battle outcomes.
        """
        if not self.combat_started:
            if self.delay_timer >= self.combat_delay:
                self.combat_started = True
            else:
                self.delay_timer += dt
                self.draw(screen)
                return

        Config.acting_character = self.actions_ordered[0]
        # Attack animation has not started and both monster and hero lists have list items
        if not Config.acting_character.animation and Config.room_monsters and Config.party_heroes: 
            self.current_target = Config.acting_character.get_target()
            if Config.acting_character.is_player:
                pos_x = Config.acting_character.pos_x
                pos_y = Config.acting_character.pos_y
                
                if Config.acting_character.attack_type == 'spell':
                    Config.acting_character.active_spell = Config.acting_character.evaluate_spells()
                    self.combat_animation = Blast(self.animation_sprites, Config.acting_character.active_spell, pos_x, pos_y)
                
                elif Config.acting_character.attack_type == 'song':
                    play_sound_effect('tune')
                    self.combat_animation = SongAnimation(self.animation_sprites, pos_x, pos_y)
                else:
                    play_sound_effect('sword')
                    if Config.acting_character.worn_items['hand1'] == None:
                        held_weapon = 'unarmed'
                    else:
                        held_weapon = Config.acting_character.worn_items['hand1'].item_name
                    self.combat_animation = Stab(self.animation_sprites, held_weapon, pos_x, pos_y)

            elif Config.acting_character.is_follower:
                play_sound_effect(Config.acting_character.type)
                pos_x = Config.acting_character.following.pos_x
                pos_y = Config.acting_character.following.pos_y
                self.combat_animation = FollowerAttack(self.animation_sprites, Config.acting_character, pos_x, pos_y)

            elif not Config.acting_character.is_player and not Config.acting_character.is_follower:
                if Config.acting_character.sound:
                    play_sound_effect(Config.acting_character.sound)

                bottomright_x, bottomright_y = Config.acting_character.rect.bottomright

                if Config.acting_character.weapon:
                    held_weapon = Config.acting_character.weapon
                    #get Config.acting_character action
                    #animation = MonsterAction
                    #action replaces melee_attack in monster attack
                    self.combat_animation = MonsterStab(self.animation_sprites, held_weapon, bottomright_x, bottomright_y)
                else:
                    self.combat_animation = Smash(self.animation_sprites, bottomright_x, bottomright_y)
                
            Config.acting_character.animation = True
            self.combat_animation.animation_start()

        # Call attack methods 
        if self.combat_animation.animate(get_animation_speed()):
            if Config.acting_character.is_player:
                Config.acting_character.activate_item_effects()
            if Config.acting_character.attack_type == 'spell':
                Config.acting_character.activate_talent_group('combat')
                Config.acting_character.spell_attack(Config.acting_character.active_spell, self.current_target)
            elif Config.acting_character.attack_type == 'song':
                Config.acting_character.activate_talent_group('song')
                Config.acting_character.song_attack()
            else:
                if Config.acting_character.is_player:
                    Config.acting_character.activate_talent_group('combat')
                    Config.acting_character.melee_attack(self.current_target)
                elif Config.acting_character.is_follower:
                    Config.acting_character.melee_attack(self.current_target)
                else: #monster attack
                    Config.acting_character.melee_attack(self.current_target)


            #self.animation_sprites.remove(self.combat_animation)
            self.actions_ordered.append(self.actions_ordered.pop(0))
            
            #if not Config.acting_character.is_monster:
            if Config.acting_character.is_player or Config.acting_character.is_follower:
                for fighting_monster in Config.room_monsters:
                    #def monster_defeated(self):
                    #call function after activating location talents, fix for ambush / smite
                    if fighting_monster.health <=0:
                        self.combat_mob_sprites.remove(fighting_monster)
                        self.actions_ordered.remove(fighting_monster)
                        self.exp_reward += fighting_monster.exp
                        if self.exp_reward + Config.party_heroes[0].exp >= Config.party_heroes[0].next_level:
                            self.next = 'levelup'
                        else:
                            self.next = 'path'
                        Config.room_monsters.remove(fighting_monster)
                        if not Config.room_monsters:
                            play_sound_effect('victory')
                            self.victory_lines = [
                            f'Experience earned: {self.exp_reward}',
                            f'Gold coins earner: {self.gold_loot}',
                            f'Found {len(self.item_loot)} items',
                            'Press any key to continue']

            #elif Config.acting_character.is_monster:
            elif not Config.acting_character.is_player and not Config.acting_character.is_follower:  
                for fighting_hero in Config.party_heroes:
                    if fighting_hero.health <=0:
                        self.combat_hero_sprites.remove(fighting_hero)
                        self.actions_ordered.remove(fighting_hero)
                        Config.party_heroes.remove(fighting_hero)
                        self.defeated_heroes.append(fighting_hero)
                        if not Config.party_heroes:
                            play_sound_effect('lose')
                            self.lose_lines = [
                            'Your heroes were defeated',
                            'Press any key to continue']

        self.draw(screen)

    def draw(self, screen):
        """Draw the battlemanager state to the screen."""
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.combat_hero_sprites.draw(self.screen)
        self.combat_mob_sprites.draw(self.screen)

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        for live_monster in Config.room_monsters:
            live_monster.draw_health_bar()

        for live_hero in Config.party_heroes:
            live_hero.display_name()
            live_hero.draw_health_bar()

        if Config.acting_character.animation: 
            self.animation_sprites.draw(self.screen)

        self.combat_log_events = Config.combat_log[-10:]
        COORDS_LOG = (self.screen_width * 0.02, self.screen_height * 0.60)
        for i, event in enumerate(reversed(self.combat_log_events)):
            log_line = '{} deals {:>4} to {}'.format(event[0].capitalize().ljust(15), event[1], event[2].capitalize())
            log_line_text = self.log_font.render(log_line, True, self.black)
            log_line_rect = log_line_text.get_rect(topleft=(COORDS_LOG[0], COORDS_LOG[1] + i * self.log_font_size))
            self.screen.blit(log_line_text, log_line_rect)

        if not self.combat_started:
            MONSTERS_NAMES = [monster.type.capitalize() for monster in Config.room_monsters]
            MONSTERS_TEXT = 'Enemies: ' + ', '.join(MONSTERS_NAMES)
            self.MONSTERS_TEXT = self.med_info_font.render(MONSTERS_TEXT, True, self.black)
            COORDS_MONSTERS_TEXT = (self.screen_width * 0.45, self.screen_height * 0.45)
            self.MONSTERS_RECT = self.MONSTERS_TEXT.get_rect(topleft=COORDS_MONSTERS_TEXT)

            self.screen.blit(self.MONSTERS_TEXT, self.MONSTERS_RECT)

        if not Config.room_monsters:
            VICTORY = 'Victory!'
            if self.exp_reward == 0:
                VICTORY = 'Game Complete!'
            VICTORY_TEXT = self.title_font.render(VICTORY, True, self.black)
            COORDS_VICTORY = (self.screen_width * 0.50, self.screen_height * 0.20)
            VICTORY_TEXT_RECT = VICTORY_TEXT.get_rect(center = COORDS_VICTORY)
            self.screen.blit(VICTORY_TEXT, VICTORY_TEXT_RECT)
            
            VICTORY_HEIGHT = VICTORY_TEXT.get_height() // 2
            COORDS_VIC = (self.screen_width * 0.50, self.screen_height * 0.35 + VICTORY_HEIGHT)

            for i, victory_line in enumerate(self.victory_lines):
                vic_line_text = self.info_font.render(victory_line, True, self.black)
                vic_line_rect = vic_line_text.get_rect(center=(COORDS_VIC[0], COORDS_VIC[1] + i * self.info_font_size))
                self.screen.blit(vic_line_text, vic_line_rect)

        if not Config.party_heroes:
            COORDS_LOSE = (self.screen_width * 0.50, self.screen_height * 0.40)

            for i, lose_line in enumerate(self.lose_lines):
                lose_line_text = self.info_font.render(lose_line, True, self.black)
                lose_line_rect = lose_line_text.get_rect(center=(COORDS_LOSE[0], COORDS_LOSE[1] + i * self.info_font_size))
                self.screen.blit(lose_line_text, lose_line_rect)
