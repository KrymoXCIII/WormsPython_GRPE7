import os
import pygame
import sys
from math import *
import math
from pygame.locals import *
import csv
import startButton
import random
from pygame import mixer

def main():
    pygame.init()
    mixer.init()
    screen_width = 1000
    screen_height = int(screen_width * 0.8)

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Worms Game")

    clock = pygame.time.Clock()
    FPS = 60

    # gravité
    GRAVITY = 0.75

    # coeficient de frottement
    k = 0.1

    # force du vent
    wind = 0

    ROWS = 16
    COLS = 150
    TILE_SIZE = screen_height // ROWS
    TILE_TYPES = 8

    start_game = False

    moving_left = False
    moving_right = False
    grenade = False
    grenade_thrown = False
    rocket = False
    rocket_thrown = False

    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1,0.0,5000)
    jump_music=pygame.mixer.Sound("jump.wav")
    jump_music.set_volume(0.5)
    explose_music=pygame.mixer.Sound("explose.wav")
    explose_music.set_volume(0.7)

    grenade_img = pygame.image.load("img/Grenade/0.png").convert_alpha()
    rocket_img = pygame.image.load("img/Rocket/0.png").convert_alpha()
    caisse_img = pygame.image.load("img/ObjetCassable/caisse.png").convert_alpha()
    health_box_img = pygame.image.load("img/ObjetCassable/health_box.png").convert_alpha()
    rocket_box_img = pygame.image.load("img/ObjetCassable/rocket_box.png").convert_alpha()
    item_boxes = {
        "Health": health_box_img,
        "Rocket": rocket_box_img
    }
    img_list = []
    for x in range(TILE_TYPES):
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)


    BG = (144, 201, 120)
    bg_Image =pygame.image.load("img/Background/background.jpg").convert_alpha()
    mini_restart_img = pygame.image.load('img/Menu/mini_restart.png').convert_alpha()
    exit_img = pygame.image.load('img/Menu/exit_btn.png').convert_alpha()
    restart_img = pygame.image.load('img/Menu/restart_btn.png').convert_alpha()
    map_0 = pygame.image.load('img/Menu/map0.png').convert_alpha()
    map_1 = pygame.image.load('img/Menu/map1.png').convert_alpha()
    map_2 = pygame.image.load('img/Menu/map2.png').convert_alpha()
    map_3 = pygame.image.load('img/Menu/map3.png').convert_alpha()
    # Variable COLOR
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    Tour = 0
    font = pygame.font.SysFont("ROBOTO", 30)
    EndGAME = False

    def path(direction, x0, y0, speed, angle, t):
        g = 9.8
        x = direction * t * speed * cos(angle) + x0
        y = (g / 2) * pow(-t, 2) + speed * math.sin(angle) * -t + y0
        return x, y

    def pathWithWind(direction, x0, y0, speed, angle, t, k, w):
        g = 9.8
        x = (x0 + (direction*(((speed) * cos(angle))/k) * (1-pow(e,-k*t)))) + t*w
        y = y0 - ((speed * math.sin(angle))/k + ((g / 2)/pow(k,2))) * (1-pow(e, -k*t)) + ((g / 2)*t)/k
        return x, y

    def calculeAngle():
        x,y = pygame.mouse.get_pos()
        angle = 0
        for allplayer in allplayer_group:
            if allplayer.turn_play and y != allplayer.rect.y:
                if allplayer.direction == 1:
                    if allplayer.rect.y<y:
                        angle = (
                        math.degrees(math.atan(
                            abs(allplayer.rect.x + allplayer.image.get_width() - x) / abs(allplayer.rect.y - y)))) -90
                    else:

                        angle = 90 - (
                            math.degrees(math.atan(
                                abs(allplayer.rect.x + allplayer.image.get_width() - x) / abs(allplayer.rect.y - y))))
                else:
                    if allplayer.rect.y<y:
                        angle = (
                        math.degrees(math.atan(
                            abs(allplayer.rect.x + allplayer.image.get_width() - x) / abs(allplayer.rect.y - y)))) -90
                    else:
                        angle = 90 - (math.degrees(math.atan(abs(allplayer.rect.x - x) / abs(allplayer.rect.y - y))))
        return angle

    def calculePuissance():
        x, y = pygame.mouse.get_pos()
        puissance = 0
        for allplayer in allplayer_group:
            if allplayer.turn_play:
                puissance = sqrt(abs(pow(x-allplayer.rect.x,2) - pow(y-allplayer.rect.y,2)))
        return puissance

    def draw_text(text, font, text_color, x, y):
        img = font.render(text, True, text_color)
        screen.blit(img, (x, y))

    def draw_bg():
        screen.fill(BG)
        screen.blit(bg_Image,(0,0))

    def draw_wind():
        pygame.draw.polygon(screen, RED, [(500, 100), (500, 50), (500 + wind, 75)])

    class Character(pygame.sprite.Sprite):
        def __init__(self, char_type, x, y, scale, speed):
            super().__init__()
            self.alive = True  # vivant ou tuer
            self.time_round = 100
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
            self.animation_list = []  # list photo action
            self.frame_index = 0
            self.action = 0  # choisir actions
            self.update_time = pygame.time.get_ticks()

            animation_types = ["Idle", "Run", "Jump", "Dead"]
            for animation in animation_types:
                temp_list = []
                num_of_frames = len(
                    os.listdir(f"img/{char_type}/{animation}"))  # compter le nombre de photos dans le fichier
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
                    self.flip = True
                    self.direction = -1
                    self.time_round -= 1
                # gauche
                if moving_right:
                    dx = self.speed
                    self.flip = False
                    self.direction = 1
                    self.time_round -= 1
                # droite
                if self.jump == True and self.in_air == False:
                    self.vel_y = -11
                    self.jump = False
                    self.in_air = True
                    self.time_round -= 1
                # saute
            self.vel_y += GRAVITY
            if self.vel_y > 10:
                self.vel_y
            dy += self.vel_y
            for tile in world.Objet_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                    elif self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = tile[1].top - self.rect.bottom
            if self.rect.left +dx <0 or self.rect.right + dx > screen_width:
                dx = 0
            if self.time_round <= 0:
                dx = 0
                dy = 0

            self.rect.x += dx
            self.rect.y += dy

        def set_gravity(self):
            dx = 0
            dy = 0
            self.vel_y += GRAVITY
            dy += self.vel_y
            for tile in world.Objet_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                    elif self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = tile[1].top - self.rect.bottom
            self.rect.x += dx
            self.rect.y += dy

        def update(self, player_round):
            self.update_animation(player_round)
            self.check_alive()

        def update_animation(self, player_round):
            if player_round:
                ANIMATION_COOLDOWN = 75
                # mise à jour d'animation
                self.image = self.animation_list[self.action][self.frame_index]
                # temps écoulé depuis le mise à jour
                if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                    self.frame_index += 1
                    self.update_time = pygame.time.get_ticks()
                # s'il dépasse la nombre d'images dans le répertoire
                if self.frame_index >= len(self.animation_list[self.action]):
                    if self.action == 3:
                        self.frame_index = len(self.animation_list[self.action]) - 1
                    else:
                        self.frame_index = 0

        def update_action(self, new_action):

            if self.action != new_action:
                self.action = new_action
                # mise à jour d'action choisie
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
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    class ItemBox(pygame.sprite.Sprite):
        def __init__(self, item_type, x, y):
            super().__init__()
            self.item_type = item_type
            self.image = item_boxes.get(self.item_type)
            self.rect = self.image.get_rect()
            self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

        def update(self):
            if pygame.sprite.collide_rect(self, player):
                if self.item_type == "Health":
                    player.health += 25
                    if player.health > player.max_health:
                        player.health = player.max_health
                if self.item_type == "Rocket":
                    player.arm = "Rocket"
                self.kill()
            if pygame.sprite.collide_rect(self, player2):
                if self.item_type == "Health":
                    player2.health += 25
                    if player2.health > player2.max_health:
                        player2.health = player2.max_health
                if self.item_type == "Rocket":
                    player2.arm = "Rocket"
                self.kill()

    class HealthBar():
        def __init__(self, x, y, health, max_health):
            self.x = x
            self.y = y
            self.health = health
            self.max_health = max_health

        def draw(self, health):
            # mise à jour de vie
            self.health = health
            # pourcentage entre le rouge et vert
            ratio = self.health / self.max_health
            pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
            pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
            pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

    class Rocket(pygame.sprite.Sprite):
        def __init__(self, x, y, direction, scale):
            super().__init__()
            self.vel_y = -11
            self.speed = calculePuissance()
            self.scale = scale
            img = pygame.transform.scale(rocket_img,
                                         (int(caisse_img.get_width() * scale), int(caisse_img.get_height() * scale)))
            self.image = img
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.direction = direction
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.time = 0
            self.x0 = self.rect.x
            self.y0 = self.rect.y
            self.angletir = calculeAngle()
            self.wind = wind

        def update(self):
            dx = 0
            dy = 0

            # initialisation des variables du tir de rocket
            self.time += 0.15
            XandY = pathWithWind(self.direction, self.x0, self.y0, self.speed, math.radians(self.angletir), self.time,
                                 k, self.wind)
            # condition grenade et le sol
            for tile in world.Objet_list:
                if tile[1].colliderect(self.rect):
                    self.kill()
                    explosion = Explosion(self.rect.x, self.rect.y, 1)
                    explosion_group.add(explosion)
                    # explose damage dans un cercle
                    for allplayer in allplayer_group:
                        if abs(self.rect.centerx - allplayer.rect.centerx) < TILE_SIZE * 0.8 and abs(
                                self.rect.centery - allplayer.rect.centery) < TILE_SIZE * 0.8:
                            allplayer.health -= 40
                        if abs(self.rect.centerx - allplayer.rect.centerx) < TILE_SIZE and abs(
                                self.rect.centery - allplayer.rect.centery) < TILE_SIZE:
                            allplayer.health -= 20
                        for lite in world.Objet_list:
                            if abs(self.rect.centerx - lite[1].x) < TILE_SIZE*1.2 and abs(
                                    self.rect.centery - lite[1].y) < TILE_SIZE*1.2:
                                world.Objet_list.remove(lite)
                                break
                    break
            dx = XandY[0]
            dy = XandY[1]
            self.rect.x -= self.rect.x
            self.rect.y -= self.rect.y

            self.rect.x += dx
            self.rect.y += dy



    class Grenade(pygame.sprite.Sprite):
        def __init__(self, x, y, direction):
            super().__init__()
            self.timer = 200
            self.vel_y = -11
            self.speed = 40
            self.image = grenade_img
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.direction = direction
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.time = 0
            self.x0 = self.rect.x
            self.y0 = self.rect.y
            self.angletir = calculeAngle()
            self.rebond = 0

        def update(self):
            dx = 0
            dy = 0
            self.time += 0.15
            XandY = path(self.direction, self.x0, self.y0, self.speed,
                         math.radians(self.angletir), self.time)
            # condition grenade et le sol
            for tile in world.Objet_list:
                if tile[1].colliderect(self.rect.x, XandY[1], self.width, self.height):
                    # calcul du vecteur vitesse à l'impact du sol
                    if self.rebond < 5:
                        if tile[1].y > XandY[1]:
                            vx = self.speed * cos(math.radians(self.angletir))
                            vy = -(9.8) * self.time + self.speed * sin(math.radians(self.angletir))
                            self.speed = sqrt(pow(vy, 2) + pow(vx, 2))
                            self.speed /= 1.8
                            self.x0 = self.rect.x
                            self.y0 = self.rect.y
                            self.time = 0
                            self.rebond += 1
                        else:
                            self.time = 0
                            self.x0 = self.rect.x
                            self.speed = 0
                    else:
                        self.speed = 0
                    return
                if tile[1].colliderect(XandY[0], self.rect.y, self.width, self.height) and self.rebond < 5:
                    self.rebond += 1
                    self.direction *= -1
                    self.x0 = self.rect.x
                    self.y0 = self.rect.y
                    self.time = 0
                    self.angletir = 60
                    self.speed/=2
                    return

            if self.rebond < 5:
                dx = XandY[0]
                dy = XandY[1]
                self.rect.x -= self.rect.x
                self.rect.y -= self.rect.y
            else:
                self.speed = 0
            # mise à jour grenade position
            self.rect.x += dx
            self.rect.y += dy

            # grenade explosion temps
            self.timer -= 1
            if self.timer <= 0:
                self.kill()
                explosion = Explosion(self.rect.x, self.rect.y, 1)
                explosion_group.add(explosion)
                # explose damage dans une cercle
                for allplayer in allplayer_group:
                    if abs(self.rect.centerx - allplayer.rect.centerx) < TILE_SIZE * 0.8 and abs(
                            self.rect.centery - allplayer.rect.centery) < TILE_SIZE * 0.8:
                        allplayer.health -= 20
                    if abs(self.rect.centerx - allplayer.rect.centerx) < TILE_SIZE and abs(
                            self.rect.centery - allplayer.rect.centery) < TILE_SIZE:
                        allplayer.health -= 10
                    for lite in world.Objet_list:
                        if abs(self.rect.centerx - lite[1].x) < TILE_SIZE and abs(
                                self.rect.centery - lite[1].y) < TILE_SIZE:
                            world.Objet_list.remove(lite)
                            break


    class World():
        def __init__(self):
            self.Objet_list = []

        def process_data(self, data):
            for y, row in enumerate(data):
                for x, tile in enumerate(row):
                    if tile>=0:
                        img = img_list[tile]
                        img_rect = img.get_rect()
                        img_rect.x = x * TILE_SIZE
                        img_rect.y = y * TILE_SIZE
                        tile_data = (img, img_rect)
                        if tile == 0 or tile == 1 or tile == 2:
                            self.Objet_list.append(tile_data)
                        if tile == 6:
                            player = Character("character", x * TILE_SIZE, y * TILE_SIZE, 0.09, 5)
                            health_bar = HealthBar(10, 40, player.health, player.health)
                            player_group.add(player)
                            allplayer_group.add(player)
                            player.turn_play = True
                        if tile == 7:
                            player2 = Character("character", x * TILE_SIZE, y * TILE_SIZE, 0.09, 5)
                            health_bar2 = HealthBar(screen_width - 160, 40, player2.health, player2.health)
                            player2_group.add(player2)
                            allplayer_group.add(player2)
                        if tile == 4:
                            item_box = ItemBox("Rocket", x * TILE_SIZE, y * TILE_SIZE)
                            item_box_group.add(item_box)
                        if tile == 5:
                            item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                            item_box_group.add(item_box)
            return player, health_bar, player2, health_bar2

        def draw(self):
            for tile in self.Objet_list:
                screen.blit(tile[0], tile[1])

    class Explosion(pygame.sprite.Sprite):
        def __init__(self, x, y, scale):
            super().__init__()
            self.images = []
            for num in range(5):
                img = pygame.image.load(f"img/explosion/{num}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                self.images.append(img)
            self.frame_index = 0
            self.image = self.images[self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.counter = 0

        def update(self):
            EXPLOSION_SPEED = 4
            self.counter += 1
            explose_music.play()
            if self.counter >= EXPLOSION_SPEED:
                self.counter = 0
                self.frame_index += 1
                if self.frame_index >= len(self.images):
                    self.kill()
                else:
                    self.image = self.images[self.frame_index]




    exit_button = startButton.Button(screen_width/2 - 120, 500, exit_img, 1)
    mini_restart_button = startButton.Button(screen_width/2+120,10, mini_restart_img, 2)
    restart_button = startButton.Button(screen_width // 2 - 100, screen_height // 2 - 50, restart_img, 2)
    map_button = startButton.Button(screen_width/2 - 250, 100, map_0, 2)
    map_button1 = startButton.Button(screen_width/2 - 250, 300, map_1, 2)
    map_button2 = startButton.Button(screen_width /2, 300, map_2, 2)
    map_button3 = startButton.Button(screen_width /2, 100, map_3, 2)
    grenade_group = pygame.sprite.Group()
    rocket_group = pygame.sprite.Group()
    explosion_group = pygame.sprite.Group()
    caisse_group = pygame.sprite.Group()
    allplayer_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    player2_group = pygame.sprite.Group()
    item_box_group = pygame.sprite.Group()

    def createMap(nbMap):
        world_data = []
        for row in range(ROWS):
            r = [-1] * COLS
            world_data.append(r)
        strMap = str(nbMap) + '.csv'
        with open(strMap, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)
        return world_data

    run = True
    #Affichage
    while run:
        clock.tick(FPS)
        if start_game == False:
            screen.fill(BG)
            if map_button.draw(screen):
                world = World()
                player, health_bar, player2, health_bar2 = world.process_data(createMap(0))
                start_game = True
            if map_button1.draw(screen):
                world = World()
                player, health_bar, player2, health_bar2 = world.process_data(createMap(1))
                start_game = True
            if map_button2.draw(screen):
                world = World()
                player, health_bar, player2, health_bar2 = world.process_data(createMap(2))
                start_game = True
            if map_button3.draw(screen):
                world = World()
                player, health_bar, player2, health_bar2 = world.process_data(createMap(3))
                start_game = True
            if exit_button.draw(screen):
                run = False
        else:
            draw_bg()
            world.draw()
            if mini_restart_button.draw(screen):
                main()
            #affichage barre de vie
            draw_text("PLAYER 1", font, WHITE, 10, 10)
            health_bar.draw(player.health)
            draw_text("PLAYER 2", font, WHITE, screen_width - 110, 10)
            health_bar2.draw(player2.health)
            draw_wind()
            if EndGAME:
                if restart_button.draw(screen):
                    main()
            #donne la gravité à ce qui ne jouent pas
            for allplayer in allplayer_group:
                if allplayer.time_round<=0:
                    allplayer.set_gravity()
                if not allplayer.turn_play:
                    allplayer.set_gravity()
                    allplayer.update(True)
                    allplayer.update_animation(True)
                if allplayer.turn_play and allplayer.alive:
                    if allplayer.time_round >0:
                        nbM = str(allplayer.time_round)
                        draw_text("Points d'action :"+nbM, font, RED, screen_width/2-100, 10)
                    else:
                        draw_text("Points d'action : 0", font, RED, screen_width/2-100,10)
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
            item_box_group.draw(screen)

            #mise à jour d'actions
            for allplayer in allplayer_group:
                if allplayer.rect.centerx<0 or allplayer.rect.centerx>screen_width or allplayer.rect.centery> screen_height or not allplayer.alive:
                    allplayer.kill()
                    EndGAME = True
                if allplayer.alive and allplayer.turn_play:
                    if grenade and grenade_thrown == False and allplayer.arm == "Grenade":
                        grenade = Grenade(allplayer.rect.centerx, allplayer.rect.top, allplayer.direction)
                        grenade_group.add(grenade)
                        grenade_thrown = True
                    if rocket and rocket_thrown == False and allplayer.arm == "Rocket":
                        rocket = Rocket(allplayer.rect.centerx, allplayer.rect.top, allplayer.direction, 0.8)
                        rocket_group.add(rocket)
                        rocket_thrown = True
                    if allplayer.in_air:
                        allplayer.update_action(2)
                    elif moving_left or moving_right:
                        allplayer.update_action(1)
                    else:
                        allplayer.update_action(0)

                        # maintient du clique gauche de la souris
                    left, middle, right = pygame.mouse.get_pressed()
                    if left:
                        for allplayer in allplayer_group:
                            # si c'est au tour du joueur on trace la courbe
                            if allplayer.turn_play:
                                if allplayer.arm == "Rocket":
                                    speed = calculePuissance()
                                    for t in range(20):
                                        XandY = path(allplayer.direction, allplayer.rect.centerx, allplayer.rect.top,
                                                     speed, math.radians(calculeAngle()), t)
                                        pygame.draw.rect(screen, BLACK, pygame.Rect(XandY[0], XandY[1], 5, 5))
                                    break
                                elif allplayer.arm == "Grenade":
                                    speed = 40
                                    for t in range(20):
                                        XandY = path(allplayer.direction, allplayer.rect.centerx, allplayer.rect.top,
                                                     speed, math.radians(calculeAngle()), t)
                                        pygame.draw.rect(screen, BLACK, pygame.Rect(XandY[0], XandY[1], 5, 5))
                                    break


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    moving_left = True
                if event.key == pygame.K_r and EndGAME:
                    main()


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
                        jump_music.play()
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
                    wind = random.randrange(-50, 50)
                    for allplayer in allplayer_group:
                        Tour += 1
                        if allplayer.alive:
                            if next:
                                allplayer.turn_play = True
                                Tour = 0
                                allplayer.time_round = 100
                                break
                            if allplayer.turn_play:
                                allplayer.turn_play = False
                                next = True

                        if Tour == len(allplayer_group):
                            for allplayer in allplayer_group:
                                if allplayer.alive:
                                    allplayer.turn_play = True
                                    Tour = 0
                                    allplayer.time_round = 100
                                    break


        pygame.display.update()

main()
