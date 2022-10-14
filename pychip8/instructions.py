""" Module for the 36 instructions on Chip-8 """
from pychip8.chip8 import Chip8
from pychip8 import window


def cls(chip8: Chip8):
    """ Clear screen """
    window.clear_screen(chip8.display.screen)