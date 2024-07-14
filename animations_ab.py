"""
Animations module for managing attack animations during battles.

This module contains various classes that create sprite objects for different types of attacks, 
including hero weapon and spell attacks, attacks from heroes' minions, song attacks and various monster attacks.
"""

import pygame as pg
from config_ab import Config
from hero_ab import Hero
from sprites_ab import Monster
from data_ab import get_data
from sounds_ab import play_sound_effect
import numpy as np
import math

#Stab, Slash and Blast class code adapted from
#https://github.com/clear-code-projects/animation 

#ThrustAttack with parameter weapon type:
#weapon rotated to point at target

weapons_data = get_data('weapons')
follower_data = get_data('followers')

animation_speed = 0.3
def set_animation_speed(speed: float):
	"""Set the animation speed."""
	global animation_speed
	animation_speed = speed

def get_animation_speed() -> float:
	"""Return the current animation speed."""
	return animation_speed

class Stab(Config, pg.sprite.Sprite):
	"""
	Creates and manages the sprite object for a hero's stab attack animation.

	This class handles the movement, timing, and graphical representation of a stab animation during battles.
	"""

	def __init__(self, groups, weapon, pos_x, pos_y):
		"""Initialize the stab attack sprite."""
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 
		self.attack_animation = False

		weapon_df = weapons_data[weapons_data['name'] == weapon].reset_index(drop=True)
		weapon_image = pg.image.load('./ab_images/weapon/' + weapon + '.png').convert_alpha()
		WIDTH, HEIGHT = weapon_image.get_size()
		SIZE_SCALAR = weapon_df.loc[0, 'size_scalar']
		SCALED_WIDTH = WIDTH // SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT // SIZE_SCALAR
		POS_X_ADJUST = weapon_df.loc[0, 'offset_x']
		POS_Y_ADJUST = weapon_df.loc[0, 'offset_y']

		pos_x += POS_X_ADJUST
		pos_y += POS_Y_ADJUST

		self.pos_y = pos_y
		self.pos_x = pos_x
		self.attack_speed = 3 

		self.image = pg.transform.smoothscale(weapon_image, (SCALED_WIDTH, SCALED_HEIGHT))
		self.rect = self.image.get_rect()
		#use bottomleft?
		self.rect.bottomright = [self.pos_x, self.pos_y]

		self.reach = 10
		self.animation_timer = 0
		
	def animation_start(self):
		"""Start the stab animation."""
		self.attack_animation = True

	def animate(self, speed): 
		"""Animate the stab attack and return True if animation is complete."""
		if self.attack_animation == True:
			self.reach -= speed
			if int(self.reach) <= 0:
				self.attack_animation = False
				self.kill()
				return True

		self.attack_speed = speed * 10
		self.pos_y -= self.attack_speed
		self.rect = self.image.get_rect()
		#bottomleft?
		self.rect.bottomright = [self.pos_x, self.pos_y]

class Blast(Config, pg.sprite.Sprite):
	"""
	Creates and manages the sprite object for a hero's blast attack animation.

	This class handles the movement, timing, and graphical representation of a blast animation during battles.
	"""

	def __init__(self, groups, spell, pos_x, pos_y):
		"""Initialize the blast attack sprite."""
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 

		self.attack_animation = False
 
		CAST_IMAGE = pg.image.load('./ab_images/blast/spell.png').convert_alpha()
		WIDTH, HEIGHT = CAST_IMAGE.get_size()
		SIZE_SCALAR = 15
		SCALED_WIDTH = WIDTH // SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT // SIZE_SCALAR
		self.spell_type = spell['type']

		self.image = pg.transform.smoothscale(CAST_IMAGE, (SCALED_WIDTH, SCALED_HEIGHT))
		spell = pg.image.load('./ab_images/blast/' + self.spell_type + '.png').convert_alpha()
		self.spell_image = pg.transform.smoothscale(spell, (SCALED_WIDTH, SCALED_HEIGHT))

		self.rect = self.image.get_rect()
		OFFSET_X = self.screen_width // 16 #120
		OFFSET_Y = self.screen_height // 27 #40
		self.rect.topleft = [(pos_x + OFFSET_X), (pos_y - OFFSET_Y)] 

		self.timer = 0
		self.animation_time = 12
		self.finger_time = 5

	def animation_start(self):
		"""Start the blast attack animation."""
		self.attack_animation = True

	def animate(self, speed):
		"""Animate the blast attack and return True if animation is complete."""
		if self.attack_animation == True:
			self.timer += speed
			if self.timer > self.finger_time:
				self.image = self.spell_image
				#play_sound_effect(self.spell_type)
			if self.timer >= self.animation_time:
				self.timer = 0
				self.attack_animation = False
				self.kill()
				return True

