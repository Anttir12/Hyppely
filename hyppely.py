import pygame,sys,random, pickle, lueString
from pygame.locals import * 
"""
Muutin animaatiota sillain et HETI kun vaihtaa suuntaa niin pelaajan kuvakin kääntyy ympäri
TODO:
	Animaatiot spritelle  DONE
	Grafiikat seinille DONE
	Taustakuva?
	ampuminen DONE
	Oma ERILLINEN fysiikka moottori. se olis hauska?
"""
BLACK = (0,0,0)
WHITE = (255,255,255)
WIDTH = 800
HEIGHT = 600 
FPS = 60
GRAVITY = 80#Pixels/second

class Creature(pygame.sprite.Sprite):
	
	def __init__(self, pos):
		self.left = False
		self.right = False
		self.up = False
		self.down = False
		self.yvelocity = 0
		self.help = 0#help variable, for the animation, for every x:th(fifth) load a new image
		self.frame = 0#Tells which frame to show in the animation
		self.facing_left = False
		self.rect = self.image.get_rect()
		self.rect.center = pos
		
	def ycollision(self):
		collide = False
		collision_list = pygame.sprite.spritecollide(self, self.walls, False)
		self.onground = False
		for collision in collision_list:
			if self.up:
				self.rect.top = collision.rect.bottom
				self.yvelocity = 0
				collide = True
			if self.down:
				self.rect.bottom = collision.rect.top
				self.onground = True
				self.yvelocity = 0
				collide = True

		return collide		
	
	
	def xcollision(self):	
		collide = False
		collision_list = pygame.sprite.spritecollide(self, self.walls, False)
		for collision in collision_list:
			if self.left:
				self.rect.left = collision.rect.right
				collide = True
			elif self.right:
				self.rect.right = collision.rect.left
				collide = True

		return collide	
		

	def move_x(self,x):
		self.rect.centerx += x
		return self.xcollision()
		
		
	def move_y(self,y):
		self.rect.centery += y			
		return self.ycollision()
		
	def gravity(self, seconds):

		self.yvelocity += GRAVITY*seconds
		if self.yvelocity > 800*seconds:
			self.yvelocity = 800*seconds
		if self.yvelocity >= 0:
			self.up = False
			self.down = True
		else:
			self.up = True
			self.down = False			


class Camera():
	def __init__(self, width,height):
		self.state = Rect(0,0,width,height)#self.state basically is the offset
		
	def apply(self, target):#Take the position of the wall and add the offset to blit it correctly
		return target.rect.move(self.state.topleft)
		
	def update(self, target):#Take the players position and change the offset accordingly
		self.state = self.camera_func(self.state, target.rect)
	
	def camera_func(self, camera, target_rect):#sets the new pos for the camera
		left, top, _, _ = target_rect
		_, _, w, h = camera
		left, top, _, _ = -left+(WIDTH/2), -top+(HEIGHT/2), w, h
		left = min(500, left)                           # stop scrolling at the left edge
		left = max(-(camera.width-WIDTH), left)  		# stop scrolling at the right edge
		top = max(-(camera.height-HEIGHT), top) 	# stop scrolling at the bottom
		top = min(150, top)                           # stop scrolling at the top
		return Rect(left, top, w, h)

