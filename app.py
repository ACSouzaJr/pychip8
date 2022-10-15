""" Main file for executing emulator """
import pychip8
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rom",
        type=str,
        default="roms/PONG.ch8",
        help="Chip-8 ROM filepath.",
    )
    args = parser.parse_args()
    pychip8.run(args.rom)


if __name__ == "__main__":
    main()
