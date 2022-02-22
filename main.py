import os
import pygame
import sys
from math import *
import math
from pygame.locals import *
import csv

pygame.init()
screen_width = 1000
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Worms Game")

clock = pygame.time.Clock()
FPS = 60

#gravité
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 8

moving_left = False
moving_right = False
grenade = False
grenade_thrown = False
rocket = False
rocket_thrown = False
grenade_img = pygame.image.load("img/Grenade/0.png").convert_alpha()
rocket_img = pygame.image.load("img/Rocket/0.png").convert_alpha()
caisse_img = pygame.image.load("img/ObjetCassable/caisse.png").convert_alpha()
caisse_casse_img = pygame.image.load("img/ObjetCassable/DestructibleObject.png").convert_alpha()
health_box_img = pygame.image.load("img/ObjetCassable/health_box.png").convert_alpha()
rocket_box_img = pygame.image.load("img/ObjetCassable/rocket_box.png").convert_alpha()
item_boxes = {
    "Health" : health_box_img,
    "Rocket" : rocket_box_img
}
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/tile/{x}.png")
    img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    img_list.append(img)
BG=(144,201,120)
# Variable COLOR
RED=(255,0,0)
WHITE = (255, 255 , 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
Tour = 0
font = pygame.font.SysFont("ROBOTO",30)
g = 9.8
def trajectoire(angle,x,y0):
    val = 9.8*(pow(x,2)/(2*pow(50,2)*pow(cos(angle),2)))+tan(angle)*x+y0
    return val

def calculeAngle():
    x = 0
    y = 0
    angle = 0
    for i in pygame.mouse.get_pos():
        if x == 0:
            x = i
        else:
            y = i
    for allplayer in allplayer_group:
        if allplayer.turn_play:
            angle = 90-(math.degrees(math.atan(abs(allplayer.rect.x+allplayer.image.get_width() - x) / abs(300 - y))))
    return angle
def draw_text(text,font,text_color,x,y):
    img = font.render(text, True, text_color)
    screen.blit(img,(x,y))

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen,RED,(0,300),(screen_width,300))

class Character(pygame.sprite.Sprite):
    def __init__(self,char_type, x, y, scale, speed):
        super().__init__()
        self.alive = True #vivant ou tuer
        self.time_round = 300
        self.turn_play = False
        self.char_type = char_type
        self.speed = speed
        self.health = 100
        self.max_health = 100
        self.direction = 1
        self.vel_y = 0
        self.arm = "Grenade"
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = [] #list photo action
        self.frame_index = 0
        self.action = 0  # choisir actions
        self.update_time = pygame.time.get_ticks()


        animation_types=["Idle","Run","Jump","Dead"]
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f"img/{char_type}/{animation}")) # compter le nombre de photos dans le fichier
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{char_type}/{animation}/{i}.png")
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    def move(self, moving_left, moving_right, player_round):
        dx = 0
        dy = 0
        if player_round:
            if moving_left:
                dx = -self.speed
                self.flip=True
                self.direction = -1
                self.time_round -= 1
            #gauche
            if moving_right:
                dx = self.speed
                self.flip=False
                self.direction = 1
                self.time_round -= 1
            #droite
            if self.jump == True and self.in_air == False:
                self.vel_y = -11
                self.jump = False
                self.in_air = True
                self.time_round -= 1
            #saute
        self.vel_y += GRAVITY
        if self.vel_y >10:
            self.vel_y
        dy += self.vel_y
        for tile in world.Objet_list:
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >=0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        self.rect.x += dx
        self.rect.y += dy
    def set_gravity(self):
        dx = 0
        dy = 0
        self.vel_y += GRAVITY
        dy += self.vel_y
        for tile in world.Objet_list:
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >=0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        self.rect.x += dx
        self.rect.y += dy
    def update(self,player_round):
        self.update_animation(player_round)
        self.check_alive()

    def update_animation(self,player_round):
        if player_round:
            ANIMATION_COOLDOWN = 75
            #mise à jour d'animation
            self.image = self.animation_list[self.action][self.frame_index]
            #temps écoulé depuis le mise à jour
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.frame_index += 1
                self.update_time = pygame.time.get_ticks()
            # s'il dépasse la nombre d'images dans le répertoire
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action ==3:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def update_action(self,new_action):

        if self.action != new_action:
            self.action = new_action
        #mise à jour d'action choisie
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.turn_play = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip, False), self.rect)

