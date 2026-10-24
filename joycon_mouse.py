"""Joy-Con Mouse: stick-only pointer movement; no gyro/accelerometer use."""
from __future__ import annotations
import time
import pygame
import pyautogui

DEADZONE = 0.16
MAX_SPEED = 1500.0
POLL_HZ = 120
DEBUG_INPUT = True
# SDL button indices vary by driver/device. Confirm with the input diagnostics below.
BUTTONS = {'A': 0, 'B': 1, 'X': 2, 'Y': 3, 'R': 6, 'ZR': 7, 'L': 6, 'ZL': 7}
STICK_AXES = (0, 1)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

def classify(name: str) -> str | None:
    n = name.lower().replace('_', ' ').replace('-', ' ')
    if not any(token in n for token in ('joy con', 'joycon', 'nintendo switch')):
        return None
    if '(l/r)' in n or '(l + r)' in n or 'combined' in n:
        return 'LR'
    if '(l)' in n or 'left' in n:
        return 'L'
    if '(r)' in n or 'right' in n:
        return 'R'
    return None

def safe_button(joy, index: int) -> bool:
    return 0 <= index < joy.get_numbuttons() and bool(joy.get_button(index))

def pressed(joy, label: str) -> bool:
    if label in ('LEFT', 'RIGHT'):
        if joy.get_numhats() > 0:
            x = joy.get_hat(0)[0]
            return x < 0 if label == 'LEFT' else x > 0
        return safe_button(joy, 3 if label == 'LEFT' else 2)
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

def raw_state(joy) -> tuple:
    axes = tuple(round(float(joy.get_axis(i)), 2) for i in range(joy.get_numaxes()))
    buttons = tuple(i for i in range(joy.get_numbuttons()) if joy.get_button(i))
    hats = tuple(joy.get_hat(i) for i in range(joy.get_numhats()))
    return axes, buttons, hats

def main() -> None:
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    previous_clicks: set[str] = set()
    last_debug = 0.0
    last_raw: dict[int, tuple] = {}
    print('Joy-Con Mouse: Ctrl+C to quit. Gyro is not used.')
    print('Move the stick and press buttons; raw input changes will be printed for mapping.')
    print('If the pointer moves unexpectedly, move the mouse to the top-left corner to trigger the PyAutoGUI failsafe.')
    try:
        while True:
            pygame.event.pump()
            all_devices = []
            for i in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(i)
                if not joy.get_init():
                    joy.init()
                all_devices.append((i, joy, classify(joy.get_name())))
            lefts = [j for _, j, side in all_devices if side == 'L']
            rights = [j for _, j, side in all_devices if side == 'R']
            combined = [j for _, j, side in all_devices if side == 'LR']
            mode = 'LR' if (lefts and rights) or combined else 'L' if lefts else 'R' if rights else 'NONE'
            dt = min(clock.get_time() / 1000.0, 0.05)
            pointer = lefts[0] if lefts else combined[0] if combined else rights[0] if rights else None
            if pointer:
                dx = round(axis(pointer, STICK_AXES[0]) * MAX_SPEED * dt)
                dy = round(axis(pointer, STICK_AXES[1]) * MAX_SPEED * dt)
                if dx or dy:
                    pyautogui.moveRel(dx, dy, duration=0)
            clicks: set[str] = set()
            if mode == 'R' and rights:
                r = rights[0]
                if pressed(r, 'A') or pressed(r, 'ZR'): clicks.add('left')
                if pressed(r, 'Y') or pressed(r, 'R'): clicks.add('right')
            elif mode == 'L' and lefts:
                l = lefts[0]
                if pressed(l, 'LEFT') or pressed(l, 'ZL'): clicks.add('left')
                if pressed(l, 'RIGHT') or pressed(l, 'L'): clicks.add('right')
            elif mode == 'LR' and lefts and rights:
                l, r = lefts[0], rights[0]
                if pressed(l, 'L') or pressed(l, 'ZL') or pressed(r, 'A') or pressed(l, 'LEFT'): clicks.add('left')
                if pressed(r, 'R') or pressed(r, 'ZR') or pressed(r, 'Y') or pressed(l, 'RIGHT'): clicks.add('right')
            # For a combined SDL device, avoid guessing its button indices; gather raw input first.
            click_edges(clicks, previous_clicks)
            previous_clicks = clicks
            now = time.monotonic()
            if DEBUG_INPUT:
                for i, joy, side in all_devices:
                    state = raw_state(joy)
                    if last_raw.get(i) != state:
                        if i in last_raw:
                            print(f'INPUT #{i}: axes={state[0]} pressed_buttons={state[1]} hats={state[2]}')
                        last_raw[i] = state
                if now - last_debug >= 2:
                    names = [f'#{i} name={j.get_name()!r} side={side or "unrecognized"} axes={j.get_numaxes()} buttons={j.get_numbuttons()} hats={j.get_numhats()}' for i, j, side in all_devices]
                    print(f'Mode={mode} | SDL devices={names or "none detected"}')
                    last_debug = now
            clock.tick(POLL_HZ)
    except KeyboardInterrupt:
        print('\nExiting.')
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()