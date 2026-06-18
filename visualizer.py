import math
import random
import sys
from typing import TYPE_CHECKING, Optional

import pygame

if TYPE_CHECKING:
    from drone import Drone
    from hub import Hub

BG_COLOR = (11, 16, 25)
EDGE_COLOR = (52, 73, 94)
EDGE_ACTIVE = (46, 134, 193)
WHITE = (255, 255, 255)
GOLD = (241, 196, 15)


class GraphVisualizer:
    """
    Visualize the drone simulation using Pygame.

    This class is responsible for drawing hubs, connections,
    drones, and updating the display after each simulation turn.

    Attributes:
        all_hubs (dict[str, Hub]): Dictionary containing all hubs.
        drones (list[Drone]): List of drones in the simulation.
        turn (int): Current simulation turn.
        width (int): Width of the window.
        height (int): Height of the window.
        screen (pygame.Surface): Main drawing surface.
        clock (pygame.time.Clock): Controls the frame rate.
    """
    def __init__(self, all_hubs: dict[str, "Hub"],
                 drones: list["Drone"]) -> None:
        """
    Initialize the graphical visualizer.

    Args:
        all_hubs (dict[str, Hub]): Dictionary of all hubs.
        drones (list[Drone]): List of drones to display.

    Returns:
        None
    """
        pygame.init()
        self.all_hubs: dict[str, "Hub"] = all_hubs
        self.drones: list["Drone"] = drones
        self.turn: int = 0

        self.width: int = 1650
        self.height: int = 950
        self.screen: pygame.surface.Surface = pygame.display.set_mode(
            (self.width, self.height)
        )
        pygame.display.set_caption("42 FLY-IN - VISUALIZER PRO")

        self.clock: pygame.time.Clock = pygame.time.Clock()

        try:
            self.font: pygame.font.Font = pygame.font.SysFont(
                "Arial", 13, bold=True
            )
            self.title_font: pygame.font.Font = pygame.font.SysFont(
                "Arial", 22, bold=True
            )
            self.has_font: bool = True
        except Exception:
            self.has_font = False

        self.scale_x: int = 62
        self.scale_y: int = 140
        self.offset_x: int = 80
        self.offset_y: int = self.height // 2

    def to_screen_coords(self, x: float, y: float) -> tuple[int, int]:
        """
    Convert world coordinates into screen coordinates.

    Args:
        x (float): Horizontal position in the graph.
        y (float): Vertical position in the graph.

    Returns:
        tuple[int, int]: Coordinates adapted to the screen.
    """
        screen_x = int(x * self.scale_x + self.offset_x)
        screen_y = int(-y * self.scale_y + self.offset_y)
        return screen_x, screen_y

    def draw_text(
        self,
        text: str,
        pos: tuple[int, int],
        color: tuple[int, int, int] = WHITE,
        bg_color: tuple[int, int, int] = (26, 36, 54),
    ) -> None:
        """
    Draw text with a colored background.

    Args:
        text (str): Text to display.
        pos (tuple[int, int]): Position on the screen.
        color (tuple[int, int, int]): Text color.
        bg_color (tuple[int, int, int]): Background color.

    Returns:
        None
    """
        if self.has_font:
            surface = self.font.render(text, True, color)
            rect = surface.get_rect(center=pos)
            bg = rect.inflate(8, 4)
            pygame.draw.rect(self.screen, bg_color, bg, border_radius=4)
            pygame.draw.rect(self.screen, EDGE_COLOR, bg, 1, border_radius=4)
            self.screen.blit(surface, rect)

    def draw_graph(self) -> None:
        """
    Draw all hubs and their connections.

    Active connections are highlighted, and each hub
    is displayed with its occupancy information.

    Returns:
        None"""
        for hub in self.all_hubs.values():
            start_pos = self.to_screen_coords(hub.x, hub.y)
            connections: list["Hub"] = (
                hub.connections
                if hasattr(hub, "connections")
                else []
            )
            for neighbor in connections:
                neighbor_obj: Optional["Hub"] = None
                if hasattr(neighbor, "x") and hasattr(neighbor, "y"):
                    neighbor_obj = neighbor
                elif isinstance(neighbor, str):
                    neighbor_obj = self.all_hubs.get(neighbor)

                if neighbor_obj is None:
                    continue

                end_pos = self.to_screen_coords(
                    neighbor_obj.x, neighbor_obj.y
                )
                is_active = hub.current_drones_count > 0
                color = EDGE_ACTIVE if is_active else EDGE_COLOR
                width = 3 if is_active else 1
                pygame.draw.line(
                    self.screen, color, start_pos, end_pos, width
                )

        for hub_name, hub in self.all_hubs.items():
            pos = self.to_screen_coords(hub.x, hub.y)
            radius = 24
            if hub_name in ("start", "impossible_goal"):
                radius = 35

            if hub_name == "start":
                color = (46, 204, 113)
            elif hub_name == "impossible_goal":
                color = (155, 89, 182)
            elif "gate_hell" in hub_name:
                color = (231, 76, 60)
            elif "trap" in hub_name:
                color = (142, 68, 173)
            elif "dead" in hub_name:
                color = (44, 62, 80)
            elif "loop" in hub_name:
                color = (211, 84, 0)
            elif "overflow" in hub_name:
                color = (192, 57, 43)
            elif "false_hope" in hub_name or "priority" in hub_name:
                color = (241, 196, 15)
            elif "conv_restricted" in hub_name:
                color = (120, 40, 40)
            else:
                color = (52, 152, 219)

            pygame.draw.circle(self.screen, (20, 27, 41), pos, radius)
            pygame.draw.circle(self.screen, color, pos, radius, 3)

            max_drones = getattr(hub, "max_drones", 1)
            label = f"{hub_name} [{hub.current_drones_count}/{max_drones}]"
            self.draw_text(label, (pos[0], pos[1] - radius - 14), color=WHITE)

    def draw_drones(self) -> None:
        """
    Draw drones at their current positions.

    Drones in transit are displayed between two hubs,
    while stationary drones are drawn around their hub.

    Returns:
        None
    """
        for i, drone in enumerate(self.drones):
            hub_actuel = self.all_hubs.get(drone.zone)
            if not hub_actuel:
                continue
            pos_start = self.to_screen_coords(hub_actuel.x, hub_actuel.y)
            transit_turns = getattr(drone, "transit_turns_left", 0)
            connection = getattr(drone, "connection", "")

            if transit_turns == 2 and connection:
                hub_cible = self.all_hubs.get(connection)
                if hub_cible:
                    pos_end = self.to_screen_coords(hub_cible.x, hub_cible.y)
                    pos = (
                        int((pos_start[0] + pos_end[0]) / 2),
                        int((pos_start[1] + pos_end[1]) / 2),
                    )
                else:
                    pos = pos_start
            else:
                if drone.zone in ("start", "impossible_goal"):
                    num_drones_here = len(
                        [d for d in self.drones if d.zone == drone.zone]
                    )
                    idx_here = [
                        d for d in self.drones if d.zone == drone.zone
                    ].index(drone)
                    angle = (2 * math.pi * idx_here) / (
                        num_drones_here if num_drones_here > 0 else 1
                    )
                    dist = 50 if drone.zone == "impossible_goal" else 45
                    pos = (
                        int(pos_start[0] + dist * math.cos(angle)),
                        int(pos_start[1] + dist * math.sin(angle)),
                    )
                else:
                    random.seed(i)
                    pos = (
                        pos_start[0] + random.randint(-12, 12),
                        pos_start[1] + random.randint(-12, 12),
                    )

            if getattr(drone, "transit_turns_left", 0) == 1:
                color_drone = (231, 76, 60)
            else:
                color_drone = (230, 126, 34)

            pygame.draw.circle(self.screen, color_drone, pos, 9)
            pygame.draw.circle(self.screen, WHITE, pos, 9, 1)

            drone_id = getattr(drone, "id", f"{i+1}")
            self.draw_text(
                f"D{drone_id}",
                (pos[0], pos[1] + 16),
                color=GOLD,
                bg_color=color_drone,
            )

    def run_turn(self) -> None:
        """
    Update and display a new simulation frame.

    Processes events, redraws the graph and drones,
    refreshes the display, and limits the frame rate.

    Returns:
        None"""
        self.turn += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(BG_COLOR)
        self.draw_graph()
        self.draw_drones()

        if self.has_font:
            surface = self.title_font.render(
                f"SIMULATION TURN :{self.turn}", True, GOLD
            )
            self.screen.blit(surface, (30, 25))

        pygame.display.flip()
        self.clock.tick(8)
