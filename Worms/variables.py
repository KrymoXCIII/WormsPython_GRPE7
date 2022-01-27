import pygame
from pygame.locals import *
pygame.init()

continuer = 1

window = pygame.display.set_mode((1920, 1080), RESIZABLE)

background = pygame.image.load("background.jpg").convert()

character1 = pygame.image.load("character.png").convert_alpha()

characterPos = character1.get_rect()

