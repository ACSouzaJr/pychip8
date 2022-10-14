import pygame
from pychip8.chip8 import Chip8
from pychip8 import instructions as inst


def run():

    chip8 = Chip8()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                inst.cls(chip8)