class Tasohyppely():
	
	def __init__(self):
		pygame.init()
		self.clock = pygame.time.Clock()
		pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE)
		pygame.display.set_caption("Tasohyppely")
		self.screen = pygame.display.get_surface()
		self.wallSprites = pygame.sprite.Group()
		self.allBullets = pygame.sprite.Group()
		self.enemySprites = pygame.sprite.Group()
		self.spriteList = pygame.sprite.Group()
		self.setupList = []
		self.allSprites = pygame.sprite.Group()
		self.font = pygame.font.SysFont(None, 36)
		self.lue = lueString.lue(self.screen, self.font) 
		
	def run(self):
		
		while True:
			playing = True
			self.lue.lue()
			filename = self.lue.getSana()
			self.load_map(filename)
			self.camera = Camera(self.map_width,self.map_height+200)
			left = right = up = down = False
			while playing:
				milliseconds = self.clock.tick(FPS)
				seconds = milliseconds / 1000.0
				
				for event in pygame.event.get():#Event handling
					#print(event)
					if event.type == QUIT:
						pygame.quit()
						sys.exit(0)
						
						#This part takes input
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_LEFT:
							left = True	
						elif event.key == pygame.K_RIGHT:
							right = True	
						elif event.key == pygame.K_UP:
							up = True		
						elif event.key == pygame.K_DOWN:
							down = True	
						elif event.key == pygame.K_r:
							playing = False
						elif event.key == pygame.K_SPACE:
							bullet = Projectile(self.player.get_position(),self.player.facing_left,self.spriteList)
							self.allBullets.add(bullet)
							self.allSprites.add(bullet)
								#keyups
					elif event.type == pygame.KEYUP:
						if event.key == pygame.K_LEFT:
							left = False	
						elif event.key == pygame.K_RIGHT:
							right = False
						elif event.key == pygame.K_UP:
							up = False
						elif event.key == pygame.K_DOWN:
							down = False

						
								## MOUSE EVENTS
					if event.type == pygame.MOUSEBUTTONDOWN:
						if event.dict["button"]==1:
							pass
				
				self.check_collision()
				self.screen.fill((190,190,190))
				self.camera.update(self.player)#Update camera
				self.player.update(left,right,up,down, seconds)#update player		
				self.allBullets.update(seconds)#update bullets
				self.enemySprites.update(seconds)#update enemies
				for object in self.allSprites:
					self.screen.blit(object.image, self.camera.apply(object))
				pygame.display.update(Rect(0,0,WIDTH,HEIGHT))#update the screen
				up = False
				if not playing:
					self.restart()
					
	def check_collision(self):
		hit_list = pygame.sprite.spritecollide(self.player, self.enemySprites, True)
		for hit in hit_list:
			print("Ouch", hit.id)
			self.player.hp -= 1
			if self.player.checkHP():
				pass
				#TODO: MITÄ TAPAHTUU KUN KUOLEEE??????
				
	def restart(self):
		self.screen.fill((190,190,190))
		self.wallSprites.empty()
		self.allBullets.empty()
		self.enemySprites.empty()
		self.spriteList.empty()
		self.allSprites.empty()
		self.setupList = []
		self.player.kill()
		return False
		
	def load_map(self, filename="taso"):#loads map
		self.map_width = 0
		self.map_height = 0
		id = 0
		self.start_pos= (0,0)
		try:
			with open("maps/"+filename, 'rb') as f:#open file
				self.setupList = pickle.load(f)#saves the contents of the file in a list
			for setup in self.setupList:#Uses the data provided by the file to build the world
				pos, dimensions, type = setup
				if type == 0:
					self.start_pos = pos
				elif type == 9:
					enemy = Enemy(pos,type, id)
					self.enemySprites.add(enemy)
					self.allSprites.add(enemy)
					self.spriteList.add(enemy)
				else:
					wall = Wall(pos, dimensions,type, id)
					self.wallSprites.add(wall)
					self.allSprites.add(wall)
					self.spriteList.add(wall)				
					if wall.rect.right > self.map_width:#gets the width of the map 
						self.map_width = wall.rect.right
					if wall.rect.bottom > self.map_height:#gets the height of the map
						self.map_height = wall.rect.bottom
				id += 1#Every object has its own unique ID (mostly for debugging/testing purposes)
		except:
			print ("Unexpected error:", sys.exc_info()[0])
			raise
			print("Fuck meh!! Load failed")
		f.close()
		self.player = Player(self.wallSprites, self.start_pos)
		self.allSprites.add(self.player)
		for enemy in self.enemySprites:
			enemy.walls = self.wallSprites
			