class FollowerAttack(Config, pg.sprite.Sprite):
	"""
	Creates and manages the sprite object for a hero's minion followerattack attack animation.

	This class handles the movement, timing, and graphical representation of a followerattack animation during battles.
	"""

	def __init__(self, groups, follower_obj, pos_x, pos_y):
		"""Initialize the follower attack sprite."""
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 
		self.attack_animation = False
		follower_type = follower_obj.type
		follower_image = pg.image.load('./ab_images/monster/' + follower_type + '.png').convert_alpha()
		WIDTH, HEIGHT = follower_image.get_size()
		SIZE_SCALAR = follower_obj.size_scalar
		SCALED_WIDTH = WIDTH // SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT // SIZE_SCALAR
		POS_X_ADJUST = follower_obj.offset_x
		POS_Y_ADJUST = follower_obj.offset_y
		pos_x += POS_X_ADJUST
		pos_y += POS_Y_ADJUST

		self.pos_y = pos_y
		self.pos_x = pos_x
		self.attack_speed = 3 

		self.image = pg.transform.smoothscale(follower_image, (SCALED_WIDTH, SCALED_HEIGHT))
		self.rect = self.image.get_rect()
		self.rect.bottomright = [self.pos_x, self.pos_y]

		self.reach = 10
		self.animation_timer = 0
		
	def animation_start(self):
		"""Start the follower attack animation."""
		self.attack_animation = True

	def animate(self, speed): 
		"""Animate the follower attack and return True if animation is complete."""
		if self.attack_animation == True:
			self.reach -= speed
			if int(self.reach) <= 0:
				self.attack_animation = False
				self.kill()
				return True

		self.pos_y -= self.attack_speed
		self.rect = self.image.get_rect()
		self.rect.bottomright = [self.pos_x, self.pos_y]

class SongAnimation(pg.sprite.Sprite):
	"""
	Creates and manages the sprite object for a hero's song attack animation.

	This class handles the movement, timing, and graphical representation of a song animation during battles.
	"""

	def __init__(self, groups, pos_x, pos_y):
		"""Initialize the song attack sprite."""
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 

		self.attack_animation = False

		CAST_IMAGE = pg.image.load('./ab_images/song.png').convert_alpha()
		WIDTH, HEIGHT = CAST_IMAGE.get_size()
		SIZE_SCALAR = 15
		SCALED_WIDTH = WIDTH // SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT // SIZE_SCALAR

		self.image = pg.transform.smoothscale(CAST_IMAGE, (SCALED_WIDTH, SCALED_HEIGHT))
		
		self.rect = self.image.get_rect()
		OFFSET_X = Config.width // 16 #120
		OFFSET_Y = Config.height // 27 #40
		self.rect.topleft = [(pos_x + OFFSET_X), (pos_y - OFFSET_Y)] 
		self.timer = 0
		self.animation_time = 12

	def animation_start(self):
		"""Start the song attack animation."""
		self.attack_animation = True

	def animate(self, speed):
		"""Animate the song attack and return True if animation is complete."""
		if self.attack_animation == True:
			self.timer += speed
			if self.timer >= self.animation_time:
				self.timer = 0
				self.attack_animation = False
				self.kill()
				return True

