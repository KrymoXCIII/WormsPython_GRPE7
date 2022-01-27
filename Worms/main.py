import pygame
from pygame.locals import *
from variables import *
from classes import *

pygame.init()

window.blit(background, (0, 0))
window.blit(character1, (100, 100))

pygame.display.flip()

while continuer:

    pygame.key.set_repeat(400, 30)

    for event in pygame.event.get():

        if event.type == QUIT:
            continuer = 0

        if event.type == KEYDOWN:
            if event.key == K_RIGHT:

                characterPos = characterPos.move(3, 0)

            if event.key == K_LEFT:
                characterPos = characterPos.move(-3, 0)

    window.blit(background, (0, 0))
    window.blit(character1, characterPos)
    pygame.display.flip()
