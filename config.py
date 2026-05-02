"""
config.py
=========
Shared configuration constants for the SQL automation pipeline.
"""

import os
import pyautogui

PASTE_SHORTCUT   = ("ctrl", "shift", "v")
QUERY_WAIT       = 5      # seconds to wait between queries
MYSQL_LOGIN_WAIT = 120     # seconds to wait for user to enter password

# Capture settings
STEPS_PER_PAGE   = 15
FOCUS_DELAY      = 1.0
MAX_PAGES        = 300
BATCH_SIZE       = 200    # scroll steps per batch when scrolling to top

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

pyautogui.FAILSAFE = True
pyautogui.PAUSE    = 0