class MonsterStab(Config, pg.sprite.Sprite):
	"""
	Creates and manages the sprite object for a monster's monsterstab attack animation.

	This class handles the movement, timing, and graphical representation of a monsterstab animation during battles.
	"""

	def __init__(self, groups, weapon, pos_x, pos_y):
		"""Initialize the monster stab attack sprite."""
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 
		self.attack_animation = False

		weapon_df = weapons_data[weapons_data['name'] == weapon].reset_index(drop=True)
		weapon_image = pg.image.load('./ab_images/weapon/' + weapon + '.png').convert_alpha()
		width, height = weapon_image.get_size()
		size_scalar = weapon_df.loc[0, 'size_scalar']
		scaled_width = width // size_scalar
		scaled_height = height // size_scalar

		adjust_x = weapon_df.loc[0, 'offset_x']
		adjust_y = weapon_df.loc[0, 'offset_y']
		pos_x += adjust_x
		pos_y += adjust_y

		self.pos_y = pos_y
		self.pos_x = pos_x
		
		scaled_image = pg.transform.smoothscale(weapon_image, (scaled_width, scaled_height))
		half_spin = 180
		self.image = pg.transform.rotozoom(scaled_image, half_spin, 1) 

		self.rect = self.image.get_rect()
		self.rect.topleft = [self.pos_x, self.pos_y]

		self.attack_speed = 3 
		self.reach = 10
		self.animation_timer = 0
		
	def animation_start(self):
		"""Start the monster stab attack animation."""
		self.attack_animation = True

	#speed = Combat.animation_speed
	def animate(self, speed): 
		"""Animate the monster stab attack and return True if animation is complete."""
		if self.attack_animation == True:
			self.reach -= speed
			if int(self.reach) <= 0:
				self.attack_animation = False
				self.kill()
				return True

		self.attack_speed = speed * 10
		self.pos_y += self.attack_speed
		self.rect = self.image.get_rect()
		self.rect.topleft = [self.pos_x, self.pos_y]
	
class Smash(pg.sprite.Sprite):
	"""
	Creates and manages the sprite object for a hero's smash attack animation.

	This class handles the movement, timing, and graphical representation of a smash animation during battles.
	"""
	
	def __init__(self, groups, pos_x, pos_y):
		"""Initialize the smash attack sprite."""
		#take weapon as parameter
		super().__init__()
		pg.sprite.Sprite.__init__(self, groups) 
		self.attack_animation = False

		#weapon_df = weapons_data[weapons_data['name'] == weapon].reset_index(drop=True)
		#weapon_image = pg.image.load('./ab_images/weapon/' + weapon + '.png').convert_alpha()
		#WIDTH, HEIGHT = weapon_image.get_size()
		#SIZE_SCALAR = weapon_df.loc[0, 'size_scalar']
		#SCALED_WIDTH = WIDTH / SIZE_SCALAR
		#SCALED_HEIGHT = HEIGHT / SIZE_SCALAR

		self.pos_x = pos_x
		self.pos_y = pos_y
		CLUB_IMAGE = pg.image.load('./ab_images/claw.png').convert_alpha()
		#CLUB_IMAGE = pg.image.load('./ab_images/weapons/club.png').convert_alpha()
		WIDTH, HEIGHT = CLUB_IMAGE.get_size()
		SIZE_SCALAR = 15
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
		"""Rotate the image and return the rotated image and its rect."""
		self.rotation -= rotation_speed
		self.rotation_remaining -= np.degrees(rotation_speed)
		image = pg.transform.rotozoom(self.club, np.degrees(self.rotation), 1)
		rect = image.get_rect()
		rect.center = (0, 0)
		return image, rect

	def animation_start(self):
		"""Start the smash attack animation."""
		self.attack_animation = True

	def animate(self, speed):
		"""Animate the smash attack and return True if animation is complete."""
		if self.attack_animation == True:
			ROTA_SPEED = 3 * speed
			SPEED_RADIANS = np.radians(ROTA_SPEED)
			self.image, self.rect = self.rotate(SPEED_RADIANS)
			if self.rotation_remaining <= 0:
				self.attack_animation = False
				self.image = pg.transform.rotozoom(self.club, np.degrees(self.rotation), 1)
				self.kill()
				return True
		
		XOFFSET, YOFFSET = np.cos(self.rotation) * self.offset, -np.sin(self.rotation) * self.offset
		self.rect.center = (self.pos_x + self.rect.centerx - XOFFSET, self.pos_y + self.rect.centery - YOFFSET)