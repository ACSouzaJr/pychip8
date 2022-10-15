import pygame
from pychip8 import chip8


def run(rom_filepath: str):
    """Run Chip-8 emulator."""

    assert rom_filepath is not None and rom_filepath.strip() != ""

    chip8_emulator = chip8.Chip8()
    chip8_emulator.memory.load_rom(rom_filepath)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                chip8_emulator.keyboard.set_key(event.key, True)
            if event.type == pygame.KEYUP:
                chip8_emulator.keyboard.set_key(event.key, False)

        for _ in range(5):
            chip8.tick(chip8_emulator)

        chip8.update_timers(chip8_emulator)
        chip8.draw(chip8_emulator)
        clock.tick(60)
