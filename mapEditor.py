import pygame,sys,random, pickle, lueString
from pygame.locals import * 

WIDTH = 800
HEIGHT = 600
BLACK = (0,0,0)
WHITE = (255,255,255)


class Camera():
	def __init__(self, width,height):
		self.state = Rect(0,0,width,height)#self.state basically is the offset
		
	def apply(self, target):#Take the position of the wall and add the offset to blit it correctly
		return target.rect.move(self.state.topleft)
		
	def update(self, target):#Take the players position and change the offset accordingly
		self.state = self.camera_func(self.state, target)
	
	def camera_func(self, camera, target_rect):#sets the new pos for the camera
		left, top, _, _ = target_rect
		_, _, w, h = camera
		left, top, _, _ = -left, -top, w, h

		return Rect(left, top, w, h)


class MapEditor():
	
	def __init__(self):
		pygame.init()
		self.clock = pygame.time.Clock()
		pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE)
		pygame.display.set_caption("kamera testailuu")
		self.screen = pygame.display.get_surface()
		self.menu = pygame.Surface((80,600))
		self.menu.fill((140,140,140))
		self.menu_items = pygame.sprite.Group()
		self.WallSprites = pygame.sprite.Group()
		self.setupList = []
		self.spriteList = []
		self.allSprites = pygame.sprite.Group()
		self.player = Player(30,30)
		self.allSprites.add(self.player)
		self.font = pygame.font.SysFont(None, 36)
		self.lue = lueString.lue(self.screen, self.font,(WIDTH-500,HEIGHT-40)) 
		self.stepfont = pygame.font.SysFont("Arial", 16)
		self.normfont = pygame.font.SysFont("Arial", 26)
		self.controls = pygame.image.load("graphics/controls1.PNG").convert()
		self.controls.set_colorkey((255,255,255))
		self.camera = Camera(800,800)
		self.start_pos_set = False
		self.bgset= False
		self.bgfile = None
		self.scroll_step = 5
		
	def run(self):
		self.offset = Rect(1,1,WIDTH,HEIGHT)
		left = right = up = down = False
		rotate = onlyheight = onlywidth = False
		bgset = False
		self.create_menu()
		while True:
			self.clock.tick(90)
			#Events
			
			for event in pygame.event.get():#Event handling
				if event.type == QUIT:
					pygame.quit()
					sys.exit(0)					
					#This part takes input and calls change_speed to move the player
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_LEFT:
						left = True
					elif event.key == pygame.K_RIGHT:
						right = True
					elif event.key == pygame.K_UP:
						up = True
					elif event.key == pygame.K_DOWN:
						down = True
					elif event.key == pygame.K_LSHIFT:
						onlywidth = True
					elif event.key == pygame.K_LCTRL:
						onlyheight = True
					elif event.key == pygame.K_LALT:
						rotate = True
					elif event.key == pygame.K_s:
						self.save_map()
					elif event.key == pygame.K_l:
						self.clear()
						self.load_map()
					elif event.key == pygame.K_c:
						self.clear()
					elif event.key == pygame.K_F1:
						self.player.change_dimensions(500, 5)
					elif event.key == pygame.K_F2:
						self.player.change_dimensions(5, 500)
					elif event.key == pygame.K_F3:
						self.player.change_dimensions(200, 200)
					elif event.key == pygame.K_F4:
						self.player.change_dimensions(700, 30)
					elif event.key == pygame.K_F5:
						self.player.change_dimensions(30, 30)
					elif event.key == pygame.K_0:
						self.player.change_type(0)
					elif event.key == pygame.K_1:
						self.player.change_type(1)
					elif event.key == pygame.K_2:
						self.player.change_type(2)
					elif event.key == pygame.K_3:
						self.player.change_type(3)
					elif event.key == pygame.K_4:
						self.player.change_type(4)
					elif event.key == pygame.K_5:
						self.player.change_type(5)
					elif event.key == pygame.K_9:
						self.player.change_type(9)
					elif event.key == pygame.K_KP_PLUS:	
						self.scroll_step += 1
						print("+step")
					elif event.key == pygame.K_KP_MINUS:	
						if not self.scroll_step < 2:
							self.scroll_step -= 1
							print("-step")
						
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
					elif event.key == pygame.K_LSHIFT:
						onlywidth = False
					elif event.key == pygame.K_LCTRL:
						onlyheight = False
					elif event.key == pygame.K_LALT:
						rotate = False
							
							## MOUSE EVENTS
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if event.dict["button"]==1:
						self.mouse1()
					elif event.dict["button"]==3:
						kill_list = pygame.sprite.spritecollide(self.player, self.WallSprites,True)
						for wall in kill_list:
							if wall.type == 0:
								self.start_pos_set = False
							self.spriteList.remove(wall)
					elif event.dict["button"]==4:#scrolling up
						print("ylös")
						if onlywidth:
							self.player.change_size(self.scroll_step,0)
						elif onlyheight:
							self.player.change_size(0,self.scroll_step)
						#elif rotate:
						#	self.player.rotate(10)
						else:
							self.player.change_size(self.scroll_step,self.scroll_step)
					elif event.dict["button"]==5:#scrolling down
						print("alas")
						if onlywidth:
							self.player.change_size(-self.scroll_step,0)
						elif onlyheight:
							self.player.change_size(0,-self.scroll_step)
						#elif rotate:
						#	self.player.rotate(-10)
						else:
							self.player.change_size(-self.scroll_step,-self.scroll_step)
							
			self.move(left,right,up,down)
			self.camera.update(self.offset)			
			self.allSprites.update(self.offset.x, self.offset.y)
			self.screen.fill(BLACK)#Fill background with color (BLACK)
			if self.bgset:#If there is a background image set, blit it
				self.screen.blit(self.backgroundimg,(-self.offset.x,-self.offset.y))
			self.screen.blit(self.controls, (100,0))#Blit the controls to the screen
			
			for item in self.menu_items:# keep the menu items at the left side of the screen
				item.rect.y = item.helpy +self.offset.y
				item.rect.x = 0 +self.offset.x
			for wall in self.spriteList:#Blit every sprite
				self.screen.blit(wall.image, self.camera.apply(wall))
			self.screen.blit(self.player.image, self.camera.apply(self.player))#blit player (mouse)
			self.screen.blit(self.menu, (0,0))#Blit the the menu
			if pygame.font:# Blit the text that shows the scroll_step
				step_text = self.stepfont.render("Scroll step: %d" %(self.scroll_step) ,2, (255, 255, 225))
				self.screen.blit(step_text, (WIDTH-100,16))
			pygame.display.flip()#update the screen
		
		pygame.quit()
	def set_scrollstep(self):
		self.lue.lue()	
		try:
			self.scroll_step = int(self.lue.getSana())
			if self.scroll_step < 1:
				self.scroll_step = 1
		except:
			print("Invalid input!")
	def mouse1(self):
		
		if self.player.rect.x < self.menu_items.sprites()[0].rect.right:
			self.player.change_type(1)
			x, y = self.player.image.get_size()
			self.player.change_dimensions (1,1)
			check = pygame.sprite.spritecollide(self.player, self.menu_items, False)
			for item in check:
				if item.type == 10:
					self.load_bg()
				elif item.type == 11:
					self.set_scrollstep()
				else:
					self.player.change_type(item.type)
				print(item.type)
			self.player.change_dimensions (x,y)
		elif self.player.type == 0 and self.start_pos_set:
			print("You can only have one starting position set, please remove the old one")
		elif not(self.player.collide(self.WallSprites)):
			wall = Wall(self.player.rect.center,self.player.get_dimensions(),self.player.type)
			self.WallSprites.add(wall)
			self.spriteList.append(wall)
			if self.player.type == 0:
				self.start_pos_set = True
			print("Uusi sprite!")
			
	def load_bg(self):
		self.lue.lue()
		self.bgfile = self.lue.getSana()
		try:
			self.backgroundimg = pygame.image.load("maps/"+self.bgfile).convert()
			self.self.bgfile = "maps/"+self.bgfile
			self.bgset= True
		except:
			print("Fuck meh!! Load failed")
		
			
	def create_menu(self):
		menu_items = ["start","wall 1","wall 2","wall 3","wall 4","wall 5","wall 6","wall 7","wall 8","Stabber","Add background","scroll step"]
		y= 1
		type = 0
		for item in menu_items:
			button = Menu_item(y,item,type)
			self.menu_items.add(button)
			self.menu.blit(button.image,(0,y))
			y += 30
			type += 1
			
	def map_size(self):
				
		xmax = xmin = ymax = ymin = 0
		for sprite in self.WallSprites:
			
			if sprite.rect.x > xmax:
				xmax = sprite.rect.x
			elif sprite.rect.x < xmin:
				xmin =sprite.rect.x
			if sprite.rect.y > ymax:
				ymax = sprite.rect.y
			elif sprite.rect.y < ymin:
				ymin = sprite.rect.y
				
				
		return xmax,xmin,ymax,ymin
			
	def save_map_img(self, filename):
		print("kuvaa tallennetaan")
		xmax,xmin,ymax,ymin = self.map_size()
		print(xmax,xmin, "  ",ymax,ymin)
		x= (int)(xmax +abs(xmin))
		y= (int)(ymax+abs(ymin))
		print(x,"  ",y)
		imagesrf = pygame.Surface((x+100,y+100))
		for sprite in self.WallSprites:
			imagesrf.blit(sprite.image,(sprite.rect.x+abs(xmin), sprite.rect.y+abs(ymin)))
			print(sprite.rect.x, sprite.rect.y)
		filename = filename+".JPEG"
		pygame.image.save(imagesrf, filename)	

	
	def save_map(self, filename="taso"):
		self.lue.lue()
		filename = self.lue.getSana()
		self.save_map_img(filename)
		i = 0
		self.setupList = []
		for sprite in self.WallSprites:
			i += 1
			if sprite.save:
				self.setupList.append(sprite.get_data())
		if self.bgfile != None:
			self.setupList.append((self.bgfile,"bg"))
		try:
			with open("maps/"+filename, 'wb') as f:
				pickle.dump(self.setupList, f)
		except:
			print("Fuck meh!! Save failed")
		f.close()
		
			
	def load_map(self):
		
		self.lue.lue()
		filename = self.lue.getSana()
		try:
			with open("maps/"+filename, 'rb') as f:
				self.setupList = pickle.load(f)
		except:
			print("Fuck meh!! Load failed")
			return
				
		for setup in self.setupList:
			print(setup)
			if len(setup) < 3:
				print("ladataaan beegee")
				self.bgfile, type = setup
				self.backgroundimg = pygame.image.load(self.bgfile).convert_alpha()
				self.bgset = True
			else:
				pos, dimensions, type = setup
				wall = Wall(pos, dimensions, type)
				self.WallSprites.add(wall)
				self.spriteList.append(wall)
		
		f.close()
		
	def clear(self):
		for sprite in self.WallSprites:
			self.WallSprites.remove(sprite)
			del sprite
		self.spriteList = []
		self.WallSprites.empty()
		self.setupList = []
		self.start_pos_set = False
		self.bgset = False
	def move(self,left,right,up,down):
		if left:
			self.offset.x -= 5
		if right:
			self.offset.x += 5
		if up:
			self.offset.y -=5
		if down:
			self.offset.y += 5
			
