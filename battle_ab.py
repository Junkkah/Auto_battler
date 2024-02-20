import pygame as pg
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Monster
from animations_ab import Stab, Slash, Blast, Smash, SongAnimation
from sounds_ab import sound_effect
import random

# Shop not resetting to hero selection if defeated in combat and going for new game

class BattleManager(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path' 
        self.actions_unordered = []
        self.defeated_heroes = []
        self.combat_hero_sprites = pg.sprite.Group()
        self.combat_mob_sprites = pg.sprite.Group()
        self.animation_sprites = pg.sprite.Group()
        self.exp_reward = 0
        #adjust in settings
        self.combat_delay = 1.1
        self.animation_speed = 0.3

    def create_loot(self):
        total_min_gold = 0
        total_max_gold = 0
        for loot_monster in Config.room_monsters:
            total_min_gold += loot_monster.gold_min
            total_max_gold += loot_monster.gold_max
        total_loot = random.randint(total_min_gold, total_max_gold)
        return total_loot
 
    def cleanup(self):
        self.animation_sprites.empty()
        self.combat_hero_sprites.empty()
        self.combat_mob_sprites.empty()
        self.actions_unordered = []
        self.temp_stats = []
        Config.room_monsters = []
        Config.gold_count += self.gold_loot

        for risen_hero in self.defeated_heroes:
            Config.party_heroes.append(risen_hero)
            risen_hero.health = risen_hero.max_health // 2
        self.defeated_heroes = []

        for cleanup_hero in Config.party_heroes:
            cleanup_hero.exp += self.exp_reward 
        self.exp_reward = 0
        self.gold_loot = 0
        self.combat_started = False
        self.delay_timer = 0.0

        Config.aura_bonus = {key: 0 for key in Config.aura_bonus}

    #hero method? get len(Config.party_heroes), check find self.name position in Config.party
    #for i in range len(S.party): S.party[i].get_into_position(i + 1) pos1,2,3,4
    def position_heroes(self, heroes: list):
        #adjust for variable hero count
        HEROPOS_X = (self.screen_width * 0.3)
        HEROPOS_Y = (self.screen_height * 0.6)
        HERO_GAP = (self.screen_width * 0.2)
        for spot_hero in Config.party_heroes:
           spot_hero.rect = spot_hero.image.get_rect(topleft = (HEROPOS_X, HEROPOS_Y)) 
           spot_hero.pos_x = HEROPOS_X
           spot_hero.pos_y = HEROPOS_Y
           HEROPOS_X += HERO_GAP

    def create_monsters(self):
        #define monster spots as function of n
        MONSTER_COUNT = len(Config.room_monsters)
        MONSTER_NAMES = []
        MONSTER_NAMES.extend(Config.room_monsters)
        MONSTERPOS_Y = self.screen_height * 0.2
        ONE_MONSTER_COORDS = (self.screen_width * 0.5, MONSTERPOS_Y)
        TWO_MONSTERS_COORDS = ((self.screen_width * 0.33, MONSTERPOS_Y), (self.screen_width * 0.66, MONSTERPOS_Y))
        THREE_MONSTERS_COORDS = ((self.screen_width * 0.25, MONSTERPOS_Y), (self.screen_width * 0.50, MONSTERPOS_Y), (self.screen_width * 0.75, MONSTERPOS_Y))

        if MONSTER_COUNT == 1:
            self.monster1 = Monster(self.monster_sprites, ONE_MONSTER_COORDS, MONSTER_NAMES[0]) 
            Config.room_monsters = [self.monster1]
        elif MONSTER_COUNT == 2:
            self.monster1 = Monster(self.monster_sprites, TWO_MONSTERS_COORDS[0], MONSTER_NAMES[0]) 
            self.monster2 = Monster(self.monster_sprites, TWO_MONSTERS_COORDS[1], MONSTER_NAMES[1])
            Config.room_monsters = [self.monster1, self.monster2]
        elif MONSTER_COUNT == 3:
            self.monster1 = Monster(self.monster_sprites, THREE_MONSTERS_COORDS[0], MONSTER_NAMES[0]) 
            self.monster2 = Monster(self.monster_sprites, THREE_MONSTERS_COORDS[1], MONSTER_NAMES[1])
            self.monster3 = Monster(self.monster_sprites, THREE_MONSTERS_COORDS[2], MONSTER_NAMES[2])
            Config.room_monsters = [self.monster1, self.monster2, self.monster3]

    def activate_auras(self):
        for aura_hero in Config.party_heroes:
            if aura_hero.aura:
                aura_stat_name, stat_val_str = aura_hero.aura.split()
                aura_stat_val = int(stat_val_str)
                Config.aura_bonus[aura_stat_name] += aura_stat_val

    #tie breaker, first in hero/mob list > lower, hero > mob, class prios
    def order_sort(self, incombat: list):
        def speed_order(battle_participant: object):
            if battle_participant.player:
                hero_speed = battle_participant.speed + Config.aura_bonus['speed']
                return hero_speed
            else:
                monster_speed = battle_participant.speed
                return monster_speed
        return sorted(incombat, key=speed_order, reverse=True)
    

    def startup(self):

        self.combat_started = False
        self.delay_timer = 0.0

        self.position_heroes(Config.party_heroes)
        self.create_monsters()

        for room_monster in Config.room_monsters:
            self.combat_mob_sprites.add(room_monster)
            self.actions_unordered.append(room_monster)
        for party_hero in Config.party_heroes:
            self.combat_hero_sprites.add(party_hero)
            self.actions_unordered.append(party_hero)

        for talent_hero in Config.party_heroes:
            talent_hero.activate_talent_group('location')

        self.activate_auras()
        self.gold_loot = self.create_loot()
        self.actions_ordered = self.order_sort(self.actions_unordered)
        Config.acting_character = self.actions_ordered[0]

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if not Config.room_monsters:
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            pass

    def update(self, screen, dt):

        if not self.combat_started:
            if self.delay_timer >= self.combat_delay:
                self.combat_started = True
            else:
                self.delay_timer += dt
                self.draw(screen)
                return

        Config.acting_character = self.actions_ordered[0]
        if not Config.acting_character.animation and Config.room_monsters: #animation hasn't started yet
            if Config.acting_character.player: #Attacker is hero
                pos_x = Config.acting_character.pos_x
                pos_y = Config.acting_character.pos_y

                #Need evaluate method
                #hero always cast index 0 spell in self.spells
                #create hero method for choosing spell to cast
                #play sound_effect based on spell type
                if Config.acting_character.attack_type == 'spell':
                    self.combat_animation = Blast(self.animation_sprites, pos_x, pos_y, Config.acting_character.spells[0])
                
                elif Config.acting_character.attack_type == 'song':
                    #sound_effect('tune')
                    #self.combat_animation = SongAnimation(self.animation_sprites, pos_x, pos_y)
                    pass
                else:
                    sound_effect('sword')
                    weapon = Config.acting_character.attack_type
                    self.combat_animation = Stab(self.animation_sprites, weapon, pos_x, pos_y)

            elif not Config.acting_character.player:
                if Config.acting_character.type == 'kobold' or Config.acting_character.type == 'goblin':
                    sound_effect('growl')
                adjusted_pos_x = Config.acting_character.pos_x + Config.acting_character.width
                adjusted_pos_y = Config.acting_character.pos_y + Config.acting_character.height
                self.combat_animation = Smash(self.animation_sprites, adjusted_pos_x, adjusted_pos_y)
                
            else:
                pass
            Config.acting_character.animation = True
            self.combat_animation.animation_start()

        # Call attack methods 
        #call activate talents here
        if self.combat_animation.animate(self.animation_speed):
            if Config.acting_character.attack_type == 'spell':
                #Config.acting_character.activate_combat_talents()
                Config.acting_character.spell_attack(Config.acting_character.spells[0])
            else:
                if Config.acting_character.player:
                    #Config.acting_character.activate_combat_talents()
                    Config.acting_character.melee_attack()
                else:
                    Config.acting_character.melee_attack()
            
            self.animation_sprites.remove(self.combat_animation)
            self.actions_ordered.append(self.actions_ordered.pop(0))
            
            if Config.acting_character.player:
                for fighting_monster in Config.room_monsters:
                    if fighting_monster.health <=0:
                        self.combat_mob_sprites.remove(fighting_monster)
                        self.actions_ordered.remove(fighting_monster)
                        self.exp_reward += fighting_monster.exp
                        if self.exp_reward + Config.party_heroes[0].exp >= Config.party_heroes[0].next_level:
                            self.next = 'levelup' #problem if level up from last node?
                        else:
                            self.next = 'path'
                        Config.room_monsters.remove(fighting_monster)
                        if not Config.room_monsters:
                            sound_effect('victory')
                            self.victory_lines = [
                            f'Experience earned: {self.exp_reward}',
                            f'Gold coins earner: {self.gold_loot}',
                            'Press any key to continue']
                            #self.done = True

            elif not Config.acting_character.player:  
                for fighting_hero in Config.party_heroes:
                    if fighting_hero.health <=0:
                        self.combat_hero_sprites.remove(fighting_hero)
                        self.actions_ordered.remove(fighting_hero)
                        Config.party_heroes.remove(fighting_hero)
                        self.defeated_heroes.append(fighting_hero)
                        if not Config.party_heroes: #do loss screen
                            Config.current_location = None
                            self.next = 'menu'
                            self.done = True
        
        #define lastest action text
        #action_log1,2,3
        #if latest action not action1-2 is 3, 1 is 2, latest is 1
        self.draw(screen)

    def draw(self, screen):
        self.screen.fill(self.white)
        self.screen.blit(self.ground, (0,0))
        self.combat_hero_sprites.draw(self.screen)
        self.combat_mob_sprites.draw(self.screen)

        gold_text = self.create_gold_text()
        self.screen.blit(gold_text, self.coords_gold)

        for live_monster in Config.room_monsters:
            live_monster.draw_health_bar()

        for live_hero in Config.party_heroes:
            live_hero.draw_health_bar()

        if Config.acting_character.animation: 
            self.animation_sprites.draw(screen)

        self.combat_log_events = Config.combat_log[-5:]
        COORDS_LOG = (self.screen_width * 0.15, self.screen_height * 0.70)
        for i, event in enumerate(reversed(self.combat_log_events)):
            log_line = f'{event[0]} deals {event[1]} to {event[2]}'
            log_line_text = self.info_font.render(log_line, True, self.black)
            log_line_rect = log_line_text.get_rect(topleft=(COORDS_LOG[0], COORDS_LOG[1] + i * self.info_font_size))
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
            VICTORY_TEXT = self.title_font.render(VICTORY, True, self.black)
            COORDS_VICTORY = (self.screen_width * 0.50, self.screen_height * 0.20)
            VICTORY_TEXT_RECT = VICTORY_TEXT.get_rect(center = COORDS_VICTORY)
            self.screen.blit(VICTORY_TEXT, VICTORY_TEXT_RECT)
            
            VICTORY_HEIGHT = VICTORY_TEXT.get_height() // 2
            COORDS_VIC = (self.screen_width * 0.50, self.screen_width * 0.20 + VICTORY_HEIGHT)

            for i, victory_line in enumerate(self.victory_lines):
                vic_line_text = self.info_font.render(victory_line, True, self.black)
                vic_line_rect = vic_line_text.get_rect(center=(COORDS_VIC[0], COORDS_VIC[1] + i * self.info_font_size))
                self.screen.blit(vic_line_text, vic_line_rect)
