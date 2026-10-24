"""Joy-Con Mouse: use analog sticks for pointer movement; no gyro/accelerometer."""
from __future__ import annotations
import time
import tkinter as tk
from tkinter import ttk
import pygame
import pyautogui

DEADZONE = 0.16
DEFAULT_SPEED = 600.0
MIN_SPEED = 100
MAX_SPEED = 2000
POLL_MS = 8
DEBUG_INPUT = True
BUTTONS = {'A': 0, 'B': 1, 'X': 2, 'Y': 3, 'R': 6, 'ZR': 7, 'L': 6, 'ZL': 7}
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

class JoyConMouseApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Joy-Con Mouse')
        self.root.geometry('440x220')
        self.root.minsize(400, 200)
        self.speed = tk.DoubleVar(value=DEFAULT_SPEED)
        self.status = tk.StringVar(value='Joy-Conを検索中…')
        self.speed_text = tk.StringVar(value=f'{int(DEFAULT_SPEED)} px/s')
        self.previous_clicks: set[str] = set()
        self.last_raw: dict[int, tuple] = {}
        self.last_debug = 0.0
        self.closed = False

        frame = ttk.Frame(root, padding=18)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='カーソル速度', font=('', 12, 'bold')).pack(anchor='w')
        row = ttk.Frame(frame)
        row.pack(fill='x', pady=(8, 4))
        self.scale = ttk.Scale(row, from_=MIN_SPEED, to=MAX_SPEED, variable=self.speed,
                               command=self.on_speed_change)
        self.scale.pack(side='left', fill='x', expand=True, padx=(0, 12))
        ttk.Label(row, textvariable=self.speed_text, width=10, anchor='e').pack(side='right')
        ttk.Label(frame, text='遅い  ←────────→  速い').pack(anchor='w')
        ttk.Separator(frame).pack(fill='x', pady=12)
        ttk.Label(frame, textvariable=self.status, wraplength=390).pack(anchor='w')
        ttk.Label(frame, text='両方のスティックに対応 / ジャイロ不使用 / 終了: ウィンドウを閉じる',
                  wraplength=390).pack(anchor='w', pady=(8, 0))
        self.root.protocol('WM_DELETE_WINDOW', self.close)

    def on_speed_change(self, _value=None):
        self.speed_text.set(f'{int(self.speed.get())} px/s')

    def close(self):
        self.closed = True
        self.root.destroy()

    def tick(self):
        if self.closed:
            return
        try:
            pygame.event.pump()
            devices = []
            for i in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(i)
                if not joy.get_init():
                    joy.init()
                devices.append((i, joy, classify(joy.get_name())))

            lefts = [j for _, j, side in devices if side == 'L']
            rights = [j for _, j, side in devices if side == 'R']
            combined = [j for _, j, side in devices if side == 'LR']
            mode = 'LR' if (lefts and rights) or combined else 'L' if lefts else 'R' if rights else 'NONE'

            # Use both sticks. On a combined SDL device, axes 0/1 are usually the
            # left stick and 2/3 the right stick; separate devices use axes 0/1 each.
            vectors = []
            if combined:
                j = combined[0]
                vectors.append((axis(j, 0), axis(j, 1)))
                vectors.append((axis(j, 2), axis(j, 3)))
            else:
                if lefts:
                    vectors.append((axis(lefts[0], 0), axis(lefts[0], 1)))
                if rights:
                    vectors.append((axis(rights[0], 0), axis(rights[0], 1)))
            vx = max(-1.0, min(1.0, sum(v[0] for v in vectors)))
            vy = max(-1.0, min(1.0, sum(v[1] for v in vectors)))
            speed = float(self.speed.get())
            dt = POLL_MS / 1000.0
            dx, dy = round(vx * speed * dt), round(vy * speed * dt)
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
            click_edges(clicks, self.previous_clicks)
            self.previous_clicks = clicks

            now = time.monotonic()
            if DEBUG_INPUT:
                for i, joy, side in devices:
                    state = raw_state(joy)
                    if self.last_raw.get(i) != state:
                        if i in self.last_raw:
                            print(f'INPUT #{i}: axes={state[0]} pressed_buttons={state[1]} hats={state[2]}')
                        self.last_raw[i] = state
                if now - self.last_debug >= 2:
                    names = [f'#{i} {j.get_name()!r} side={side or "unrecognized"}' for i, j, side in devices]
                    print(f'Mode={mode} | SDL devices={names or "none detected"}')
                    self.last_debug = now
            self.status.set(f'Mode: {mode} | 検出デバイス: {len(devices)}台')
        except pyautogui.FailSafeException:
            self.status.set('安全停止しました。再起動するには一度終了して起動し直してください。')
            print('PyAutoGUI failsafe triggered; closing app loop.')
            self.closed = True
            self.root.after(0, self.root.destroy)
            return
        except Exception as exc:
            self.status.set(f'入力エラー: {exc}')
            print(f'Input error: {exc}')
        self.root.after(POLL_MS, self.tick)

def main() -> None:
    pygame.init()
    pygame.joystick.init()
    root = tk.Tk()
    app = JoyConMouseApp(root)
    print('Joy-Con Mouse started. GUI slider adjusts cursor speed; gyro is not used.')
    print('Move the sticks/buttons to print raw input changes in this console.')
    app.tick()
    try:
        root.mainloop()
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
