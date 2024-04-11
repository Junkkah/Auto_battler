import pygame as pg
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Monster, Equipment
from animations_ab import Stab, Slash, Blast, Smash, SongAnimation
from sounds_ab import play_sound_effect
from data_ab import get_json_data, get_affix
import random
import pygame.mixer


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
        self.combat_delay = 1.1
        self.animation_speed = 0.3
    
    def cleanup(self):
        self.animation_sprites.empty()
        self.combat_hero_sprites.empty()
        self.combat_mob_sprites.empty()
        self.actions_unordered = []
        Config.room_monsters = []
        Config.combat_log = []
        for loot_item in self.item_loot:
            BattleManager.item_to_backpack(loot_item)
        self.item_loot = []
        Config.gold_count += self.gold_loot

        for risen_hero in self.defeated_heroes:
            Config.party_heroes.append(risen_hero)
            risen_hero.health = risen_hero.max_health // 2
        self.defeated_heroes = []

        for cleanup_hero in Config.party_heroes:
            cleanup_hero.exp += self.exp_reward
            cleanup_hero.item_stats_dict = {item_key: 0 for item_key in cleanup_hero.item_stats_dict}

        self.exp_reward = 0
        self.gold_loot = 0
        self.combat_started = False
        self.delay_timer = 0.0
        Config.aura_bonus = {aura_key: 0 for aura_key in Config.aura_bonus}
        if self.party_defeated:
            self.reset_adventure()
    
    def create_gold_loot(self):
        total_min_gold = 0
        total_max_gold = 0
        for loot_monster in Config.room_monsters:
            total_min_gold += loot_monster.gold_min
            total_max_gold += loot_monster.gold_max
        total_loot = random.randint(total_min_gold, total_max_gold)
        return total_loot
    
    @staticmethod
    def item_to_backpack(item):
        sorted_keys = sorted(Config.party_backpack.keys(), key=lambda x: int(x.split('slot')[1]))
        for key in sorted_keys:
            if Config.party_backpack[key] is None:
                Config.party_backpack[key] = item
                break 
    
    #create itemhandler class
    @staticmethod
    def create_magic_item(item_type, subtype, item_power):
        tier = random.randint(1, item_power)
        slot_type_mapping = {'weapon': 'hand1', 'armor': subtype}
        item_tier = 'tier_' + str(tier)
        #tie certain modifiers to item subtypes (staff = magic_power)
        if item_type == 'consumable':
            affix_df = get_affix(subtype, 'suffix')
            random_affix = affix_df.sample(n = 1)
            suffix = random_affix[item_tier].iloc[0]
            prefix = ''
        else:
            affix_df = get_affix(item_type, 'prefix')
            random_affix = affix_df.sample(n = 1)
            prefix = random_affix[item_tier].iloc[0]
            suffix = ''
        effect_type = random_affix['mod_type'].iloc[0]
        effect = random_affix['mod_effect'].iloc[0]

        slot_type = slot_type_mapping.get(item_type, item_type)
        magic_item = Equipment(subtype, item_type, slot_type, prefix, suffix, effect_type, effect, tier)
        return magic_item

    @classmethod
    def create_random_item(cls, item_probabilities):
        item_type = random.choices(list(item_probabilities.keys()), weights=[40, 45, 15])[0]
        subtype = random.choices(item_probabilities[item_type]['types'], weights=item_probabilities[item_type]['prob'])[0]
        upper_limit = Config.current_location.tier
        item_power = random.randint(1, upper_limit)
        created_item = cls.create_magic_item(item_type, subtype, item_power)
        return created_item

    def create_item_loot(self):
        looted_items = []
        item_probabilities = get_json_data('item_probabilities')
        drop_chance_bonus = (Config.current_location.tier / 100)
        for monster in Config.room_monsters:
            #number_of_loot_rolls attribute, 1-5. Repeat for each 
            item_drop_chance = monster.loot_roll + drop_chance_bonus
            if random.random() <= item_drop_chance:
                random_item = self.create_random_item(item_probabilities)
                looted_items.append(random_item)
        return looted_items    
    
    def reset_adventure(self):
        self.defeated_heroes = []
        Config.party_backpack = {}
        Config.backpack_slots = []
        Config.equipment_slots = []
        Config.current_adventure = None
        Config.current_location = None
        Config.acting_character = None
        Config.gold_count = 50
        Config.scout_active = False
        self.party_defeated = False

    #move to Config?
    def position_heroes(self, heroes: list):
        HEROPOS_X = (self.screen_width * 0.3)
        HEROPOS_Y = (self.screen_height * 0.6)
        HERO_GAP = (self.screen_width * 0.2)
        for spot_hero in Config.party_heroes:
           spot_hero.rect = spot_hero.image.get_rect(topleft = (HEROPOS_X, HEROPOS_Y)) 
           spot_hero.pos_x = HEROPOS_X
           spot_hero.pos_y = HEROPOS_Y
           HEROPOS_X += HERO_GAP
    
    def create_monsters(self, monster_count, monster_names):
        y = 0.2
        pos_y = self.screen_height * y
        monster_x_coords = [(i + 1) / (monster_count + 1) for i in range(monster_count)]

        for j, x in enumerate(monster_x_coords):
            pos_x = self.screen_width * x
            monster = Monster(self.monster_sprites, (pos_x, pos_y), monster_names[j])
            Config.room_monsters.append(monster)

    #tie breaker, first in hero/mob list > lower, hero > mob, class prios
    def order_sort(self, incombat: list):
        def speed_order(battle_participant: object):
            if battle_participant.is_player:
                hero_speed = battle_participant.total_stat('speed')
                return hero_speed
            else:
                monster_speed = battle_participant.speed
                return monster_speed
        return sorted(incombat, key=speed_order, reverse=True)
    

    def startup(self):
        self.party_defeated = False
        if Config.current_location.type == 'boss':
            play_sound_effect(Config.current_location.name)
        self.combat_started = False
        self.delay_timer = 0.0

        self.position_heroes(Config.party_heroes)
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

        #group in activation function
        for activation_hero in Config.party_heroes:
            activation_hero.activate_talent_group('location')
            activation_hero.activate_item_stats()
            #activation_hero.acticate_item_effects()
            activation_hero.activate_aura()

        self.gold_loot = self.create_gold_loot()
        self.item_loot = self.create_item_loot()
        self.actions_ordered = self.order_sort(self.actions_unordered)
        Config.acting_character = self.actions_ordered[0]

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if not Config.room_monsters:
                if Config.current_location.type == 'boss':
                    #dark forest adventure cleared
                    #continue to decrepit ruins adventure
                    pg.mixer.stop()
                    self.party_defeated = True
                    self.next = 'menu'
                self.done = True
            if not Config.party_heroes:
                pg.mixer.stop()
                self.party_defeated = True
                self.next = 'menu'
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
        # Attack animation has not started and both monster and hero lists have list items
        if not Config.acting_character.animation and Config.room_monsters and Config.party_heroes: 
            if Config.acting_character.is_player:
                pos_x = Config.acting_character.pos_x
                pos_y = Config.acting_character.pos_y

                #hero always cast index 0 spell in self.spells
                if Config.acting_character.attack_type == 'spell':
                    #play play_sound_effect based on spell type
                    #weapon = Config.acting_character.worn_items['hand1']
                    self.combat_animation = Blast(self.animation_sprites, pos_x, pos_y, Config.acting_character.spells[0])
                
                elif Config.acting_character.attack_type == 'song':
                    play_sound_effect('tune')
                    self.combat_animation = SongAnimation(self.animation_sprites, pos_x, pos_y)
                else:
                    play_sound_effect('sword')
                    if Config.acting_character.worn_items['hand1'] == None:
                        held_weapon = 'unarmed'
                    else:
                        held_weapon = Config.acting_character.worn_items['hand1'].name
                    self.combat_animation = Stab(self.animation_sprites, held_weapon, pos_x, pos_y)

            elif not Config.acting_character.is_player:
                if Config.acting_character.type in ['kobold', 'goblin']:
                    play_sound_effect('growl')
                adjusted_pos_x = Config.acting_character.pos_x + Config.acting_character.width
                adjusted_pos_y = Config.acting_character.pos_y + Config.acting_character.height
                self.combat_animation = Smash(self.animation_sprites, adjusted_pos_x, adjusted_pos_y)
                
            Config.acting_character.animation = True
            self.combat_animation.animation_start()

        # Call attack methods 
        if self.combat_animation.animate(self.animation_speed):
            if Config.acting_character.attack_type == 'spell':
                Config.acting_character.activate_talent_group('combat')
                #Config.acting_character.spell_attack()
                Config.acting_character.spell_attack(Config.acting_character.spells[0])
            elif Config.acting_character.attack_type == 'song':
                Config.acting_character.activate_talent_group('song')
                Config.acting_character.song_attack()
            else:
                if Config.acting_character.is_player:
                    Config.acting_character.activate_talent_group('combat')
                Config.acting_character.melee_attack()

            self.animation_sprites.remove(self.combat_animation)
            self.actions_ordered.append(self.actions_ordered.pop(0))
            
            if Config.acting_character.is_player:
                for fighting_monster in Config.room_monsters:
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

            elif not Config.acting_character.is_player:  
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

        self.combat_log_events = Config.combat_log[-10:]
        COORDS_LOG = (self.screen_width * 0.05, self.screen_height * 0.60)
        for i, event in enumerate(reversed(self.combat_log_events)):
            log_line = "{} deals {:>4} to {}".format(event[0].capitalize().ljust(14), event[1], event[2].capitalize())
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
