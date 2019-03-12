# Copyright 2019 John Reese
# Licensed under the MIT license

"""
Simple "game" framework for CircuitPython embedded hardware.
Uses timers and decorators to provide a responsive, event-driven application.

Decorators:

  @tick - Run a function at every tick of the framework's event loop.
  @every(t) - Run a function every x seconds.

  @on(*b: pin, action=DOWN) - Run a function when one or more buttons are pressed.

Framework functions:

  at(t, fn) - Run a function at monotonic time t.
  after(t, fn) - Run a function after monotic time t from now.
  cancel(fn) - Cancel any timer or hook for function fn.

  enable_speaker(on=True) - Enable or disable the onboard speaker.
  sample(frequency) - Generate a sine wave sample for the given frequency.
  play_sound(sample, duration) - Play a given sample for the given duration.
  stop_sound() - Stop all currently-playing sounds.

  start([fn]) - Start the main event loop, optionally running a function immediately.
  stop() - Stop the main event loop.

"""

__author__ = "John Reese"
__version__ = "0.5"

import array
import math
import time

import board
import gamepad
from audioio import AudioOut, RawSample
from digitalio import DigitalInOut, Direction, Pull
from touchio import TouchIn

try:
    from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
except ImportError:
    pass


# External constants

DOWN = 1
UP = 2
PROPOGATE = object()

# Internal constants

DIGITALIO = [board.BUTTON_A, board.BUTTON_B]
TOUCHIO = [board.A1, board.A2, board.A3, board.A4, board.A5, board.A6, board.A7]
SAMPLERATE = 8000  # recommended

AUDIO = AudioOut(board.A0)
SPEAKER = DigitalInOut(board.SPEAKER_ENABLE)
SPEAKER.direction = Direction.OUTPUT

# Internal state

RUNNING = True
INTERVALS = {}  # type: Dict[Callable, Tuple[float, float]]
TIMERS = {}  # type: Dict[Callable, float]
BUTTONS = []  # type: List[Any]
DIOS = []  # type: List[DigitalInOut]
PRESSES = []  # type: List[Tuple[Callable, Sequence[Any], int]]


def tick(fn):
    # type: (Callable) -> Callable
    INTERVALS[fn] = (0, 0)
    return fn


def every(interval, fn=None):
    # type: (float, Optional[Callable]) -> Callable

    def wrapper(fn):
        INTERVALS[fn] = (interval, 0)
        return fn

    if fn:
        return wrapper(fn)

    return wrapper


def at(target, fn):
    # type: (float, Callable) -> None
    TIMERS[fn] = target


def after(target, fn):
    # type: (float, Callable) -> None
    TIMERS[fn] = time.monotonic() + target


def cancel(*fns):
    # type: (Callable) -> None
    for fn in fns:
        INTERVALS.pop(fn, None)
        TIMERS.pop(fn, None)

        for idx, press in enumerate(PRESSES):
            if press[0] == fn:
                PRESSES.pop(idx)
                break


def on(*buttons, fn=None, action=DOWN):
    # type: (Any, Callable, int) -> Callable
    global GAMEPAD

    for button in buttons:
        if button not in BUTTONS:
            if button in DIGITALIO:
                dio = DigitalInOut(button)
                dio.direction = Direction.INPUT
                dio.pull = Pull.DOWN
            elif button in TOUCHIO:
                dio = TouchIn(button)
            else:
                print("unknown button {}".format(button))
            BUTTONS.append(button)
            DIOS.append(dio)

    value = tuple(buttons)

    def wrapper(fn):
        PRESSES.append((fn, buttons, action))
        return fn

    if fn:
        return wrapper(fn)

    return wrapper


def enable_speaker(on=True):
    # type: (bool) -> None
    print("speaker {}".format("on" if on else "off"))
    SPEAKER.value = on


def sample(frequency):
    # type: (int) -> RawSample
    length = SAMPLERATE // frequency
    sine_wave = array.array("H", [0] * length)
    for i in range(length):
        sine_wave[i] = int(math.sin(math.pi * 2 * i / 18) * (2 ** 15) + 2 ** 15)
    return RawSample(sine_wave)


def play_sound(sample, duration):
    # type: (RawSample, float) -> None
    AUDIO.play(sample, loop=True)
    after(duration, stop_sound)


def stop_sound(*args):
    # type: (Any) -> None
    AUDIO.stop()


def stop():
    # type: () -> None
    global RUNNING
    RUNNING = False


def start(fn=None):
    # type: (Optional[Callable]) -> None
    if PRESSES:
        every(0.02)(Gamepad())

    if fn:
        at(0, fn)

    while True:
        if not TIMERS and not INTERVALS:
            print("No functions registered, quitting")
            return

        now = time.monotonic()
        for fn, (interval, last_called) in INTERVALS.items():
            target = last_called + interval
            if target <= now:
                fn(now)
                INTERVALS[fn] = (interval, now)
                target += interval

        for fn, target in TIMERS.items():
            if target <= now:
                del TIMERS[fn]
                fn(now)

        next_target = min(
            [last_called + interval for last_called, interval in INTERVALS.values()]
            + [target for target in TIMERS.values()]
        )

        while True:
            slp = next_target - time.monotonic()
            if slp > 0:
                # print("Sleeping for {} seconds".format(slp))
                time.sleep(slp)
            else:
                break


class Gamepad:
    def __init__(self):
        self.down = ()
        self.pressed = []

    def __call__(self, now):
        down = tuple(button for button, dio in zip(BUTTONS, DIOS) if dio.value)
        if down != self.down:
            self.down = down
            return

        fresh_down = [b for b in down if b not in self.pressed]
        fresh_up = [b for b in self.pressed if b not in down]

        if fresh_down:
            # print("fresh down: {}".format(fresh_down))
            self.pressed.extend(fresh_down)

        if fresh_up:
            # print("fresh up: {}".format(fresh_up))
            for btn in fresh_up:
                self.pressed.remove(btn)

        if not (fresh_down or fresh_up):
            return

        for (fn, buttons, action) in PRESSES:
            if action == DOWN and all(b in fresh_down for b in buttons):
                v = fn(now)
            elif action == UP and all(b in fresh_up for b in buttons):
                v = fn(now)
            else:
                v = PROPOGATE

            if v is not PROPOGATE:
                break
