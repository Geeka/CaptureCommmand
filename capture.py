"""
capture.py
==========
Handles PowerShell scrollback capture — scrolling to top, taking screenshots
page by page, and saving them to a timestamped folder.
"""

import pyautogui
import time
import os
import datetime
from PIL import ImageGrab
import win32gui

from config import STEPS_PER_PAGE, FOCUS_DELAY, MAX_PAGES, BATCH_SIZE, SCRIPT_DIR
from initialize import bring_to_front


# ─────────────────────────────────────────
# OUTPUT FOLDER
# ─────────────────────────────────────────
def make_output_folder() -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(SCRIPT_DIR, "screenshots", f"ps_capture_{ts}")
    os.makedirs(folder, exist_ok=True)
    return folder


# ─────────────────────────────────────────
# SCREEN CAPTURE HELPERS
# ─────────────────────────────────────────
def get_client_rect_screen(hwnd: int):
    left, top = win32gui.ClientToScreen(hwnd, (0, 0))
    cr = win32gui.GetClientRect(hwnd)
    return left, top, left + cr[2], top + cr[3]


def capture(hwnd: int):
    return ImageGrab.grab(bbox=get_client_rect_screen(hwnd))


def frames_identical(img1, img2) -> bool:
    if img1.size != img2.size:
        return False
    return img1.tobytes() == img2.tobytes()


# ─────────────────────────────────────────
# SCROLLING
# ─────────────────────────────────────────
def scroll_to_top(hwnd: int):
    BATCH_PAUSE = 0.3
    bring_to_front(hwnd)
    pyautogui.hotkey("ctrl", "shift", "end")
    time.sleep(0.3)
    print("    Scrolling to top ", end="", flush=True)
    while True:
        for _ in range(BATCH_SIZE):
            pyautogui.hotkey("ctrl", "shift", "up")
        time.sleep(BATCH_PAUSE)
        before = capture(hwnd)
        pyautogui.hotkey("ctrl", "shift", "up")
        time.sleep(BATCH_PAUSE)
        after = capture(hwnd)
        print(".", end="", flush=True)
        if frames_identical(before, after):
            print(" done.")
            break


def scroll_one_page_down(hwnd: int):
    bring_to_front(hwnd)
    for _ in range(STEPS_PER_PAGE):
        pyautogui.hotkey("ctrl", "shift", "down")
    time.sleep(0.3)


# ─────────────────────────────────────────
# MAIN CAPTURE ROUTINE
# ─────────────────────────────────────────
def run_capture(hwnd: int) -> str:
    print("\n" + "=" * 60)
    print("  PowerShell Scrolling Screenshot Capture")
    print(f"  Steps per page : {STEPS_PER_PAGE}")
    print("=" * 60)

    bring_to_front(hwnd)
    time.sleep(0.5)

    print("\nScrolling to top ...")
    scroll_to_top(hwnd)

    out_folder = make_output_folder()
    print(f"-> Output folder: {out_folder}")
    print("\nCapturing — do NOT move mouse or switch windows.\n")

    bring_to_front(hwnd)
    page = 1
    prev = None

    while page <= MAX_PAGES:
        current = capture(hwnd)
        if prev is not None and frames_identical(prev, current):
            print("\n[DONE] Bottom of buffer reached.")
            break
        filename = os.path.join(out_folder, f"page_{page:04d}.png")
        current.save(filename)
        print(f"  [OK] page {page:>3}  ->  {os.path.basename(filename)}")
        prev = current
        scroll_one_page_down(hwnd)
        page += 1
    else:
        print(f"\n[!] Safety cap of {MAX_PAGES} pages reached — stopping.")

    print(f"\n{'=' * 60}")
    print(f"  Pages captured : {page - 1}")
    print(f"  Output folder  : {out_folder}")
    print(f"{'=' * 60}\n")

    return out_folder