class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes.get(self.item_type)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        if pygame.sprite.collide_rect(self,player):
            if self.item_type == "Health":
                player.health+=25
                if player.health >player.max_health:
                    player.health = player.max_health
            if self.item_type == "Rocket":
                player.arm = "Rocket"
            self.kill()
        if pygame.sprite.collide_rect(self,player2):
            if self.item_type == "Health":
                player2.health += 25
                if player2.health >player2.max_health:
                    player2.health = player2.max_health
            if self.item_type == "Rocket":
                player2.arm = "Rocket"
            self.kill()



class HealthBar():
    def __init__(self,x,y,health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    def draw(self,health):
        #mise à jour de vie
        self.health = health
        #pourcentage entre le rouge et vert
        ratio = self.health / self.max_health
        pygame.draw.rect(screen,BLACK, (self.x - 2,self.y -2 ,154 , 24))
        pygame.draw.rect(screen,RED,(self.x,self.y,150,20))
        pygame.draw.rect(screen,GREEN,(self.x,self.y,150 * ratio,20))


class Rocket(pygame.sprite.Sprite):
    def __init__(self,x,y,direction,scale):
        super().__init__()
        self.vel_y = -11
        self.speed = 7
        self.scale = scale
        img = pygame.transform.scale(rocket_img,(int(caisse_img.get_width() * scale), int(caisse_img.get_height() * scale)))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        #condition rocket et le sol
        for tile in world.Objet_list:
            if tile[1].colliderect(self.rect):
                self.kill()
                explosion = Explosion(self.rect.x, self.rect.y, 1)
                explosion_group.add(explosion)
        #mise à jour rocket position
        self.rect.x += dx
        self.rect.y += dy
        for allplayer in allplayer_group:
            if pygame.sprite.collide_rect(self, allplayer):
                allplayer.health -= 30
                self.kill()
                explosion = Explosion(self.rect.x, self.rect.y, 1)
                explosion_group.add(explosion)

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        #condition grenade et le sol
        for tile in world.Objet_list:
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >=0:
                    self.vel_y = 0

                    dy = tile[1].top - self.rect.bottom
        #condition reflet grenade
        if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
            self.direction *= -1
        #mise à jour grenade position
        self.rect.x += dx
        self.rect.y += dy
        #grenade explosion temps
        self.timer -=1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x,self.rect.y,1)
            explosion_group.add(explosion)
            #explose damage dans une cercle
            for allplayer in allplayer_group:
                if abs(self.rect.centerx - allplayer.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - allplayer.rect.centery) < TILE_SIZE * 2:
                    allplayer.health -= 20
                if abs(self.rect.centerx - allplayer.rect.centerx) < TILE_SIZE * 3 and abs(self.rect.centery - allplayer.rect.centery) < TILE_SIZE * 3:
                    allplayer.health -= 10
            for caissee in caisse_group:
                if abs(self.rect.centerx - caissee.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - caissee.rect.centery) < TILE_SIZE * 2:
                    caissee.update()

