# Copyright 2019 John Reese
# Licensed under the MIT license

"""
Catch the running light when it passes button B.
Button A starts a new game, each consisting of ten rounds of increasing difficulty. 
"""

import random

import board
import neopixel
from colors import GREEN, OFF, RAINBOW, RED, WHITE
from cpgame import after, at, every, on, start, tick

try:
    from typing import List
except ImportError:
    pass


ROUNDS = 10
SPEEDS = [0.11, 0.1, 0.1, 0.09, 0.08, 0.08, 0.07, 0.06, 0.05, 0.04]
COLORS = [WHITE] + list(reversed(RAINBOW))
REWARD = [RED, GREEN]
FLASH = [WHITE, OFF]

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.05, auto_write=False)
pixels.fill(OFF)
pixels.show()


class state:
    ready = False
    round = 0
    pos = 0
    results = []  # type: List[int]

    @classmethod
    def reset(cls):
        cls.ready = False
        cls.round = 0
        cls.pos = random.randint(0, 9)
        cls.results = [0 for i in range(ROUNDS)]


def render():
    color = COLORS[state.round]
    pixels.fill(OFF)
    pixels[state.pos] = color
    pixels.show()


@on(board.BUTTON_A)
def ready(now):
    state.ready = True


@on(board.BUTTON_B)
def play(now):
    if not state.ready:
        return

    good = 1 if state.pos == 7 else 0
    pixels.fill(REWARD[good])
    pixels[state.pos] = REWARD[not good]
    pixels.show()

    state.results[state.round] = good
    state.round += 1
    state.pos = random.randint(0, 9)

    after(0.5, main)


def finish(now):
    pixels.fill(OFF)
    for idx, value in enumerate(state.results):
        if value:
            pixels[idx] = REWARD[value]
    pixels.show()

    state.reset()
    after(3, main)


def main(now):
    if not state.ready:
        pixels.fill(OFF)
        pixels[2] = FLASH[int(now) % 2]
        pixels.show()
        return after(0.1, main)

    if state.round >= ROUNDS:
        return after(0, finish)

    after(SPEEDS[state.round], main)
    state.pos += 1
    if state.pos >= 10:
        state.pos = 0

    render()


state.reset()
at(0, main)
start()
