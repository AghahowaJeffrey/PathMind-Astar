"""
gui.py
======
GUIController: pygame-based visualiser for the A* Goal-Based Agent.

Responsibilities
----------------
  - Render the grid and all cell states (empty, obstacle, open, closed,
    path, agent, start, goal).
  - Drive the A* generator one step per animation tick.
  - Drive the agent along the found path one step per animation tick.
  - Handle user input (buttons, keyboard shortcuts, map selector).
  - Display a real-time stats panel.

State machine
-------------
  IDLE        → waiting for user to press Start
  SEARCHING   → stepping through the A* generator
  FOUND       → path discovered; brief pause before agent movement
  MOVING      → agent traversing the final path
  NO_PATH     → open set exhausted; no solution
  PAUSED      → user pressed Space to freeze

Keyboard shortcuts
------------------
  Space  — pause / resume
  R      — reset
  S      — start search (when idle)
  1–4    — load predefined maps
  +/-    — increase / decrease animation speed
"""

from __future__ import annotations

import sys
import time
from typing import Iterator, List, Optional

import pygame

from agent import GoalBasedAgent
from astar import SearchStep
from constants import (
    AGENT_STEP_DELAY_MS,
    C_ACCENT, C_AGENT, C_BG, C_CLOSED, C_EMPTY, C_ERROR, C_GOAL, C_GREY,
    C_GRID_LINE, C_OBSTACLE, C_OPEN, C_PANEL_BG, C_PATH, C_START, C_SUCCESS,
    C_TOPBAR_BG, C_WARNING, C_WHITE,
    CELL_SIZE, DEFAULT_STEP_DELAY_MS, FPS, GRID_COLS, GRID_ROWS,
    MARGIN, MAP_LABELS, PANEL_WIDTH, TOP_BAR_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH,
)
from environment import GridWorld, State
from utils import get_predefined_map

# ---------------------------------------------------------------------------
# Simulation states
# ---------------------------------------------------------------------------
IDLE      = "IDLE"
SEARCHING = "SEARCHING"
FOUND     = "FOUND"
MOVING    = "MOVING"
NO_PATH   = "NO_PATH"
PAUSED    = "PAUSED"


