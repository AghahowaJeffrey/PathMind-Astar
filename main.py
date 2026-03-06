"""
main.py
=======
Entry point for the A* Goal-Based Agent visualiser.

Usage
-----
    python main.py [map_name]

    map_name: one of 'Open Field', 'Maze', 'Corridors', 'Random (25% obstacles)'
              (default: 'Open Field')
"""

from __future__ import annotations

import sys

from constants import MAP_LABELS
from gui import GUIController


def main() -> None:
    # Allow the user to pass a map name as a CLI argument
    map_name = MAP_LABELS[0]
    if len(sys.argv) > 1:
        arg = " ".join(sys.argv[1:])
        if arg in MAP_LABELS:
            map_name = arg
        else:
            print(f"Unknown map '{arg}'. Available maps:")
            for m in MAP_LABELS:
                print(f"  - {m}")
            print(f"Defaulting to '{map_name}'.")

    app = GUIController(map_name=map_name)
    app.run()


if __name__ == "__main__":
    main()
