cpgame
======

Simple "game" framework for [CircuitPython][] embedded hardware.

[![build status](https://travis-ci.org/jreese/cpgame.svg?branch=master)](https://travis-ci.org/jreese/cpgame)
[![version](https://img.shields.io/pypi/v/cpgame.svg)](https://pypi.org/project/cpgame)
[![license](https://img.shields.io/pypi/l/cpgame.svg)](https://github.com/jreese/cpgame/blob/master/LICENSE)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


Install
-------

Download the [compiled library][cpgame.mpy] and copy it to your device's directory:

```bash
$ cp -X cpgame.mpy /Volumes/CIRCUITPY/
```

[cpgame.mpy]: https://github.com/jreese/cpgame/releases/download/v0.5/cpgame.mpy


Overview
--------

cpgame provides a number of decorators and a simple event loop to provide a responsive
framework for building applications and games on embedded hardware using CircuitPython.

Run a function on every "tick" of the event loop:

```python
from cpgame import start, tick

@tick
def loop(now):
    ...

start()
```

Blink a Neopixel every second:

```python
@every(1)
def periodic(now):
    pixel[0] = RED if int(now) % 2 else OFF
```

Turn a Neopixel on and off with a button press:

```python
@on(board.BUTTON_A, DOWN)
def pressed(now):
    pixel[0] = RED

@on(board.BUTTON_A, UP)
def released(now):
    pixel[0] = OFF
```

Create or reset timers:

```python
@on(board.BUTTON_A)
def flood(now):
    pixels.fill(random.choice(COLORS))
    delay = random.randint(20, 100) / 10  # between 2 and 10 seconds
    after(delay, flood)

@on(board.BUTTON_B)
def halt(now):
    cancel(flood)
```

Play sound:

```python
enable_speaker()
middle_a = sample(440)

@on(board.BUTTON_A)
def noise(now):
    play_sound(middle_a, 1)
```


Roadmap
-------

* Support more boards than Circuit Playground Express.
* Add helper functions for animating NeoPixels, raw audio clips, and LCD displays.


License
-------

cpgame is copyright [John Reese](https://jreese.sh), and licensed under the
MIT license.  I am providing code in this repository to you under an open source
license.  This is my personal repository; the license you receive to my code
is from me and not from my employer. See the `LICENSE` file for details.

[CircuitPython]: https://circuitpython.org