class World():
    def __init__(self):
        self.Objet_list = []
    def process_data(self,data):
        for y,row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >=0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile == 0 or tile == 1 or tile == 2:
                        self.Objet_list.append(tile_data)
                    if tile == 6:
                        player = Character("character",x * TILE_SIZE,y * TILE_SIZE, 0.15, 5)
                        health_bar = HealthBar(10, 40, player.health, player.health)
                        player_group.add(player)
                        allplayer_group.add(player)
                        player.turn_play = True
                    if tile == 7:
                        player2 = Character("character", x * TILE_SIZE, y * TILE_SIZE, 0.15, 5)
                        health_bar2 = HealthBar(screen_width - 160, 40, player2.health, player2.health)
                        player2_group.add(player2)
                        allplayer_group.add(player2)
                    if tile == 4:
                        item_box = ItemBox("Rocket", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    if tile == 5:
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
        return player,health_bar,player2,health_bar2
    def draw(self):
        for tile in self.Objet_list:
            screen.blit(tile[0],tile[1])

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        super().__init__()
        self.images = []
        for num in range(5):
            img = pygame.image.load(f"img/explosion/{num}.png").convert_alpha()
            img = pygame.transform.scale(img,(int(img.get_width() * scale),int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    def update(self):
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
class Caisse(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        super().__init__()
        self.scale = scale
        img = pygame.transform.scale(caisse_img, (int(caisse_img.get_width() * scale), int(caisse_img.get_height() * scale)))
        imgCassé = pygame.transform.scale(caisse_casse_img, (int(caisse_casse_img.get_width() * scale), int(caisse_casse_img.get_height() * scale)))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.images = []
        self.images.append(img)
        self.images.append(imgCassé)
    def update(self):
        self.image = self.images[1]
grenade_group = pygame.sprite.Group()
rocket_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
caisse_group = pygame.sprite.Group()
allplayer_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player2_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
#item_box = ItemBox("Health",100,260)
#item_box_group.add(item_box)
#item_box = ItemBox("Rocket",500,260)
#item_box_group.add(item_box)
#player = Character("character",200, 200, 0.15, 5)
#health_bar = HealthBar(10, 40, player.health, player.health)
#player2 = Character("character",400, 200, 0.15, 5)
#health_bar2 = HealthBar(screen_width - 160, 40, player2.health, player2.health)
#caisse = Caisse(500,300-caisse_img.get_height(),2)

#caisse_group.add(caisse)


#map
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
with open(f'0.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

world = World()
player,health_bar,player2,health_bar2 = world.process_data(world_data)
run = True
#Affichage
while run:
    clock.tick(FPS)
    draw_bg()
    world.draw()
    #affichage barre de vie
    draw_text("PLAYER 1", font, WHITE, 10, 10)
    health_bar.draw(player.health)
    draw_text("PLAYER 2", font, WHITE, screen_width - 110, 10)
    health_bar2.draw(player2.health)
    #donne la gravité à ce qui ne jouent pas
    for allplayer in allplayer_group:
        if not allplayer.turn_play:
            allplayer.set_gravity()
            allplayer.update(True)
            allplayer.update_animation(True)
        if allplayer.turn_play and allplayer.alive:
            allplayer.move(moving_left, moving_right, True)
            allplayer.update(True)
            allplayer.update_animation(True)
        allplayer.draw()
    rocket_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    grenade_group.draw(screen)
    rocket_group.draw(screen)
    explosion_group.draw(screen)
    caisse_group.draw(screen)
    item_box_group.draw(screen)

    #mise à jour d'actions
    for allplayer in allplayer_group:
        if allplayer.alive and allplayer.turn_play:
            if grenade and grenade_thrown == False and allplayer.arm == "Grenade":
                grenade = Grenade(allplayer.rect.centerx + (allplayer.direction), allplayer.rect.top,allplayer.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
            if rocket and rocket_thrown == False and allplayer.arm == "Rocket":
                rocket = Rocket(allplayer.rect.centerx + (allplayer.direction*50), allplayer.rect.top+(allplayer.direction*-10),allplayer.direction,0.8)
                rocket_group.add(rocket)
                rocket_thrown = True
            if allplayer.in_air:
                allplayer.update_action(2)
            elif moving_left or moving_right:
                allplayer.update_action(1)
            else:
                allplayer.update_action(0)
    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for allplayer in allplayer_group:
                    if allplayer.turn_play:
                        if allplayer.direction == -1:
                            for x in range(0, -1000, -1):
                                y = trajectoire(45, x, 300)
                                pygame.draw.rect(screen, RED,
                                                 pygame.Rect(allplayer.rect.x + x, y, 2,
                                                             2))
                                pygame.display.flip()
                        else:
                            for x in range(0, -1000, -1):
                                y = trajectoire(45, x, 300)
                                pygame.draw.rect(screen, RED,
                                                 pygame.Rect(allplayer.rect.x - x + allplayer.image.get_width(), y, 2,
                                                             2))
                                pygame.display.flip()
                        break

        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_ESCAPE :
                run = False
            if event.key == pygame.K_a:
                grenade = True
                rocket = True
            for allplayer in allplayer_group:
                if event.key == pygame.K_z and allplayer.alive:
                    allplayer.jump = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_a:
                grenade = False
                grenade_thrown = False
                rocket = False
                rocket_thrown = False
                next = False
                #Changement de tour apres tir
                for allplayer in allplayer_group:
                    Tour += 1
                    if allplayer.alive:
                        if next:
                            allplayer.turn_play = True
                            Tour = 0
                            break
                        if allplayer.turn_play:
                            allplayer.turn_play = False
                            next = True

                    if Tour == len(allplayer_group):
                        for allplayer in allplayer_group:
                            if allplayer.alive:
                                allplayer.turn_play = True
                                Tour = 0
                                break


    pygame.display.update()


