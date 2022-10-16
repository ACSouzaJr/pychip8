""" Module for the 36 instructions on Chip-8 """
import random
import logging
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychip8.chip8 import Chip8

# Create logger
logger = logging.getLogger(__name__)
# Config logger
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# Enable logger
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


def cls(chip8: "Chip8"):
    """Clear screen."""
    chip8.memory.display = [0 for _ in range(64 * 32)]


def call(chip8: "Chip8", addr: int):
    """Call subroutine at nnn."""
    chip8.memory.stack[chip8.registers.sp] = chip8.registers.pc
    chip8.registers.sp += 1
    chip8.registers.pc = addr


def ret(chip8: "Chip8"):
    """Return from a subroutine."""
    chip8.registers.sp -= 1
    chip8.registers.pc = chip8.memory.stack[chip8.registers.sp]


def jump(chip8: "Chip8", addr: int):
    """Jump to location nnn."""
    chip8.registers.pc = addr


def branch(chip8: "Chip8", addr: int):
    """Jump to location nnn + V0."""
    chip8.registers.pc = addr + chip8.registers.v[0]


def se_byte(chip8: "Chip8", x: int, byte: int):
    """Skip next instruction if Vx == kk."""
    if chip8.registers.v[x] == byte:
        chip8.registers.pc += 2


def sne_byte(chip8: "Chip8", x: int, byte: int):
    """Skip next instruction if Vx != kk."""
    if chip8.registers.v[x] != byte:
        chip8.registers.pc += 2


def se(chip8: "Chip8", x: int, y: int):
    """Skip next instruction if Vx == Vy."""
    if chip8.registers.v[x] == chip8.registers.v[y]:
        chip8.registers.pc += 2


def sne(chip8: "Chip8", x: int, y: int):
    """Skip next instruction if Vx != Vy."""
    if chip8.registers.v[x] != chip8.registers.v[y]:
        chip8.registers.pc += 2


def ld_byte(chip8: "Chip8", x: int, byte: int):
    """The interpreter puts the value kk into register Vx."""
    chip8.registers.v[x] = byte


def ldi(chip8: "Chip8", addr: int):
    """Set I = nnn."""
    chip8.registers.i = addr


def ld_sprite(chip8: "Chip8", x: int):
    """Set I = location of sprite for digit Vx.

    The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx.
    The sprites for hexadecimal digits (0-F) are 5 bytes long, or 8x5 pixels.
    """
    chip8.registers.i = 5 * chip8.registers.v[x]


