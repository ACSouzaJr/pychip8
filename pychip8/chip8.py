""" Main module with Chip8 interface

## About

"What's a Chip-8?"
Chip-8 is a simple, interpreted, programming language which was first used on some do-it-yourself computer systems in the late 1970s and early 1980s.
A Chip-8 interpeter was used in calculators as a simple way to make games.

## Memory

Memory = 4KB RAM = 2^12 (0x000-0xFFF)
12 bits memory address
+---------------+= 0x000 (0) Start of Chip-8 RAM
| 0x000 to 0x1FF|
| Reserved for  |
|  interpreter  |
+---------------+= 0x200 (512) Start of most Chip-8 programs
|               |
|     Chip-8    |
| Program / Data|
|     Space     |
|               |
+---------------+= 0xFFF (4095) End of Chip-8 RAM

## Registers

16 registers 8-bit (V0-VF) - general puspose
    VF = Flags register

03 registers 16-bit 
    (I) - store address (lower 12 bits)
    (PC) - store current address on memory
    (SP) - pointer to stack top

Stack: 16 16-bit register to store addresses for subrotine jump.

## Display

Monitor = 64x32 pixels (mochrome) = 2KB = 2^11 (2048)

Draws to screen with sprites. A sprite is a group of bytes which are a binary representation of the desired picture. 8x15 size - 1 byte per line.

The sprites for hexadecimal digits (0-F) should be store at the interpreter address (0x000-0x01FF). They are 5 bytes long, or 8x5 pixels.

## Timers & Sound

Delay timer: active when register DT (delay timer register) is non-zero. The timer subtract 1 from the register at a rate of 60 Hz.

Sound Timer: active when register ST (sound timer register) is non-zero. The timer subtract 1 from the register at a rate of 60 Hz. As long as ST's value is greater than zero Chip-8 buzzer sound.

## Instructions

36 instructions: math, graphics, and flow control.

all instructions is 2 bytes long, msb first.
"""
from dataclasses import dataclass, field
from pygame.surface import Surface

from pychip8.window import create_window


@dataclass
class Registers:
    i: int = 0
    pc: int = 0
    sp: int = 0
    vx: list[int] = field(default_factory=lambda: [0 for _ in range(0xF)])


@dataclass
class Memory:
    ram: list[int] = field(default_factory=lambda: [0 for _ in range(0xFFF)])
    sp: list[int] = field(
        default_factory=lambda: [0 for _ in range(0x10)])    # 16
    display: list[int] = field(
        default_factory=lambda: [0 for _ in range(64 * 32)])

    def __post_init__(self):
        ...


@dataclass
class Display:
    width: int = 64
    height: int = 32
    scale: int = 20
    screen: Surface = field(init=False)

    def __post_init__(self):
        self.screen = create_window(self.width, self.height, self.scale)


@dataclass
class Chip8:
    registers: Registers = Registers()
    memory: Memory = Memory()
    display: Display = Display()