class GUIController:
    """
    Main pygame application controller.

    Parameters
    ----------
    map_name : str
        Name of the predefined map to load on startup.
    """

    def __init__(self, map_name: str = MAP_LABELS[0]) -> None:
        pygame.init()
        pygame.display.set_caption("A* Goal-Based Agent  |  AI Pathfinding Demo")

        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._clock  = pygame.time.Clock()

        # Fonts
        self._font_title  = pygame.font.SysFont("monospace", 15, bold=True)
        self._font_body   = pygame.font.SysFont("monospace", 13)
        self._font_small  = pygame.font.SysFont("monospace", 11)
        self._font_stat   = pygame.font.SysFont("monospace", 12, bold=True)

        # Delay (ms) between search steps
        self._step_delay  = DEFAULT_STEP_DELAY_MS
        self._agent_delay = AGENT_STEP_DELAY_MS

        # Simulation state
        self._sim_state: str = IDLE
        self._pre_pause_state: str = IDLE

        # Map / agent
        self._current_map_idx: int = MAP_LABELS.index(map_name)
        self._grid: GridWorld = GridWorld.from_dict(
            get_predefined_map(MAP_LABELS[self._current_map_idx]))
        self._agent: GoalBasedAgent = GoalBasedAgent(self._grid)

        # A* generator reference
        self._search_gen: Optional[Iterator[SearchStep]] = None
        self._last_step: Optional[SearchStep] = None

        # Display overlay: open/closed sets, path, current
        self._open_cells: frozenset  = frozenset()
        self._closed_cells: frozenset = frozenset()
        self._path_cells: List[State] = []
        self._current_cell: Optional[State] = None

        # Timing accumulators (ms since last tick)
        self._search_accum: float = 0.0
        self._move_accum:   float = 0.0

        # Buttons (built lazily after layout is known)
        self._buttons: List[dict] = []
        self._build_buttons()

        # Message for status bar
        self._status_msg = "Press  START  or  S  to begin."

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _grid_origin(self) -> tuple:
        """Pixel (x, y) of the top-left corner of the grid."""
        return (MARGIN, TOP_BAR_HEIGHT + MARGIN)

    def _cell_rect(self, row: int, col: int) -> pygame.Rect:
        ox, oy = self._grid_origin()
        x = ox + col * CELL_SIZE
        y = oy + row * CELL_SIZE
        return pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

    def _cell_color(self, row: int, col: int) -> tuple:
        state = (row, col)
        if state == self._agent.current_position and self._sim_state in (MOVING, FOUND):
            return C_AGENT
        if state == self._grid.start:
            return C_START
        if state == self._grid.goal:
            return C_GOAL
        if state in self._grid.obstacles:
            return C_OBSTACLE
        if state in self._path_cells:
            return C_PATH
        if state == self._current_cell:
            return C_AGENT
        if state in self._closed_cells:
            return C_CLOSED
        if state in self._open_cells:
            return C_OPEN
        return C_EMPTY

    # ------------------------------------------------------------------
    # Button construction
    # ------------------------------------------------------------------

    def _panel_x(self) -> int:
        """Left edge of the right-side panel."""
        return WINDOW_WIDTH - PANEL_WIDTH

    def _build_buttons(self) -> None:
        px = self._panel_x() + 14
        btn_w, btn_h = PANEL_WIDTH - 28, 32
        y0 = TOP_BAR_HEIGHT + MARGIN + 10

        def btn(label: str, action: str, y: int, color=C_ACCENT) -> dict:
            return {"rect": pygame.Rect(px, y, btn_w, btn_h),
                    "label": label, "action": action, "color": color}

        self._buttons = [
            btn("▶  START  (S)",     "start",  y0),
            btn("⏸  PAUSE  (Space)", "pause",  y0 + 40),
            btn("↺  RESET  (R)",     "reset",  y0 + 80, color=(80, 80, 120)),
            # Map selector arrows
            btn("◀  Prev Map",        "prev_map", y0 + 140, color=(60, 60, 100)),
            btn("▶  Next Map",        "next_map", y0 + 180, color=(60, 60, 100)),
            # Speed controls
            btn("＋  Faster  (+)",    "faster",  y0 + 240, color=(60, 100, 80)),
            btn("－  Slower  (−)",    "slower",  y0 + 280, color=(100, 60, 60)),
        ]

    # ------------------------------------------------------------------
    # Simulation control
    # ------------------------------------------------------------------

    def _load_map(self, idx: int) -> None:
        self._current_map_idx = idx % len(MAP_LABELS)
        cfg = get_predefined_map(MAP_LABELS[self._current_map_idx])
        self._grid = GridWorld.from_dict(cfg)
        self._reset_display()

    def _start_search(self) -> None:
        if self._sim_state not in (IDLE, NO_PATH):
            return
        self._agent = GoalBasedAgent(self._grid)
        self._search_gen = self._agent.plan_generator()
        self._sim_state  = SEARCHING
        self._status_msg = "Searching…"
        self._search_accum = 0.0

    def _reset(self) -> None:
        self._reset_display()
        self._status_msg = "Press  START  or  S  to begin."

    def _reset_display(self) -> None:
        self._sim_state   = IDLE
        self._search_gen  = None
        self._last_step   = None
        self._open_cells  = frozenset()
        self._closed_cells = frozenset()
        self._path_cells  = []
        self._current_cell = None
        self._agent       = GoalBasedAgent(self._grid)
        self._search_accum = 0.0
        self._move_accum   = 0.0

    def _toggle_pause(self) -> None:
        if self._sim_state == PAUSED:
            self._sim_state = self._pre_pause_state
            self._status_msg = "Resumed."
        elif self._sim_state in (SEARCHING, MOVING):
            self._pre_pause_state = self._sim_state
            self._sim_state = PAUSED
            self._status_msg = "Paused — press  Space  to resume."

    def _step_search(self) -> None:
        """Advance A* by one expansion."""
        if self._search_gen is None:
            return
        try:
            step: SearchStep = next(self._search_gen)
            self._last_step    = step
            self._open_cells   = step.open_set
            self._closed_cells = step.closed_set
            self._current_cell = step.current

            if step.found:
                self._path_cells = step.path
                self._agent.record_result(step)
                self._sim_state  = FOUND
                self._status_msg = (
                    f"Path found!  Cost: {self._agent.path_cost}  |  "
                    f"Nodes explored: {self._agent.nodes_explored}"
                )
                self._move_accum = 0.0
                # Start agent movement after a short pause
                pygame.time.set_timer(pygame.USEREVENT, 600, loops=1)

            elif step.exhausted:
                self._agent.record_result(step)
                self._sim_state  = NO_PATH
                self._status_msg = "No path exists between start and goal."

        except StopIteration:
            self._sim_state = IDLE

    def _step_agent(self) -> None:
        """Advance agent by one step along the path."""
        if not self._agent.has_next_step():
            self._sim_state  = IDLE
            self._status_msg = "Agent reached the goal! ✓"
            return
        self._agent.advance()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _handle_button(self, action: str) -> None:
        if action == "start":
            self._start_search()
        elif action == "pause":
            self._toggle_pause()
        elif action == "reset":
            self._reset()
        elif action == "prev_map":
            self._load_map(self._current_map_idx - 1)
        elif action == "next_map":
            self._load_map(self._current_map_idx + 1)
        elif action == "faster":
            self._step_delay = max(5, self._step_delay - 10)
        elif action == "slower":
            self._step_delay = min(500, self._step_delay + 10)

    def _handle_events(self) -> bool:
        """Process pygame events. Return False if the app should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.USEREVENT:
                # Timer fires after path-found pause → begin agent animation
                if self._sim_state == FOUND:
                    self._sim_state = MOVING
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                if event.key == pygame.K_s:
                    self._start_search()
                if event.key == pygame.K_r:
                    self._reset()
                if event.key in (pygame.K_SPACE, pygame.K_p):
                    self._toggle_pause()
                if event.key in (pygame.K_KP_PLUS, pygame.K_EQUALS):
                    self._step_delay = max(5, self._step_delay - 10)
                if event.key in (pygame.K_KP_MINUS, pygame.K_MINUS):
                    self._step_delay = min(500, self._step_delay + 10)
                # Map hotkeys 1–4
                for i, k in enumerate([pygame.K_1, pygame.K_2,
                                        pygame.K_3, pygame.K_4]):
                    if event.key == k and i < len(MAP_LABELS):
                        self._load_map(i)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in self._buttons:
                    if b["rect"].collidepoint(event.pos):
                        self._handle_button(b["action"])
        return True

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _draw_topbar(self) -> None:
        bar = pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT)
        pygame.draw.rect(self._screen, C_TOPBAR_BG, bar)
        title = self._font_title.render(
            "A* Goal-Based Agent  —  Pathfinding Visualiser", True, C_WHITE)
        self._screen.blit(title, (MARGIN + 4, 10))
        sub = self._font_small.render(
            "f(n) = g(n) + h(n)  |  Heuristic: Manhattan Distance  |  "
            "Movement: 4-directional", True, C_GREY)
        self._screen.blit(sub, (MARGIN + 4, 32))

    def _draw_grid(self) -> None:
        for r in range(self._grid.rows):
            for c in range(self._grid.cols):
                colour = self._cell_color(r, c)
                rect   = self._cell_rect(r, c)
                pygame.draw.rect(self._screen, colour, rect, border_radius=3)

                # Draw agent position highlight ring
                if (r, c) == self._agent.current_position and self._sim_state == MOVING:
                    pygame.draw.rect(self._screen, C_WHITE, rect,
                                     width=2, border_radius=3)

    def _draw_panel(self) -> None:
        px = self._panel_x()
        panel_rect = pygame.Rect(px, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self._screen, C_PANEL_BG, panel_rect)
        pygame.draw.line(self._screen, (40, 44, 65), (px, 0), (px, WINDOW_HEIGHT), 2)

        # Title
        t = self._font_title.render("Controls", True, C_ACCENT)
        self._screen.blit(t, (px + 14, 14))

        # Buttons
        for b in self._buttons:
            mouse = pygame.mouse.get_pos()
            hover = b["rect"].collidepoint(mouse)
            shade = tuple(min(255, v + 30) for v in b["color"]) if hover else b["color"]
            pygame.draw.rect(self._screen, shade, b["rect"], border_radius=6)
            pygame.draw.rect(self._screen, C_WHITE, b["rect"], width=1, border_radius=6)
            lbl = self._font_body.render(b["label"], True, C_WHITE)
            lx  = b["rect"].x + (b["rect"].width - lbl.get_width()) // 2
            ly  = b["rect"].y + (b["rect"].height - lbl.get_height()) // 2
            self._screen.blit(lbl, (lx, ly))

        # ---- Statistics section ----
        sy = TOP_BAR_HEIGHT + MARGIN + 330
        self._draw_section_header("Statistics", px + 14, sy)
        sy += 24

        status_color = (
            C_SUCCESS if self._sim_state in (FOUND, MOVING, IDLE)
            and self._agent.plan_found
            else C_ERROR if self._sim_state == NO_PATH
            else C_WARNING if self._sim_state == SEARCHING
            else C_WHITE
        )
        state_label = {
            IDLE:      "Idle",
            SEARCHING: "Searching…",
            FOUND:     "Path Found ✓",
            MOVING:    "Agent Moving",
            NO_PATH:   "No Path Exists",
            PAUSED:    "Paused",
        }.get(self._sim_state, self._sim_state)

        stats = [
            ("State",     state_label,                           status_color),
            ("Map",       MAP_LABELS[self._current_map_idx],      C_WHITE),
            ("Heuristic", "Manhattan dist.",                      C_WHITE),
            ("Explored",  str(self._agent.nodes_explored),        C_ACCENT),
            ("Path len",  str(len(self._path_cells)) or "–",     C_ACCENT),
            ("Path cost", str(self._agent.path_cost) or "–",     C_ACCENT),
            ("Time (ms)", f"{self._agent.elapsed_ms:.1f}",       C_ACCENT),
            ("Step delay",f"{self._step_delay} ms",              C_GREY),
        ]
        for label, value, color in stats:
            lbl_surf = self._font_small.render(label + ":", True, C_GREY)
            val_surf = self._font_stat.render(value,         True, color)
            self._screen.blit(lbl_surf, (px + 14, sy))
            self._screen.blit(val_surf, (px + 14, sy + 13))
            sy += 32

        # ---- Legend ----
        ly2 = sy + 14
        self._draw_section_header("Legend", px + 14, ly2)
        ly2 += 24
        legend = [
            (C_START,    "Start"),
            (C_GOAL,     "Goal"),
            (C_OBSTACLE, "Obstacle"),
            (C_OPEN,     "Open set"),
            (C_CLOSED,   "Closed set"),
            (C_PATH,     "Final path"),
            (C_AGENT,    "Agent"),
        ]
        for colour, name in legend:
            pygame.draw.rect(self._screen, colour,
                             pygame.Rect(px + 14, ly2 + 3, 14, 14), border_radius=3)
            txt = self._font_small.render(name, True, C_WHITE)
            self._screen.blit(txt, (px + 34, ly2))
            ly2 += 20

        # ---- Keyboard cheatsheet ----
        ky = ly2 + 14
        self._draw_section_header("Keys", px + 14, ky); ky += 22
        keys = ["S — Start", "R — Reset", "Space — Pause",
                "1-4 — Maps", "+ / − — Speed"]
        for k in keys:
            t = self._font_small.render(k, True, C_GREY)
            self._screen.blit(t, (px + 14, ky))
            ky += 17

    def _draw_section_header(self, text: str, x: int, y: int) -> None:
        t = self._font_body.render(text, True, C_ACCENT)
        self._screen.blit(t, (x, y))
        pygame.draw.line(self._screen, C_GREY,
                         (x, y + 18), (x + PANEL_WIDTH - 28, y + 18), 1)

    def _draw_statusbar(self) -> None:
        """Bottom status bar spanning the grid area."""
        bar_y = WINDOW_HEIGHT - 22
        bar_w = self._panel_x() - MARGIN
        bar = pygame.Rect(MARGIN, bar_y, bar_w, 20)
        pygame.draw.rect(self._screen, (18, 20, 32), bar)
        txt = self._font_small.render(self._status_msg, True, C_GREY)
        self._screen.blit(txt, (MARGIN + 6, bar_y + 3))

    def _render(self) -> None:
        self._screen.fill(C_BG)
        self._draw_grid()
        self._draw_topbar()
        self._draw_panel()
        self._draw_statusbar()
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the application event loop."""
        running = True
        while running:
            dt = self._clock.tick(FPS)   # ms since last frame

            running = self._handle_events()

            # Advance simulation
            if self._sim_state == SEARCHING:
                self._search_accum += dt
                # Take as many steps as the accumulated time allows
                while self._search_accum >= self._step_delay:
                    self._search_accum -= self._step_delay
                    self._step_search()
                    if self._sim_state != SEARCHING:
                        break

            elif self._sim_state == MOVING:
                self._move_accum += dt
                if self._move_accum >= self._agent_delay:
                    self._move_accum -= self._agent_delay
                    self._step_agent()

            self._render()

        pygame.quit()
        sys.exit(0)
