import pygame as pg, sys
from states import States
from objects import Hero, Monster
import numpy as np

def melee_attack(attacker, target):
	States.acting.animation = False
	target.health -= (attacker.damage - target.armor)

def spell_attack(attacker, target, spell):
	States.acting.animation = False
	if spell["area"] == 1:
		for target_mob in States.room_monsters:
			target_mob.health -= spell["damage"]
	target.health -= attacker.damage

#Stab, Slash and Blast class code adapted from
#https://github.com/clear-code-projects/animation 

#Animation masterclass or consolidate into single class

class Stab(pg.sprite.Sprite): #Groupsingle
	def __init__(self, pos_x, pos_y):
		super().__init__()
		self.attack_animation = False
		self.weapon_sprites = [] 
		#club_image = pg.image.load('./ab_images/club.png').convert_alpha()
		weapon_image = pg.image.load('./ab_images/stab/sword1.png').convert_alpha()
		height = weapon_image.get_height()
		width = weapon_image.get_width()
		
		for i in range(1, 11):
			weapon = pg.image.load('./ab_images/stab/sword' + str(i) + '.png').convert_alpha()
			#adjust width height / 10 to screen size
			self.weapon_sprites.append(pg.transform.scale(weapon, ((width / 10), (height / 10))))
        
		self.current_sprite = 0
		self.image = self.weapon_sprites[self.current_sprite]

		self.rect = self.image.get_rect()
		self.rect.bottomright = [pos_x, pos_y]

	def animation_start(self):
		self.attack_animation = True

	def animate(self, speed): #attacker is always speedorder[0], target enemy list[0]
		if self.attack_animation == True:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.weapon_sprites):
				self.current_sprite = 0
				self.attack_animation = False
				self.image = self.weapon_sprites[int(self.current_sprite)]
				melee_attack(States.acting, States.room_monsters[0])
				return True #triggers next attacker

		self.image = self.weapon_sprites[int(self.current_sprite)]

class Blast(pg.sprite.Sprite):
	def __init__(self, pos_x, pos_y, spell):
		super().__init__()
		self.attack_animation = False
		self.spell_sprites = [] 
		self.attack_spell = spell
		cast_image = pg.image.load('./ab_images/blast/spell.png').convert_alpha()
		height = cast_image.get_height()
		width = cast_image.get_width()
		spell_type = spell["type"]

		for i in range(1, 6):
			spell = pg.image.load('./ab_images/blast/spell.png').convert_alpha()
			self.spell_sprites.append(pg.transform.scale(spell, ((width / 15), (height / 15))))
		
		for i in range(6, 11):
			spell = pg.image.load('./ab_images/blast/' + spell_type + '.png').convert_alpha()
			self.spell_sprites.append(pg.transform.scale(spell, ((width / 15), (height / 15))))
        
		self.current_sprite = 0
		self.image = self.spell_sprites[self.current_sprite]

		self.rect = self.image.get_rect()
		self.rect.topleft = [(pos_x + (States.width / 16)), (pos_y - (States.width / 27))] 

	def animation_start(self):
		self.attack_animation = True

	def animate(self, speed): #attacker is always speedorder[0], target enemy list[0]
		if self.attack_animation == True:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.spell_sprites):
				self.current_sprite = 0
				self.attack_animation = False
				self.image = self.spell_sprites[int(self.current_sprite)]
				#melee_attack(States.acting, States.room_monsters[0])
				spell_attack(States.acting, States.room_monsters[0], self.attack_spell)
				return True #triggers next attacker

		self.image = self.spell_sprites[int(self.current_sprite)]

class Slash(pg.sprite.Sprite):
	def __init__(self, pos_x, pos_y):
		super().__init__()
		self.attack_animation = False
		self.claw_sprites = []
		claw = pg.image.load('./ab_images/claw/claw.png').convert_alpha()
		WIDTH, HEIGHT = claw.get_size()
		SIZE_SCALAR = 10
		SCALED_WIDTH = WIDTH / SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT / SIZE_SCALAR

		for i in range(10):
			CLAW_ROTATION = pg.transform.rotate(claw, ((i * -9) + 45))
			self.claw_sprites.append(pg.transform.scale(CLAW_ROTATION, (SCALED_WIDTH, SCALED_HEIGHT)))
        
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
				melee_attack(States.acting, States.party_heroes[0])
				return True

		self.image = self.claw_sprites[int(self.current_sprite)]
		self.rect = self.image.get_rect(topleft = self.rect.topleft)

class Smash(pg.sprite.Sprite):
	def __init__(self, pos_x, pos_y):
		super().__init__()
		self.attack_animation = False
		self.pos_x = pos_x
		self.pos_y = pos_y
		CLUB_IMAGE = pg.image.load('./ab_images/club.png').convert_alpha()
		WIDTH, HEIGHT = CLUB_IMAGE.get_size()
		SIZE_SCALAR = 5
		SCALED_WIDTH = WIDTH / SIZE_SCALAR
		SCALED_HEIGHT = HEIGHT / SIZE_SCALAR
		INITIAL_ANGLE = 150
		ROTATION_ANGLE = 50
		self.club = pg.transform.scale(CLUB_IMAGE, (SCALED_WIDTH, SCALED_HEIGHT))
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
			ROTA_SPEED = 2 * speed
			SPEED_RADIANS = np.radians(ROTA_SPEED)
			self.image, self.rect = self.rotate(SPEED_RADIANS)
			if self.rotation_remaining <= 0:
				self.attack_animation = False
				self.image = pg.transform.rotozoom(self.club, np.degrees(self.rotation), 1)
				melee_attack(States.acting, States.party_heroes[0])
				return True
		
		XOFFSET, YOFFSET = np.cos(self.rotation) * self.offset, -np.sin(self.rotation) * self.offset
		self.rect.center = (self.pos_x + self.rect.centerx - XOFFSET, self.pos_y + self.rect.centery - YOFFSET)