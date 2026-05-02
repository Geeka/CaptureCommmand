"""
028_Fest_DB SQL Automation Script
===================================
1. Browse and select a SQL file.
2. A new PowerShell window opens with mysql -u root -p.
3. User types password — script waits 60s.
4. Queries are pasted and executed one by one.
5. After last query, PowerShell scrollback is captured automatically.

Requirements:
    pip install pyautogui pyperclip pillow pywin32
"""

import sys
import time
import ctypes
import win32gui
import win32con

from config import MYSQL_LOGIN_WAIT
from initialize import ask_sql_filename, load_sql_queries, open_mysql_powershell, bring_to_front
from execute import run_automation


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    print("=" * 58)
    print("  028_Fest_DB SQL Automation Script")
    print("=" * 58 + "\n")

    # 1. Select SQL file
    sql_file = ask_sql_filename()
    queries  = load_sql_queries(sql_file)
    if not queries:
        print("[ERROR] No queries found in the SQL file.")
        sys.exit(1)
    print(f"[INFO] Loaded {len(queries)} queries.\n")
    print("[TIP]  Move mouse to top-left corner anytime to ABORT.\n")

    # 2. Open PowerShell + MySQL, grab hwnd
    hwnd = open_mysql_powershell()

    # 3. Wait for user to enter password
    print(f"[INFO] Waiting {MYSQL_LOGIN_WAIT}s for you to enter your MySQL password...")
    for i in range(MYSQL_LOGIN_WAIT, 0, -1):
        print(f"\r  Time remaining: {i}s ...  ", end="", flush=True)
        time.sleep(1)
    print()

    # 4. Focus and maximize PowerShell, then run queries
    bring_to_front(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.5)
    run_automation(queries, hwnd)
