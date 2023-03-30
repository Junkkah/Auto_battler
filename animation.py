import pygame as pg, sys
from states import States
from objects import Hero, Monster

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

class Stab(pg.sprite.Sprite):
	def __init__(self, xpos, ypos):
		super().__init__()
		self.attack_animation = False
		self.sword_sprites = [] 
		sword_image = pg.image.load('./ab_images/stab/sword1.png').convert_alpha()
		height = sword_image.get_height()
		width = sword_image.get_width()
		
		for i in range(1, 11):
			sword = pg.image.load('./ab_images/stab/sword' + str(i) + '.png').convert_alpha()
			#adjust width height / 10 to screen size
			self.sword_sprites.append(pg.transform.scale(sword, ((width / 10), (height / 10))))
        
		self.current_sprite = 0
		self.image = self.sword_sprites[self.current_sprite]

		self.rect = self.image.get_rect()
		self.rect.bottomright = [xpos, ypos]

	def animation_start(self):
		self.attack_animation = True

	def animate(self, speed): #attacker is always speedorder[0], target enemy list[0]
		if self.attack_animation == True:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.sword_sprites):
				self.current_sprite = 0
				self.attack_animation = False
				self.image = self.sword_sprites[int(self.current_sprite)]
				melee_attack(States.acting, States.room_monsters[0])
				return True #triggers next attacker

		self.image = self.sword_sprites[int(self.current_sprite)]

class Blast(pg.sprite.Sprite):
	def __init__(self, xpos, ypos, spell):
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
		self.rect.topleft = [(xpos + (States.width / 16)), (ypos - (States.width / 27))] 

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
	def __init__(self, xpos, ypos):
		super().__init__()
		self.attack_animation = False
		self.claw_sprites = []
		claw = pg.image.load('./ab_images/claw/claw.png').convert_alpha()
		HEIGHT = claw.get_height()
		WIDTH = claw.get_width()
		SIZE_SCALAR = 10

		for i in range(10):
			#CLAW_ROTATION = pg.transform.rotozoom(claw, ((i * -9) + 45), 1)
			CLAW_ROTATION = pg.transform.rotate(claw, ((i * -9) + 45))
			self.claw_sprites.append(pg.transform.scale(CLAW_ROTATION, ((WIDTH / SIZE_SCALAR), (HEIGHT / SIZE_SCALAR))))
        
		self.current_sprite = 0
		self.image = self.claw_sprites[self.current_sprite]
		self.rect = self.image.get_rect()
		self.rect.center = [xpos, ypos]
		
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