def ld(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vy."""
    chip8.registers.v[x] = chip8.registers.v[y]


def ld_dt(chip8: "Chip8", x: int):
    """Set Vx = delay timer value."""
    chip8.registers.v[x] = chip8.registers.dt


def set_dt(chip8: "Chip8", x: int):
    """Set delay timer = Vx."""
    chip8.registers.dt = chip8.registers.v[x]


def set_st(chip8: "Chip8", x: int):
    """Set sound timer = Vx."""
    chip8.registers.st = chip8.registers.v[x]


def store_bcd(chip8: "Chip8", x: int):
    """Store BCD representation of Vx in memory locations I, I+1, and I+2.

    The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.
    """
    number = chip8.registers.v[x]
    hundreds = number // 100
    tens = number % 100 // 10
    ones = number % 10

    # print(f"Number 0x{number:02X}")
    # print(f"hundreds 0x{hundreds:02X}")
    # print(f"tens 0x{tens:02X}")
    # print(f"ones 0x{ones:02X}")

    chip8.memory.ram[chip8.registers.i] = hundreds
    chip8.memory.ram[chip8.registers.i + 1] = tens
    chip8.memory.ram[chip8.registers.i + 2] = ones


def store_v(chip8: "Chip8", x: int):
    """Store registers V0 through Vx in memory starting at location I.

    The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
    """

    for reg_i in range(x + 1):  # starts from zero
        chip8.memory.ram[chip8.registers.i + reg_i] = chip8.registers.v[reg_i]


def ld_v(chip8: "Chip8", x: int):
    """Read registers V0 through Vx from memory starting at location I.

    The interpreter reads values from memory starting at location I into registers V0 through Vx.
    """

    for reg_i in range(x + 1):  # starts from zero
        chip8.registers.v[reg_i] = chip8.memory.ram[chip8.registers.i + reg_i]


def add_byte(chip8: "Chip8", x: int, byte: int):
    """Set Vx = Vx + kk."""
    chip8.registers.v[x] += byte
    chip8.registers.v[x] &= 0xFF


def addi(chip8: "Chip8", x: int):
    """Set I = I + Vx."""
    chip8.registers.i += chip8.registers.v[x]
    chip8.registers.i &= 0xFFF


def or_(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vx OR Vy."""
    chip8.registers.v[x] |= chip8.registers.v[y]


def and_(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vx AND Vy."""
    chip8.registers.v[x] &= chip8.registers.v[y]


def xor_(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vx XOR Vy."""
    chip8.registers.v[x] ^= chip8.registers.v[y]


def add(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vx + Vy, set VF = carry."""
    chip8.registers.v[x] += chip8.registers.v[y]

    # set overflow flag
    if chip8.registers.v[x] & 0xFF > 0:
        chip8.registers.v[0xF] = 1
    else:
        chip8.registers.v[0xF] = 0

    chip8.registers.v[x] &= 0xFF


def sub(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vx - Vy, set VF = NOT borrow."""

    # set overflow flag
    if chip8.registers.v[x] > chip8.registers.v[y]:
        chip8.registers.v[0xF] = 1
    else:
        chip8.registers.v[0xF] = 0

    chip8.registers.v[x] -= chip8.registers.v[y]
    chip8.registers.v[x] &= 0xFF


def subn(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vy - Vx, set VF = NOT borrow."""

    # set overflow flag
    if chip8.registers.v[y] > chip8.registers.v[x]:
        chip8.registers.v[0xF] = 1
    else:
        chip8.registers.v[0xF] = 0

    chip8.registers.v[x] = chip8.registers.v[y] - chip8.registers.v[x]
    chip8.registers.v[x] &= 0xFF


def shr(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vx SHR 1."""

    # set overflow flag
    chip8.registers.v[0xF] = chip8.registers.v[x] & 0x1

    chip8.registers.v[x] >>= 1
    chip8.registers.v[x] &= 0xFF


def shl(chip8: "Chip8", x: int, y: int):
    """Set Vx = Vx SHL 1."""

    # set overflow flag
    chip8.registers.v[0xF] = (chip8.registers.v[x] & 0x80) >> 7

    chip8.registers.v[x] <<= 1
    chip8.registers.v[x] &= 0xFF


def rnd(chip8: "Chip8", x: int, byte: int):
    """Set Vx = random byte AND kk."""
    random_number = random.randint(0, 255)
    chip8.registers.v[x] = random_number and byte


def ld_kp(chip8: "Chip8", x: int):
    """Wait for a key press, store the value of the key in Vx.

    All execution stops until a key is pressed, then the value of that key is stored in Vx.
    """
    pygame.event.clear()
    # print("Key press!")
    event = pygame.event.wait()
    if event.type == pygame.KEYDOWN:
        # print(event.key)
        chip8.keyboard.set_key(event.key)
        chip8.registers.v[x] = chip8.keyboard.is_pressed(event.key)


def skp(chip8: "Chip8", x: int):
    """Skip next instruction if key with the value of Vx is pressed."""

    if chip8.keyboard.is_pressed(chip8.registers.v[x]):
        chip8.registers.pc += 2


def sknp(chip8: "Chip8", x: int):
    """Skip next instruction if key with the value of Vx is not pressed."""

    if not chip8.keyboard.is_pressed(chip8.registers.v[x]):
        chip8.registers.pc += 2


def draw(chip8: "Chip8", x: int, y: int, n: int):
    """Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

    The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, it wraps around to the opposite side of the screen.
    """

    # reset flag

    # position
    ## wrap around coords
    x_mem = chip8.registers.v[x]
    y_mem = chip8.registers.v[y]

    # For each column on sprite
    sprite = range(n)
    for row in sprite:
        pixels = chip8.memory.ram[chip8.registers.i + row]

        # one sprite row = 1 byte = 8 bits
        byte = range(8)
        for col in byte:

            bit = (pixels & (0x80)) >> 7  # get first pixel

            logger.debug(f"BIT {bit}")

            x_pos = (x_mem + col) % chip8.display.width
            y_pos = (y_mem + row) % chip8.display.height

            logger.debug("DRAW y: %d, %d, %d" % (y, y_mem, y_pos))
            logger.debug("DRAW x: %d, %d, %d" % (x, x_mem, x_pos))

            index_pos = y_pos * chip8.display.width + x_pos

            old_bit = chip8.memory.display[index_pos]
            chip8.memory.display[index_pos] ^= bit

            # check if pixel as erased
            chip8.registers.v[0xF] = int(
                old_bit and not chip8.memory.display[index_pos]
            )

            # go to nex bit
            pixels <<= 1
