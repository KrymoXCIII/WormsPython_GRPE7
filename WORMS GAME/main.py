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

moving_left = False
moving_right = False
grenade = False
grenade_thrown = False
grenade_img = pygame.image.load("img/Grenade/0.png").convert_alpha()
BG=(144,201,120)
RED=(255,0,0)
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen,RED,(0,300),(screen_width,300))

class Character(pygame.sprite.Sprite):
    def __init__(self,char_type, x, y, scale, speed, ammo):
        super().__init__()
        self.alive = True #vivant ou tuer
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
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
    def move(self, moving_left,moving_right):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip=True
            self.direction = -1
        #gauche
        if moving_right:
            dx = self.speed
            self.flip=False
            self.direction = 1
        #droite
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        #saute
        self.vel_y += GRAVITY
        dy += self.vel_y
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False
        self.rect.x += dx
        self.rect.y += dy
    def update(self):
        self.update_animation()
        self.check_alive()
    def shoot(self):
        if self.ammo >0:
            #lancer grenade
            pass
        self.ammo-=1
    def update_animation(self):
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
            self.alive= False
            self.update_action(3)



    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip, False), self.rect)

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
        #mise à jour grenade position
        self.rect.x +=dx
        self.rect.y +=dy
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
        if pygame.sprite.spritecollide(player,grenade_group, False):
            if player2.alive:
                player2.health -=10
                self.kill()
        if pygame.sprite.spritecollide(player2,grenade_group, False):
            if player.alive:
                player.health -=10
                self.kill()

grenade_group = pygame.sprite.Group()

player = Character("character",200, 200, 0.2, 5, 3)
player2 = Character("character2",400, 200, 0.2, 5, 3)

run = True
#Affichage
while run:
    clock.tick(FPS)
    draw_bg()
    player.update_animation()
    player.move(moving_left, moving_right)
    player.draw()
    player.update()
    player2.draw()
    player2.update()
    grenade_group.update()
    grenade_group.draw(screen)
    #mise à jour d'actions
    if player.alive:
        if grenade and grenade_thrown == False:
            grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top,player.direction)
            grenade_group.add(grenade)
            grenade_thrown = True
        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)

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
            if event.key == pygame.K_z and player.alive:
                player.jump = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_a:
                grenade = False
                grenade_thrown = False

    pygame.display.update()
