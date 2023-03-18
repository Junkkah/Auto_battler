import pygame as pg, sys
from states import States
from objects import Hero, Monster

def melee_attack(attacker, target):
	States.acting.animation = False
	target.data["health"] -= attacker.data["damage"]
	target.health -= attacker.damage
    

class Stab(pg.sprite.Sprite):
	def __init__(self, xpos, ypos):
		super().__init__()
		self.attack_animation = False
		self.sword_sprites = [] 
		sword_image = pg.image.load('auto_battle/ab_kuvat/stab/sword1.png')
		height = sword_image.get_height()
		width = sword_image.get_width()
		
		for i in range(1, 11):
			sword = pg.image.load('auto_battle/ab_kuvat/stab/sword' + str(i) + '.png')
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

class Slash(pg.sprite.Sprite):
	def __init__(self, xpos, ypos):
		super().__init__()
		self.attack_animation = False
		self.claw_sprites = []
		claw1 = pg.image.load('auto_battle/ab_kuvat/claw/claw1.png')
		height = claw1.get_height()
		width = claw1.get_width()

		for i in range(10):
			claw = pg.image.load('auto_battle/ab_kuvat/claw/claw1.png')
			clawr = pg.transform.rotozoom(claw, ((i * -9) + 45), 1)
			self.claw_sprites.append(pg.transform.scale(clawr, ((width / 10), (height / 10))))
        
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
