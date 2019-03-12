cpgame
======

Simple "game" framework for [CircuitPython][] embedded hardware.


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

aiosqlite is copyright [John Reese](https://jreese.sh), and licensed under the
MIT license.  I am providing code in this repository to you under an open source
license.  This is my personal repository; the license you receive to my code
is from me and not from my employer. See the `LICENSE` file for details.

[CircuitPython]: https://circuitpython.org