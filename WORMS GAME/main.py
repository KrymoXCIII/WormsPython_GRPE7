import os
import pygame
import sys
from pygame.locals import *

pygame.init()
screen_width = 1000
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Worms Game")

clock = pygame.time.Clock()
FPS = 60

#gravité
GRAVITY = 0.75
TILE_SIZE = 40
moving_left = False
moving_right = False
grenade = False
grenade_thrown = False
grenade_img = pygame.image.load("img/Grenade/0.png").convert_alpha()
caisse_img = pygame.image.load("img/ObjetCassable/caisse.png").convert_alpha()
caisse_casse_img = pygame.image.load("img/ObjetCassable/DestructibleObject.png").convert_alpha()
BG=(144,201,120)
# Variable COLOR
RED=(255,0,0)
WHITE = (255, 255 , 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
Tour = 0
font = pygame.font.SysFont("ROBOTO",30)

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
        self.direction = 1
        self.vel_y = 0
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
        dy += self.vel_y
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False
        self.rect.x += dx
        self.rect.y += dy
    def set_gravity(self):
        dx = 0
        dy = 0
        self.vel_y += GRAVITY
        dy += self.vel_y
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False
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
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        #condition grenade et le sol
        if self.rect.bottom + dy >300:
            dy = 300 - self.rect.bottom
            self.speed = 0
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
explosion_group = pygame.sprite.Group()
caisse_group = pygame.sprite.Group()
allplayer_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player2_group = pygame.sprite.Group()

player = Character("character",200, 200, 0.2, 5)
health_bar = HealthBar(10, 40, player.health, player.health)
player2 = Character("character",400, 200, 0.2, 5)
health_bar2 = HealthBar(screen_width - 160, 40, player2.health, player2.health)
caisse = Caisse(500,300-caisse_img.get_height(),2)
player2_group.add(player2)
player_group.add(player)
allplayer_group.add(player)
allplayer_group.add(player2)
caisse_group.add(caisse)
player.turn_play = True
run = True
#Affichage
while run:
    clock.tick(FPS)
    draw_bg()
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
    grenade_group.update()
    explosion_group.update()
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    caisse_group.draw(screen)
    #mise à jour d'actions
    for allplayer in allplayer_group:
        if allplayer.alive and allplayer.turn_play:
            if grenade and grenade_thrown == False:
                grenade = Grenade(allplayer.rect.centerx + (allplayer.direction), allplayer.rect.top,allplayer.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
            if allplayer.in_air:
                allplayer.update_action(2)
            elif moving_left or moving_right:
                allplayer.update_action(1)
            else:
                allplayer.update_action(0)
    for event in pygame.event.get():
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