class Player(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([x, y])
		self.dimensions =(x,y)
		self.image.fill((255,0,0))
		self.image.set_colorkey((255,255,255))
		self.rect = self.image.get_rect()
		self.rect.x = 400
		self.rect.y = 300
		self.speedx = 0
		self.speedy = 0
		self.x = x
		self.y = y
		self.rotation = 0
		self.type = 1
		self.change_type(1)
		
	def update(self,xoffset,yoffset):
		self.rect.center = pygame.mouse.get_pos()
		self.rect.x += xoffset 
		self.rect.y += yoffset 
		#self.check_type()
	
	def change_size(self, changeX,changeY):
		if self.type != 0 and self.type != 9:
			old_center = self.rect.center
			self.x = self.x+changeX
			self.y = self.y+changeY
			if self.x < 5:
				self.x = 5
			if self.y < 5:
				self.y = 5
			self.image = pygame.Surface([self.x, self.y])
			self.rect = self.image.get_rect()
			self.rect.center = old_center
			self.apply_texture()
			
	def change_dimensions(self, x, y):
		if self.type != 0 and self.type != 9:
			old_center = self.rect.center
			self.x = x
			self.y = y
			self.image = pygame.Surface([self.x, self.y])
			self.rect = self.image.get_rect()
			self.rect.center = old_center
			self.apply_texture()
			
	def change_type(self,type):
		self.type = 1
		if type == 1:
			self.texture = pygame.image.load("graphics/tile1.png").convert()
		elif type == 2:
			self.texture = pygame.image.load("graphics/tile2.png").convert()
		elif type == 3:
			self.texture = pygame.image.load("graphics/tile3.png").convert()
		elif type == 4:
			self.texture = pygame.image.load("graphics/tile4.png").convert()
		elif type == 5:
			self.texture = pygame.image.load("graphics/tile5.png").convert()
		elif type == 0:
			self.texture = pygame.image.load("graphics/pelaaja_oikea_0.png").convert()
			self.change_dimensions(40,45)
		elif type == 9:
			self.texture = pygame.image.load("graphics/puukottaja0.png").convert()
			self.change_dimensions(41,57)
		self.type = type
		self.apply_texture()
	
	def get_dimensions(self):
		return (self.x,self.y)
		
	def rotate(self, rotation):#not in use atm
		self.rotation += rotation
		tmpimg = self.image
		old_center = self.rect.center
		self.image = pygame.transform.rotate(tmpimg, self.rotation)
		self.rect = self.image.get_rect()
		self.rect.center = old_center
	
	def collide(self, wallSprites):
		hits = False;
		hit_list = pygame.sprite.spritecollide(self, wallSprites, False)
		if len(hit_list) > 0:
			hits = True
		return hits
		
	def remove_sprite(self, wallSprites):
		hits = False;
		hit_list = pygame.sprite.spritecollide(self, wallSprites, False)
		return hit_list

	def apply_texture(self):
		width,height = self.image.get_size()
		xstep,ystep = self.texture.get_size()
		for y in range(0,height,ystep):
			for x in range (0,width,xstep):
				self.image.blit(self.texture,(x,y))
			
		
class Wall(pygame.sprite.Sprite):
	def __init__(self, pos, dimensions,type):
		pygame.sprite.Sprite.__init__(self)
		self.dimensions = dimensions
		self.image = pygame.Surface(self.dimensions)
		self.image.fill(WHITE)
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.type = type
		self.check_type()
		self.movx = 0
		self.movy = 0
		self.save = True;
		self.destroyable = False
	
	def get_data(self):
		return self.rect.center, self.dimensions, self.type
	def set_destroyable(self):
		if self.destroyable:
			self.destroyable = False
		else:
			self.destroyable = True
		
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
		elif self.type == 0:
			texture = pygame.image.load("graphics/pelaaja_oikea_0.png").convert()
		elif self.type == 9:
			texture = pygame.image.load("graphics/puukottaja0.png").convert()

		self.apply_texture(texture)
		
	def apply_texture(self,texture):
		width,height = self.dimensions
		xstep,ystep = texture.get_size()
		for y in range(0,height,ystep):
			for x in range (0,width,xstep):
				self.image.blit(texture,(x,y))
		
class Menu_item(pygame.sprite.Sprite):
	def __init__(self, y, text, type):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((80,29))
		self.image.fill(WHITE)
		font = pygame.font.SysFont("Arial", 12)
		buttontext = font.render(text,2,BLACK)
		self.image.blit(buttontext, (0,0))
		self.rect = self.image.get_rect()
		self.helpy = y
		self.rect.x = 0
		self.rect.y = y
		self.type = type
		#print(self.rect.top," - ",self.rect.bottom)
		
def main():
	MapEditor().run()
	
if __name__=="__main__":
	main()