"""
initialize.py
=============
Handles SQL file selection, query loading, and PowerShell/MySQL setup.
"""

import sys
import time
import subprocess
import tkinter as tk
from tkinter import filedialog
import win32gui
import win32con

from config import FOCUS_DELAY, SCRIPT_DIR


# ─────────────────────────────────────────
# BROWSE FOR SQL FILE
# ─────────────────────────────────────────
def ask_sql_filename() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    filepath = filedialog.askopenfilename(
        title="Select SQL File",
        filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")],
        initialdir=SCRIPT_DIR
    )
    root.destroy()
    if not filepath:
        print("[ERROR] No file selected. Exiting.")
        sys.exit(0)
    print(f"[INFO] Selected: {filepath}")
    return filepath


# ─────────────────────────────────────────
# SQL LOADING
# ─────────────────────────────────────────
def load_sql_queries(filepath: str) -> list:
    """
    Returns a list of (label, query) tuples.
    Labels are extracted from -- comments (e.g. -- Q1_Before → 'Q1_Before').
    If no comment precedes a query, label is None.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results = []
    current_label = None
    current_query_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("--"):
            # Flush any pending query first
            if current_query_lines:
                query = " ".join(current_query_lines).strip()
                if query:
                    results.append((current_label, query))
                current_query_lines = []
                current_label = None
            # Extract label from comment
            comment_text = stripped.lstrip("-").strip()
            current_label = comment_text if comment_text else None

        elif stripped.startswith("/*"):
            pass  # skip block comment lines

        elif stripped:
            current_query_lines.append(stripped)
            if stripped.endswith(";"):
                query = " ".join(current_query_lines).strip()
                results.append((current_label, query))
                current_query_lines = []
                current_label = None

    # Flush any remaining query
    if current_query_lines:
        query = " ".join(current_query_lines).strip()
        if query:
            results.append((current_label, query))

    return results


# ─────────────────────────────────────────
# OPEN POWERSHELL + MYSQL
# ─────────────────────────────────────────
def open_mysql_powershell() -> int:
    """Open a new PowerShell window with mysql, return its hwnd."""
    subprocess.Popen([
        "powershell.exe", "-Command",
        "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'mysql -u root -v -p'"
    ])
    print("[INFO] Opening PowerShell and launching MySQL...")
    time.sleep(3)  # wait for window to appear

    hwnd = find_our_powershell()
    print(f"[INFO] Found PowerShell window (hwnd={hwnd})")
    return hwnd


def find_our_powershell() -> int:
    """Find the most recently opened PowerShell window."""
    results = []
    def _cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if title and ("powershell" in title.lower() or "pwsh" in title.lower()):
            results.append(hwnd)
    win32gui.EnumWindows(_cb, None)
    if not results:
        print("[WARN] No PowerShell window found.")
        return None
    return results[-1]  # most recently opened


# ─────────────────────────────────────────
# WINDOW FOCUS
# ─────────────────────────────────────────
def bring_to_front(hwnd: int):
    placement = win32gui.GetWindowPlacement(hwnd)
    if placement[1] == win32con.SW_SHOWMINIMIZED:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(FOCUS_DELAY)
