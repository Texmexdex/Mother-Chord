"""
TeX's Mother-Chord
TeXmExDeX Type Tunes
Main entry point
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import run_app

if __name__ == "__main__":
    run_app()
