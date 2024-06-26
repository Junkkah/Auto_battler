import pygame as pg
from config_ab import Config
from data_ab import get_talent_data, row_to_dict, get_data, get_json_data
from sprites_ab import Follower
import random

spells_data = get_data('spells')

class TalentsManager(Config):
    def __init__(self):
        Config.__init__(self)

    @staticmethod
    def add_talent(talent_name: str, talent_type: str, hero):
        hero_talents = get_talent_data(hero.type)
        talents_row = hero_talents[hero_talents['name'] == talent_name]
        talents = row_to_dict(talents_row, talent_name)

        if talent_type == 'spell':
            #resolve name/effect in spells with id
            #Talent name: 'Fire Gush' effect: 'fire_gush'
            #effect should be name, name should be name_text

            spell_name = talents['effect'] 
            talent_spell = row_to_dict(spells_data, spell_name)
            hero.talents.append(talent_name)
            hero.spells.append(talent_spell)

        elif talent_type == 'stat':
            hero.talents.append(talent_name)
            stat_bonus = talents['effect']
            hero.add_stat(stat_bonus)

        elif talent_type in ['location', 'combat', 'map', 'song']:
            hero.talents.append(talent_name)
            effect = talents['effect']
            effect_name, rank = effect.split()
            talent_rank = int(rank)
            method_name = f'{effect_name}_activation'

            #dynamic activation
            activation_method = getattr(TalentActivations, method_name)
            #activation_method = getattr(hero, method_name)
            hero.talent_groups[talent_type][effect_name] = {'activation_method': activation_method, 'rank': talent_rank}
            #[effect] = [effect_name]
        elif talent_type == 'domain':
            hero.talents.append(talent_name) 
            hero.type = talents['effect']

        elif talent_type == 'm_stat':
            hero.talents.append(talent_name)
            string = talents['effect']
            stats = string.split()
            first_bonus = ' '.join(stats[:2])
            second_bonus = ' '.join(stats[2:])
            hero.add_stat(first_bonus)
            hero.add_stat(second_bonus)
        
        elif talent_type == 'aura':
            hero.talents.append(talent_name)
            hero.aura = talents['effect']
        
        elif talent_type == 'spell_mastery':
            hero.talents.append(talent_name)
            mastery_type = talents['effect']
            hero.spell_mastery[mastery_type] += 1
        
        elif talent_type == 'once':
            hero.talents.append(talent_name)
            effect = talents['effect']
            if len(effect.split()) == 3:
                method, eff1, eff2 = effect.split()
                effect = eff1 + ' ' + eff2
            else:
                method, effect = effect.split()
            method_name = f'{method}_activation'

            activation_method = getattr(TalentActivations, method_name)
            #activation_method = getattr(hero, method_name)
            activation_method(hero, effect)

