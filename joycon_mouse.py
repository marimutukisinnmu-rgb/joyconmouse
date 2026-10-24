"""Joy-Con Mouse: stick-only pointer movement; no gyro/accelerometer use."""
from __future__ import annotations
import time
import pygame
import pyautogui

DEADZONE = 0.16
MAX_SPEED = 1500.0  # pixels/second at full stick deflection
POLL_HZ = 120
DEBUG_INPUT = True

# Typical SDL raw button indices; verify these on your Windows setup.
# Right Joy-Con: A=0, B=1, X=2, Y=3, SR=4, SL=5, R=6, ZR=7
# Left Joy-Con: Down=0, Up=1, Right=2, Left=3, SR=4, SL=5, L=6, ZL=7
BUTTONS = {'A': 0, 'B': 1, 'X': 2, 'Y': 3, 'R': 6, 'ZR': 7, 'L': 6, 'ZL': 7}
STICK_AXES = (0, 1)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

def classify(name: str) -> str | None:
    n = name.lower().replace('_', ' ').replace('-', ' ')
    if 'joy con' not in n and 'joycon' not in n:
        return None
    if '(l)' in n or 'left' in n:
        return 'L'
    if '(r)' in n or 'right' in n:
        return 'R'
    return None

def safe_button(joy, index: int) -> bool:
    return index < joy.get_numbuttons() and bool(joy.get_button(index))

def pressed(joy, label: str) -> bool:
    if label in ('LEFT', 'RIGHT'):
        if joy.get_numhats() > 0:
            x = joy.get_hat(0)[0]
            return x < 0 if label == 'LEFT' else x > 0
        # Some SDL drivers expose the D-pad as buttons instead of a hat.
        fallback = 3 if label == 'LEFT' else 2
        return safe_button(joy, fallback)
    return safe_button(joy, BUTTONS[label])

def axis(joy, index: int) -> float:
    if index >= joy.get_numaxes():
        return 0.0
    value = float(joy.get_axis(index))
    if abs(value) <= DEADZONE:
        return 0.0
    return (1 if value > 0 else -1) * (abs(value) - DEADZONE) / (1.0 - DEADZONE)

def click_edges(current: set[str], previous: set[str]) -> None:
    for key in current - previous:
        pyautogui.click(button=key)

def main() -> None:
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    previous_clicks: set[str] = set()
    last_debug = 0.0
    print('Joy-Con Mouse: Ctrl+C to quit. Gyro is not used.')
    try:
        while True:
            pygame.event.pump()
            devices = []
            for i in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(i)
                if not joy.get_init():
                    joy.init()
                side = classify(joy.get_name())
                if side:
                    devices.append((side, joy))
            lefts = [j for side, j in devices if side == 'L']
            rights = [j for side, j in devices if side == 'R']
            mode = 'LR' if lefts and rights else 'L' if lefts else 'R' if rights else 'NONE'
            dt = min(clock.get_time() / 1000.0, 0.05)
            # Use L stick when available; otherwise use R stick.
            pointer = lefts[0] if lefts else rights[0] if rights else None
            if pointer:
                x = axis(pointer, STICK_AXES[0])
                y = axis(pointer, STICK_AXES[1])
                dx, dy = round(x * MAX_SPEED * dt), round(y * MAX_SPEED * dt)
                if dx or dy:
                    pyautogui.moveRel(dx, dy, duration=0)
            clicks: set[str] = set()
            if mode == 'R':
                r = rights[0]
                if pressed(r, 'A') or pressed(r, 'ZR'): clicks.add('left')
                if pressed(r, 'Y') or pressed(r, 'R'): clicks.add('right')
            elif mode == 'L':
                l = lefts[0]
                if pressed(l, 'LEFT') or pressed(l, 'ZL'): clicks.add('left')
                if pressed(l, 'RIGHT') or pressed(l, 'L'): clicks.add('right')
            elif mode == 'LR':
                l, r = lefts[0], rights[0]
                if pressed(l, 'L') or pressed(l, 'ZL') or pressed(r, 'A') or pressed(l, 'LEFT'): clicks.add('left')
                if pressed(r, 'R') or pressed(r, 'ZR') or pressed(r, 'Y') or pressed(l, 'RIGHT'): clicks.add('right')
            click_edges(clicks, previous_clicks)
            previous_clicks = clicks
            now = time.monotonic()
            if DEBUG_INPUT and now - last_debug >= 2:
                names = [f'{side}: {joy.get_name()}' for side, joy in devices]
                print(f'Mode={mode} | devices={names or "none"}')
                last_debug = now
            clock.tick(POLL_HZ)
    except KeyboardInterrupt:
        print('\nExiting.')
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()