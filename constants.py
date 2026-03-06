"""
constants.py
============
Central configuration for the A* Goal-Based Agent visualiser.

All tuneable values (colours, sizes, frame-rates, etc.) live here so that
the rest of the codebase stays free of magic numbers.
"""

# ---------------------------------------------------------------------------
# Grid geometry
# ---------------------------------------------------------------------------
CELL_SIZE: int = 36          # Pixel width/height of each grid cell
GRID_COLS: int = 25          # Number of columns in the default grid
GRID_ROWS: int = 18          # Number of rows in the default grid
GRID_PADDING: int = 2        # Gap between cells (pixels)

# ---------------------------------------------------------------------------
# Window layout
# ---------------------------------------------------------------------------
PANEL_WIDTH: int = 280       # Right-side stats panel width (pixels)
TOP_BAR_HEIGHT: int = 54     # Top bar height for title / toolbar
MARGIN: int = 6              # Outer canvas margin

WINDOW_WIDTH: int = CELL_SIZE * GRID_COLS + PANEL_WIDTH + MARGIN * 2
WINDOW_HEIGHT: int = CELL_SIZE * GRID_ROWS + TOP_BAR_HEIGHT + MARGIN * 2

FPS: int = 60                # Target frame-rate

# ---------------------------------------------------------------------------
# Animation timing
# ---------------------------------------------------------------------------
DEFAULT_STEP_DELAY_MS: int = 40   # ms between A* steps during exploration
AGENT_STEP_DELAY_MS: int  = 80   # ms between agent movement steps

# ---------------------------------------------------------------------------
# Colours  (R, G, B)
# ---------------------------------------------------------------------------
# Background / structure
C_BG          = (15,  17,  26)   # Dark navy background
C_GRID_LINE   = (30,  34,  50)   # Subtle grid lines
C_PANEL_BG    = (20,  22,  32)   # Side-panel background
C_TOPBAR_BG   = (12,  14,  22)   # Top bar background

# Cell states
C_EMPTY       = (38,  42,  60)   # Unvisited cell
C_OBSTACLE    = (55,  55,  70)   # Blocked cell
C_START       = (52, 211, 153)   # Emerald green – start node
C_GOAL        = (251, 113, 133)  # Rose – goal node
C_OPEN        = (56, 189, 248)   # Sky-blue – in open set
C_CLOSED      = (99,  98, 200)   # Muted purple – in closed set
C_PATH        = (250, 204,  21)  # Amber – final path
C_AGENT       = (239, 68,   68)  # Vivid red – agent position

# UI text / accents
C_WHITE       = (235, 238, 245)
C_GREY        = (110, 115, 140)
C_ACCENT      = ( 99, 202, 229)
C_SUCCESS     = ( 52, 211, 153)
C_ERROR       = (239,  68,  68)
C_WARNING     = (250, 204,  21)

# ---------------------------------------------------------------------------
# Agent / algorithm
# ---------------------------------------------------------------------------
MOVE_COST: int = 1           # Cost per step (uniform grid)

# ---------------------------------------------------------------------------
# Predefined map identifiers
# ---------------------------------------------------------------------------
MAP_OPEN_FIELD   = "Open Field"
MAP_MAZE         = "Maze"
MAP_CORRIDORS    = "Corridors"
MAP_RANDOM       = "Random (25% obstacles)"
MAP_LABELS = [MAP_OPEN_FIELD, MAP_MAZE, MAP_CORRIDORS, MAP_RANDOM]