class Player(Creature):

	def __init__(self, walls,pos):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("graphics/pelaaja_oikea_0.png").convert()
		self.image.set_colorkey(WHITE)
		super().__init__(pos)
		#Loads the png files to list for the running animation. 
		self.right_image_list = []
		self.left_image_list = []
		self.load_textures()
		self.walls = walls#List of every wall in the map (for collision detection etc.)
		self.onground = False
		self.hp = 2
		
	def update(self,left,right,up,down,seconds):
		if left and right:
			left = right = False
		self.left = left
		self.right = right
		self.up = up
		self.down = down
		self.speed = 300# set the speed of the sprite(pixels/second)
		self.speed = int(self.speed * seconds)


			
		self.help += 1	
		if self.left:
			if not self.facing_left:
				self.frame = 0
				self.help = 6
				self.facing_left = True
			#replace image with a new one every fifth frame
			if self.help > 5:
				self.oldrect = self.rect
				self.image = self.left_image_list[self.frame]
				self.image.set_colorkey(WHITE)
				self.rect = self.oldrect
				self.frame += 1
				if self.frame > 5:
					self.frame = 0
				self.help = 0
				
			for i in range(0,self.speed):
				if self.move_x(-1):
					break
			
		elif self.right:
			if self.facing_left:
				self.frame = 0
				self.help = 6
				self.facing_left = False
			#replace image with a new one every fifth frame
			if self.help > 5:
				self.oldrect = self.rect
				self.image = self.right_image_list[self.frame]
				self.image.set_colorkey(WHITE)
				self.rect = self.oldrect
				self.frame += 1
				if self.frame > 5:
					self.frame = 0				
				self.help = 0
				
			for i in range(0,self.speed):
				if self.move_x(1):
					break
					
		
		
		elif not self.right and not self.left:
			#stance
			if self.facing_left:
				self.image = self.left_image_list[0] 
				self.image.set_colorkey(WHITE)
			else:
				self.image = self.right_image_list[0]
				self.image.set_colorkey(WHITE)				
				
		if self.up:
			self.jump()
			
		self.gravity(seconds)#Add gravity

		if self.up:
			for i in range(0,int(-self.yvelocity)):
				if self.move_y(-1):
					break
			
		elif self.down:
			for i in range(0,int(self.yvelocity)):
				if self.move_y(1):
					break
	
	def jump(self):
		if self.onground:
			self.yvelocity = -21

	def get_position(self):
		return self.rect.center
	
	def set_x(self, x):
		self.rect.centerx = x
		
	def set_y(self, y):
		self.rect.centery = y
		
	def checkHP(self):
		dead = False
		if self.hp <= 0:
			self.kill()
			dead = True
		return dead
			
	def load_textures(self):
		self.right_image_list.append(pygame.image.load("graphics/pelaaja_oikea_0.png").convert())
		self.right_image_list.append(pygame.image.load("graphics/pelaaja_oikea_1.png").convert())
		self.right_image_list.append(pygame.image.load("graphics/pelaaja_oikea_2.png").convert())
		self.right_image_list.append(pygame.image.load("graphics/pelaaja_oikea_3.png").convert())
		self.right_image_list.append(pygame.image.load("graphics/pelaaja_oikea_2.png").convert())
		self.right_image_list.append(pygame.image.load("graphics/pelaaja_oikea_1.png").convert())
		#Makes a new list where the image is flipped vertically
		self.left_image_list = []
		for image in self.right_image_list:
			self.left_image_list.append(pygame.transform.flip(image,True,False))
	
	
class Wall(pygame.sprite.Sprite):
	def __init__(self, pos, dimensions, type, id):
		pygame.sprite.Sprite.__init__(self)
		self.dimensions = dimensions
		self.image = pygame.Surface(self.dimensions)
		self.image.fill(WHITE)
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.id = id
		self.type = type
		self.check_type()
		
	def get_id(self):
		return self.id
	
	def check_type(self):
		texture = self.image
		if self.type == 1:
			texture = pygame.image.load("graphics/tile1.png").convert()
		elif self.type == 2:
			texture = pygame.image.load("graphics/tile2.png").convert()
		elif self.type == 3:
			texture = pygame.image.load("graphics/tile3.png").convert()
		elif self.type == 4:
			texture = pygame.image.load("graphics/tile4.png").convert()
		elif self.type == 5:
			texture = pygame.image.load("graphics/tile5.png").convert()

		self.apply_texture(texture)
	
	def apply_texture(self,texture):
		width,height = self.dimensions
		for y in range(0,height,50):
			for x in range (0,width,50):
				self.image.blit(texture,(x,y))
				
