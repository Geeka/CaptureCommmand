"""
execute.py
==========
Handles pasting and executing SQL queries in the PowerShell/MySQL window.
"""

import pyautogui
import pyperclip
import time

from config import PASTE_SHORTCUT, QUERY_WAIT
from initialize import bring_to_front
from capture import run_capture
from stitch import stitch_folder
from export_to_text import export_to_text


# ─────────────────────────────────────────
# PASTE & EXECUTE
# ─────────────────────────────────────────
def paste_and_execute(query: str, label: str = None):
    """Blank line → type label comment → paste query → Enter to execute."""
    pyautogui.press("enter")           # blank line for visual separation
    if label:
        pyperclip.copy(f"-- {label}")
        pyautogui.hotkey(*PASTE_SHORTCUT)
        time.sleep(0.3)
        pyautogui.press("enter")       # submit the comment line
        time.sleep(0.3)
    pyperclip.copy(query)
    pyautogui.hotkey(*PASTE_SHORTCUT)
    time.sleep(0.5)
    pyautogui.press("enter")           # execute query


# ─────────────────────────────────────────
# MAIN AUTOMATION LOOP
# ─────────────────────────────────────────
def run_automation(queries: list, hwnd: int):
    total = len(queries)
    print(f"\n{'='*58}")
    print(f"  028_Fest_DB SQL Automation — {total} queries")
    print(f"{'='*58}\n")
    
    for idx, (label, query) in enumerate(queries, start=1):
        if idx > 1:
            print(f"  Waiting {QUERY_WAIT}s for output...")
            time.sleep(QUERY_WAIT)
        if label:
            print(f"[{idx}/{total}] Label: {label}")
        preview = query.replace("\n", " ").strip()
        print(f"[{idx}/{total}] Pasting: {preview[:80]}{'...' if len(preview) > 80 else ''}")
        paste_and_execute(query, label=label)

    print(f"\n  Waiting {QUERY_WAIT}s for final query output...")
    time.sleep(QUERY_WAIT)
    pyautogui.press("enter")     # ensure last query is executed
    time.sleep(QUERY_WAIT)       # wait for its output
    print(f"\n{'='*58}")
    print(f"  ✅  All {total} queries executed!")
    print(f"{'='*58}\n")
    
    # Auto-capture scrollback
    print("[INFO] Starting PowerShell scrollback capture...")
    out_folder = run_capture(hwnd)

    # Auto-stitch screenshots into one image
    print("[INFO] Stitching screenshots into full_capture.png...")
    stitch_folder(out_folder)

    # Export PowerShell buffer to text
    #print("[INFO] Exporting PowerShell output to text...")
    #export_to_text(hwnd, out_folder)