class TalentActivations(Config):
    def __init__(self):
        Config.__init__(self)


    #scroll activation
    #move to items?
    @staticmethod
    def fire_spell_activation(hero, rank):
        if rank > 1:
            spell_name = 'fireball'
        else:
            spell_name = 'flame_bolt'
        fire_spell = row_to_dict(spells_data, spell_name)
        hero.spell_attack(fire_spell)

    #used for talent and item
    #move copy to items?
    @staticmethod
    def healing_activation(hero, rank):
        total_rank = rank
        healing_per_rank = 3
        total_healing = healing_per_rank * total_rank
        hero.gain_health(total_healing)

    @staticmethod
    def invisibility_activation(hero, rank):
        hero.menace = 1
    
    @staticmethod
    def uplift_activation(hero, rank):
        total_rank = hero.songmaster_rank + rank
        damage_bonus_per_rank = 1
        total_damage_bonus = damage_bonus_per_rank * total_rank
        Config.aura_bonus['damage'] += total_damage_bonus

    @staticmethod
    def sooth_activation(hero, rank):
        total_rank = hero.songmaster_rank + rank
        healing_per_rank = 1
        total_healing = (healing_per_rank * total_rank) - 1
        for healing_hero in Config.party_heroes:
            healing_hero.gain_health(total_healing)

    @staticmethod
    def loud_activation(hero, rank):
        total_rank = hero.songmaster_rank + rank
        damage_per_rank = 2
        total_damage = damage_per_rank * total_rank
        damage_type = 'sonic'
        DAMAGE = total_damage
        armor_penalty = 0
        for target_mob in Config.room_monsters:
            target_mob.take_damage(DAMAGE, damage_type, armor_penalty)

    @staticmethod
    def songmaster_activation(hero, effect):
        rank = int(effect)
        hero.songmaster_rank += rank

    @staticmethod
    def scout_activation(hero, effect):
        Config.scout_active = True 
    
    @staticmethod
    def surprise_activation(hero, rank):
        speed_penalty_per_rank = 3
        total_speed_penalty = speed_penalty_per_rank * rank
        for surprised_monster in Config.room_monsters:
            surprised_monster.take_debuff('speed', total_speed_penalty)
    
    @staticmethod
    def reveal_activation(hero, rank):
        armor_penalty_per_rank = 1
        total_armor_penalty = armor_penalty_per_rank * rank
        for revealed_monster in Config.room_monsters:
            revealed_monster.take_debuff('armor', total_armor_penalty)

    @staticmethod
    def berserk_activation(hero, rank):
        #hero.talent_bonus['menace'] = 0
        damage_bonus_per_rank = 3
        menace_bonus_per_rank = 2
        total_damage = damage_bonus_per_rank * rank
        total_menace = menace_bonus_per_rank * rank
        if hero.health < hero.max_health // 2:
            hero.talent_bonus['damage'] += total_damage
            #hero.talent_bonus['menace'] += total_menace

    @staticmethod
    def crush_activation(hero, rank):
        armor_pierced_per_rank = 2
        total_pierce = armor_pierced_per_rank * rank
        hero.enemy_armor_penalty += total_pierce

    @staticmethod
    def smite_activation(hero, rank):
        damage_per_rank = 2
        damage_type = 'holy'
        DAMAGE = damage_per_rank * rank
        armor_penalty = 0
        for target_mob in Config.room_monsters:
            target_mob.take_damage(DAMAGE, damage_type, armor_penalty)

    @staticmethod
    def roots_activation(hero, rank):
        damage_per_rank = 1
        damage_type = 'nature'
        DAMAGE = damage_per_rank * rank
        armor_penalty = 0
        for target_mob in Config.room_monsters:
            target_mob.take_damage(DAMAGE, damage_type, armor_penalty)
    
    @staticmethod
    def smiting_activation(hero, rank):
        damage_per_rank = 1
        damage_type = 'holy'
        DAMAGE = damage_per_rank * rank
        armor_penalty = 0
        for target_mob in Config.room_monsters:
            target_mob.take_damage(DAMAGE, damage_type, armor_penalty)

    @staticmethod
    def replenish_activation(hero, rank):
        healing_per_rank = 2
        total_healing = healing_per_rank * rank
        for healing_hero in Config.party_heroes:
            healing_hero.gain_health(total_healing)
    
    @staticmethod
    def pilfer_activation(hero, rank):
        gold_per_rank = 2
        extra_gold = gold_per_rank * rank
        Config.gold_count += extra_gold

    #add health check for mobs before combat, after talent activation
    @staticmethod
    def ambush_activation(hero, rank):
        DAMAGE = hero.worn_items['hand1'].base_damage
        target = hero.get_target()
        armor_penalty = 0
        target.take_damage(DAMAGE, 'physical', armor_penalty)
    
    @staticmethod
    def lonewolf_activation(hero, rank):
        damage_bonus_per_rank = 4
        total_damage_bonus = damage_bonus_per_rank * rank
        armor_bonus_per_rank = 1
        total_armor_bonus = armor_bonus_per_rank * rank
        if len(Config.party_heroes) == 1:
            hero.talent_bonus['damage'] += total_damage_bonus
            hero.talent_bonus['armor'] += total_armor_bonus
    
    @staticmethod
    def inevitable_activation(hero, rank):
        damage_increase_per_rank = 1
        total_damage_increase = damage_increase_per_rank * rank
        hero.damage += total_damage_increase
    
    @staticmethod
    def bloodthirst_activation(hero, rank):
        healing_per_rank = 2
        total_healing = healing_per_rank * rank
        hero.gain_health(total_healing)

    @staticmethod
    def shelter_activation(hero, rank):
        armor_per_rank = 1
        total_armor = armor_per_rank * rank
        Config.aura_bonus['armor'] += total_armor

    @staticmethod
    def xtr_att_activation(hero, rank):
        extra_attacks_per_rank = 1
        total_extra_attacks = extra_attacks_per_rank * rank
        target = hero.get_target()
        hero.melee_attack(target)

    @staticmethod
    def haste_activation(hero, rank):
        for dancing_hero in Config.party_heroes:
            target = hero.get_target()
            dancing_hero.melee_attack(target)
    
    @staticmethod
    def coordinate_activation(hero, rank):
        menace_debuff_per_rank = 3
        total_menace_debuff = menace_debuff_per_rank * rank
        target = hero.get_target()
        target.take_debuff('menace', total_menace_debuff)

    @staticmethod
    def homing_activation(hero, rank):
        menace_per_rank = 1
        total_menace = menace_per_rank * rank
        target = hero.get_target()
        target.menace += total_menace
    
    @staticmethod
    def entrap_activation(hero, rank):
        armor_penalty_per_rank = 1
        total_armor_penalty = armor_penalty_per_rank * rank
        for entrapped_monster in Config.room_monsters:
            entrapped_monster.take_debuff('armor', total_armor_penalty)
    
    @staticmethod
    def dark_activation(hero, rank):
        damage_penalty_per_rank = 1
        total_damage_penalty = damage_penalty_per_rank * rank
        for blinded_monster in Config.room_monsters:
            blinded_monster.take_debuff('damage', total_damage_penalty)
    
    @staticmethod
    def magicfind_activation(hero, effect):
        rank = int(effect)
        magic_find_per_rank = 0.02
        total_magic_find = magic_find_per_rank * rank
        Config.magic_find += total_magic_find
    
    #requires importing Follower from hero_ab
    #hero_ab needs to import talentactivation
    #move follower to sprites
    @staticmethod
    def follower_activation(hero, effect):
        follower_type = effect
        follower_names = get_json_data('follower_names')
        name = random.choice(follower_names[follower_type])
        new_follower = Follower(name, follower_type, hero)
        Config.party_followers.append(new_follower)
    
    @staticmethod
    def foll_dam_activation(hero, effect):
        rank = int(effect)
        damage_increase_per_rank = 2
        total_damage_increase = damage_increase_per_rank * rank
        for follower in Config.party_followers:
            if follower.following == hero:
                follower.damage += total_damage_increase
    
    @staticmethod
    def bargain_activation(hero, effect):
        rank = int(effect)
        discount_per_rank = 3
        total_discount = discount_per_rank * rank
        Config.party_discount += total_discount
    
    @staticmethod
    def fiery_activation(hero, effect):
        hero.attack_type = 'spell'
        TalentsManager.add_talent('Burn', 'spell')
    
    @staticmethod
    def waterheal_activation(hero, effect):
        for healed_hero in Config.party_heroes:
            health = healed_hero.max_health
            healed_hero.gain_health(health)
    
    @staticmethod
    def revivify_activation(hero, effect):
        Config.revive_divisor = 1.5