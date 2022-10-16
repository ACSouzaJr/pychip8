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

all instructions is '2 bytes long', msb first.
"""
import pygame
import logging
from pygame.surface import Surface
from dataclasses import dataclass, field
from pychip8 import instructions as inst

from pychip8.window import create_window

# Create logger
logger = logging.getLogger(__name__)
# Config logger
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# Enable logger
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


@dataclass
class Registers:
    i: int = 0  # instruction register
    pc: int = 0x200  # program counter
    sp: int = 0  # stack pointer
    dt: int = 0  # delay timer
    st: int = 0  # sound timer
    v: list[int] = field(default_factory=lambda: [0 for _ in range(0x10)])  # 16


@dataclass
class Keyboard:
    pressed_keys: list[bool] = field(
        default_factory=lambda: [False for _ in range(0x10)]
    )  # 16
    key_mapper = {
        49: 0x1,  # 1
        50: 0x2,  # 2
        51: 0x3,  # 3
        52: 0xC,  # 4
        113: 0x4,  # Q
        119: 0x5,  # W
        101: 0x6,  # E
        114: 0xD,  # R
        97: 0x7,  # A
        115: 0x8,  # S
        100: 0x9,  # D
        102: 0xE,  # F
        122: 0xA,  # Z
        120: 0x0,  # X
        99: 0xB,  # C
        118: 0xF,  # V
    }

    def set_key(self, key: int, value=True):
        """Set equivalent keyboard keys to Chip-8."""
        try:
            key = self.key_mapper[key]
            self.pressed_keys[key] = value
        except KeyError:
            print("Invalid key pressed!")

    def is_pressed(self, key: int) -> bool:
        return self.pressed_keys[key]


@dataclass
class Memory:
    ram: list[int] = field(default_factory=lambda: [0 for _ in range(0x1000)])  # 4096
    stack: list[int] = field(default_factory=lambda: [0 for _ in range(0x10)])  # 16
    display: list[int] = field(default_factory=lambda: [0 for _ in range(64 * 32)])

    def __post_init__(self):
        # yapf: disable
        hexadecimal_sprites = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,   # 0
            0x20, 0x60, 0x20, 0x20, 0x70,   # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,   # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,   # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,   # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,   # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,   # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,   # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,   # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,   # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,   # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,   # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,   # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,   # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,   # E
            0xF0, 0x80, 0xF0, 0x80, 0x80    # F
        ]
        # yapf: enable

        for i, sprite in enumerate(hexadecimal_sprites):
            self.ram[i] = sprite

    def load_rom(self, rom_filepath: str):
        with open(rom_filepath, "rb") as f:
            for i, byte in enumerate(f.read()):
                self.ram[0x200 + i] = byte


@dataclass
class Display:
    width: int = 64
    height: int = 32
    scale: int = 20
    screen: Surface = field(init=False)

    def __post_init__(self):
        self.screen = create_window(self.width, self.height, self.scale)


@dataclass
class Sound:
    beep = pygame.mixer.Sound("assets/beep.wav")


@dataclass
class Chip8:
    registers: Registers = Registers()
    memory: Memory = Memory()
    display: Display = Display()
    keyboard: Keyboard = Keyboard()
    sound: Sound = Sound()


def get_opcode(chip8: Chip8):
    """Get next opcode on ram."""

    msb = chip8.memory.ram[chip8.registers.pc]
    lsb = chip8.memory.ram[chip8.registers.pc + 1]

    chip8.registers.pc += 2

    return msb, lsb


def tick(chip8: Chip8):
    """Execute a single instruction

    Execute one cycle of the Fetch-Decode-Execute loop.
    """
    ## Fetch
    msb, lsb = get_opcode(chip8)  # 16 bits

    opcode = (msb << 8) | lsb

    op = opcode & 0xF000  # 4 highest byte
    addr = opcode & 0xFFF  # 12 lowest bits
    n = opcode & 0xF  # 4 lowest bits
    x = msb & 0xF  # 4 lowest bits of the msb
    y = (lsb & 0xF0) >> 4  # 4 upper bits of the lsb
    byte = lsb  # 8 bit lowest value

    logger.debug(f"OPCODE 0x{opcode:02X}")
    logger.debug(
        f"OP 0x{op:02X}, ADDR 0x{addr:02X}, X 0x{x:02X}, Y 0x{y:02X}, BYTE 0x{byte:02X}, N 0x{n:02X}"
    )

    ## Decode
    match op:
        case 0x0:
            match byte:
                case 0xE0:
                    inst.cls(chip8)  # Execute
                case 0xEE:
                    inst.ret(chip8)
        case 0x1000:
            inst.jump(chip8, addr=addr)
        case 0x2000:
            inst.call(chip8, addr=addr)
        case 0x3000:
            inst.se_byte(chip8, x=x, byte=byte)
        case 0x4000:
            inst.sne_byte(chip8, x=x, byte=byte)
        case 0x5000:
            inst.se(chip8, x=x, y=y)
        case 0x6000:
            inst.ld_byte(chip8, x=x, byte=byte)
        case 0x7000:
            inst.add_byte(chip8, x=x, byte=byte)
        case 0x8000:
            match n:
                case 0x0:
                    inst.ld(chip8, x=x, y=y)
                case 0x1:
                    inst.or_(chip8, x=x, y=y)
                case 0x2:
                    inst.and_(chip8, x=x, y=y)
                case 0x3:
                    inst.xor_(chip8, x=x, y=y)
                case 0x4:
                    inst.add(chip8, x=x, y=y)
                case 0x5:
                    inst.sub(chip8, x=x, y=y)
                case 0x6:
                    inst.shr(chip8, x=x, y=y)
                case 0x7:
                    inst.subn(chip8, x=x, y=y)
                case 0xE:
                    inst.shl(chip8, x=x, y=y)
        case 0x9000:
            inst.sne(chip8, x=x, y=y)
        case 0xA000:
            inst.ldi(chip8, addr=addr)
        case 0xB000:
            inst.branch(chip8, addr=addr)
        case 0xC000:
            inst.rnd(chip8, x=x, byte=byte)
        case 0xD000:
            inst.draw(chip8, x=x, y=y, n=n)
        case 0xE000:
            match byte:
                case 0x9E:
                    inst.skp(chip8, x=x)
                case 0xA1:
                    inst.sknp(chip8, x=x)
        case 0xF000:
            match byte:
                case 0x07:
                    inst.ld_dt(chip8, x=x)
                case 0x0A:
                    inst.ld_kp(chip8, x=x)
                case 0x15:
                    inst.set_dt(chip8, x=x)
                case 0x18:
                    inst.set_st(chip8, x=x)
                case 0x1E:
                    inst.addi(chip8, x=x)
                case 0x29:
                    inst.ld_sprite(chip8, x=x)
                case 0x33:
                    inst.store_bcd(chip8, x=x)
                case 0x55:
                    inst.store_v(chip8, x=x)
                case 0x65:
                    inst.ld_v(chip8, x=x)


def draw(chip8: Chip8):
    """Draw to display based on memory."""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    color_pallete = {0: BLACK, 1: WHITE}

    scale = chip8.display.scale

    for y in range(chip8.display.height):
        for x in range(chip8.display.width):

            # logger.debug("DRAW y: %d" % (y))
            # logger.debug("DRAW x: %d" % (x))

            index_pos = y * chip8.display.width + x
            pixel = chip8.memory.display[index_pos]
            pygame.draw.rect(
                chip8.display.screen,
                color_pallete[pixel],
                [x * scale, y * scale, scale, scale],
                0,
            )
    pygame.display.flip()


def update_timers(chip8: Chip8):
    """Update built in timers"""
    if chip8.registers.dt > 0:
        chip8.registers.dt -= 1

    if chip8.registers.st > 0:
        chip8.sound.beep.play()
        chip8.registers.st -= 1
    elif chip8.registers.st == 0:
        chip8.sound.beep.stop()