class Projectile(pygame.sprite.Sprite):
	def __init__(self,pos,left,walls):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((6,3))
		self.image.fill((50,30,66))
		self.rect = self.image.get_rect()
		self.walls = walls
		self.rect.x, self.rect.y = pos
		self.dist_travelled = 0
		self.speed = 900 #speed pixels/second
		if left:
			self.move = -1
		else:
			
			self.move = 1
		
		
	def update(self,seconds):
		
		for i in range(0,int(self.speed*seconds)):
			self.rect.centerx += self.move
			self.collision()
		self.dist_travelled += self.speed*seconds
		if abs(self.dist_travelled) > 2000:
			self.kill()
			print("dist poks")
	
	def collision(self):
		collision_list = pygame.sprite.spritecollide(self, self.walls, False)
		for collision in collision_list:
			if collision.type == 9:
				collision.kill()
				print("Spläts")
		if len(collision_list) > 0:
			self.kill()
			
class Enemy(Creature):
	
	def __init__(self,pos,type,id):
		pygame.sprite.Sprite.__init__(self)
		self.load_textures()
		super().__init__(pos)
		self.type = type
		self.speed = 300
		self.id = id
		self.walls = None
		
	def load_textures(self,type=1):
		self.right_image_list =[]
		self.left_image_list =[]
		if type == 1:
			self.right_image_list.append(pygame.image.load("graphics/puukottaja0.png").convert())
			self.right_image_list.append(pygame.image.load("graphics/puukottaja1.png").convert())
			self.right_image_list.append(pygame.image.load("graphics/puukottaja2.png").convert())
			self.right_image_list.append(pygame.image.load("graphics/puukottaja3.png").convert())
			self.right_image_list.append(pygame.image.load("graphics/puukottaja2.png").convert())
			self.right_image_list.append(pygame.image.load("graphics/puukottaja1.png").convert())
			#Makes a new list where the image is flipped vertically
			for image in self.right_image_list:
				self.left_image_list.append(pygame.transform.flip(image,True,False))
			self.image = self.right_image_list[0]
		self.image.set_colorkey(WHITE)
		
	def update(self,seconds):
		self.xvelocity = self.speed# set the speed of the sprite(pixels/second)
		self.xvelocity = int(self.xvelocity * seconds)
		if self.xvelocity > 0:
			self.left = True
			self.right = False
		elif self.xvelocity < 0:
			self.right = True
			self.left = False
		self.help += 1	
		if self.left:
			if not self.facing_left:
				self.frame = 0
				self.help = 6
				self.facing_left = True
			#replace image with a new one every fifth frame
			if self.help > 5:
				self.oldrect = self.rect
				self.image = self.left_image_list[self.frame]
				self.image.set_colorkey(WHITE)
				self.rect = self.oldrect
				self.frame += 1
				if self.frame > 5:
					self.frame = 0
				self.help = 0
				
			for i in range(0,self.xvelocity):
				if self.move_x(-1):
					self.speed *= -1
					break
			
		elif self.right:
			if self.facing_left:
				self.frame = 0
				self.help = 6
				self.facing_left = False
			#replace image with a new one every fifth frame
			if self.help > 5:
				self.oldrect = self.rect
				self.image = self.right_image_list[self.frame]
				self.image.set_colorkey(WHITE)
				self.rect = self.oldrect
				self.frame += 1
				if self.frame > 5:
					self.frame = 0				
				self.help = 0
				
			for i in range(0,abs(self.xvelocity)):
				if self.move_x(1):
					self.speed *= -1
					break
					
		self.gravity(seconds)#Add gravity to the y axis
		if self.up:
			for i in range(0,int(-self.yvelocity)):
				if self.move_y(-1):
					break
			
		elif self.down:
			for i in range(0,int(self.yvelocity)):
				if self.move_y(1):
					break

			

	
def main():
	Tasohyppely().run()
	
if __name__=="__main__":
	main()