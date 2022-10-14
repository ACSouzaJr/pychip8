import pygame
from pygame.surface import Surface


def create_window(
        width: int,
        height: int,
        scale=2,
        background_color=(255, 255, 0)    # RGB
) -> Surface:
    """ Create window with pygame """

    # create screen
    pygame.display.set_caption("Chip-8")
    screen = pygame.display.set_mode((width * scale, height * scale))

    # set background color
    screen.fill(background_color)

    # write to creen
    pygame.display.flip()

    return screen


def clear_screen(screen: Surface) -> Surface:
    """ Clear screen with black """
    # set background color
    background_color = (0, 0, 0)
    screen.fill(background_color)

    # write to creen
    pygame.display.flip()

    return screen