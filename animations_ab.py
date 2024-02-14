import pygame as pg, sys
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Monster
from data_ab import get_data
import numpy as np

#Stab, Slash and Blast class code adapted from
#https://github.com/clear-code-projects/animation 

#ThrustAttack with parameter weapon type:
#weapon rotated to point at target

weapons_data = get_data('weapons')

#Wizard / Bard without spells breaks
class Stab(Config, pg.sprite.Sprite): #Groupsingle
	def __init__(self, groups, weapon, pos_x, pos_y):
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 
		self.attack_animation = False

		weapon_df = weapons_data[weapons_data['name'] == weapon].reset_index(drop=True)
		weapon_image = pg.image.load('./ab_images/weapons/' + weapon + '.png').convert_alpha()
		WIDTH, HEIGHT = weapon_image.get_size()
		SIZE_SCALAR = weapon_df.loc[0, 'size_scalar']
		SCALED_WIDTH = WIDTH / SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT / SIZE_SCALAR
		POS_X_ADJUST = weapon_df.loc[0, 'offset_x']
		POS_Y_ADJUST = weapon_df.loc[0, 'offset_y']
		pos_x += POS_X_ADJUST
		pos_y += POS_Y_ADJUST

		self.pos_y = pos_y
		self.pos_x = pos_x
		self.attack_speed = 3 

		self.image = pg.transform.smoothscale(weapon_image, (SCALED_WIDTH, SCALED_HEIGHT))
		self.rect = self.image.get_rect()
		#bottomleft?
		self.rect.bottomright = [self.pos_x, self.pos_y]

		self.reach = 10
		self.animation_timer = 0
		
	def animation_start(self):
		self.attack_animation = True
	
	def animate(self, speed): #speed = Combat.animation_speed
		if self.attack_animation == True:
			self.reach -= speed
			if int(self.reach) <= 0:

				self.attack_animation = False
				#self.image = self.weapon_sprites[int(self.current_sprite)]
				#
				#pass weapon information to attack
				Config.acting_character.melee_attack()
				return True #return melee/spell?

		self.pos_y -= self.attack_speed
		#self.image = self.weapon_sprites[int(self.current_sprite)]
		self.rect = self.image.get_rect()
		self.rect.bottomright = [self.pos_x, self.pos_y]


class Staby(Config, pg.sprite.Sprite): #Groupsingle
	def __init__(self, groups, weapon, pos_x, pos_y):
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 
		self.attack_animation = False
		self.weapon_sprites = [] 
		weapon_image = pg.image.load('./ab_images/weapons/dagger.png').convert_alpha()
		WIDTH, HEIGHT = weapon_image.get_size()
		SIZE_SCALAR = 5
		SCALED_WIDTH = WIDTH / SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT / SIZE_SCALAR
		POS_X_ADJUST = 20
		POS_Y_ADJUST = 12
		pos_x += POS_X_ADJUST
		pos_y += POS_Y_ADJUST

		self.pos_y = pos_y
		self.pos_x = pos_x
		self.stab_speed = 3 

		for i in range(0, 10):
			self.weapon_sprites.append(pg.transform.smoothscale(weapon_image, (SCALED_WIDTH, SCALED_HEIGHT)))
	
		self.current_sprite = 0
		self.image = self.weapon_sprites[self.current_sprite]
		self.rect = self.image.get_rect()
		#bottomleft?
		self.rect.bottomright = [self.pos_x, self.pos_y]

	def animation_start(self):
		self.attack_animation = True

	def animate(self, speed): 
		if self.attack_animation == True:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.weapon_sprites):
				self.current_sprite = 0
				self.attack_animation = False
				self.image = self.weapon_sprites[int(self.current_sprite)]
				Config.acting_character.melee_attack()
				return True #return melee/spell?
		self.pos_y -= 3
		self.image = self.weapon_sprites[int(self.current_sprite)]
		self.rect = self.image.get_rect()
		self.rect.bottomright = [self.pos_x, self.pos_y]


class Blast(pg.sprite.Sprite):
	def __init__(self, groups, pos_x, pos_y, spell):
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 

		self.attack_animation = False
		self.spell_sprites = [] 
		self.attack_spell = spell
		CAST_IMAGE = pg.image.load('./ab_images/blast/spell.png').convert_alpha()
		WIDTH, HEIGHT = CAST_IMAGE.get_size()
		SIZE_SCALAR = 15
		SCALED_WIDTH = WIDTH / SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT / SIZE_SCALAR
		spell_type = spell["type"]

		for i in range(1, 6):
			self.spell_sprites.append(pg.transform.smoothscale(CAST_IMAGE, (SCALED_WIDTH, SCALED_HEIGHT)))
		
		for i in range(6, 11):
			spell = pg.image.load('./ab_images/blast/' + spell_type + '.png').convert_alpha()
			self.spell_sprites.append(pg.transform.smoothscale(spell, (SCALED_WIDTH, SCALED_HEIGHT)))
        
		self.current_sprite = 0
		self.image = self.spell_sprites[self.current_sprite]

		self.rect = self.image.get_rect()
		self.rect.topleft = [(pos_x + (Config.width / 16)), (pos_y - (Config.width / 27))] 

	def animation_start(self):
		self.attack_animation = True

	def animate(self, speed): #attacker is always speedorder[0], target enemy list[0]
		if self.attack_animation == True:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.spell_sprites):
				self.current_sprite = 0
				self.attack_animation = False
				self.image = self.spell_sprites[int(self.current_sprite)]
				Config.acting_character.spell_attack(self.attack_spell)
				return True

		self.image = self.spell_sprites[int(self.current_sprite)]

#Slash animation not working properly
#black screen blink in combat start
class Slash(pg.sprite.Sprite):
	def __init__(self, groups, pos_x, pos_y):
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups)

		self.attack_animation = False
		self.claw_sprites = []
		claw = pg.image.load('./ab_images/claw/claw.png').convert_alpha()
		WIDTH, HEIGHT = claw.get_size()
		SIZE_SCALAR = 10
		SCALED_WIDTH = WIDTH / SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT / SIZE_SCALAR

		for i in range(10):
			CLAW_ROTATION = pg.transform.rotate(claw, ((i * -9) + 45))
			self.claw_sprites.append(pg.transform.smoothscale(CLAW_ROTATION, (SCALED_WIDTH, SCALED_HEIGHT)))
        
		self.current_sprite = 0
		self.image = self.claw_sprites[self.current_sprite]
		self.rect = self.image.get_rect()
		self.rect.center = [pos_x, pos_y]
		
	def animation_start(self):
		self.attack_animation = True

	def animate(self, speed):
		if self.attack_animation == True:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.claw_sprites):
				self.current_sprite = 0
				self.attack_animation = False
				self.image = self.claw_sprites[int(self.current_sprite)]
				Config.acting_character.melee_attack() #Config.party_heroes[0]
				return True

		self.image = self.claw_sprites[int(self.current_sprite)]
		self.rect = self.image.get_rect(topleft = self.rect.topleft)


class Smash(pg.sprite.Sprite):
	def __init__(self, groups, pos_x, pos_y):
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 
		self.attack_animation = False
		self.pos_x = pos_x
		self.pos_y = pos_y
		CLUB_IMAGE = pg.image.load('./ab_images/claw.png').convert_alpha()
		#CLUB_IMAGE = pg.image.load('./ab_images/weapons/club.png').convert_alpha()
		WIDTH, HEIGHT = CLUB_IMAGE.get_size()
		#claw skalar
		SIZE_SCALAR = 15
		#SIZE_SCALAR = 5
		SCALED_WIDTH = WIDTH / SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT / SIZE_SCALAR
		INITIAL_ANGLE = 150
		ROTATION_ANGLE = 50
		self.club = pg.transform.smoothscale(CLUB_IMAGE, (SCALED_WIDTH, SCALED_HEIGHT))
		self.reach = self.club.get_rect()[2]
		self.offset = self.reach / 2.0
		self.rotation = np.radians(INITIAL_ANGLE)
		self.rotation_remaining = ROTATION_ANGLE
		self.image = pg.transform.rotozoom(self.club, np.degrees(self.rotation), 1)
		self.rect = self.image.get_rect()
		self.rect.center = [pos_x, pos_y]

	def rotate(self, rotation_speed):
		self.rotation -= rotation_speed
		self.rotation_remaining -= np.degrees(rotation_speed)
		image = pg.transform.rotozoom(self.club, np.degrees(self.rotation), 1)
		rect = image.get_rect()
		rect.center = (0, 0)
		return image, rect

	def animation_start(self):
		self.attack_animation = True

	def animate(self, speed):
		if self.attack_animation == True:
			ROTA_SPEED = 3 * speed
			SPEED_RADIANS = np.radians(ROTA_SPEED)
			self.image, self.rect = self.rotate(SPEED_RADIANS)
			if self.rotation_remaining <= 0:
				self.attack_animation = False
				self.image = pg.transform.rotozoom(self.club, np.degrees(self.rotation), 1)
				Config.acting_character.melee_attack()
				return True
		
		XOFFSET, YOFFSET = np.cos(self.rotation) * self.offset, -np.sin(self.rotation) * self.offset
		self.rect.center = (self.pos_x + self.rect.centerx - XOFFSET, self.pos_y + self.rect.centery - YOFFSET)