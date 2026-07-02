"""Graphical visualizer module using Pygame for the Fly-In drone simulation.

Modern Dark-Mode Edition with unified metadata coloring.
"""

import math
import re
import sys
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from drone import Drone
    from hub import Hub

BG_COLOR = (11, 16, 25)
EDGE_COLOR = (28, 41, 61)
TEXT_COLOR = (218, 227, 240)
WHITE = (255, 255, 255)
GOLD = (241, 196, 15)


class GraphVisualizer:
    """Visualize the drone simulation using an advanced,
    sleek Pygame interface.

    Handles unified metadata colors for hubs, connections, and smooth
    rendering.
    """

    def __init__(self, all_hubs: dict[str, "Hub"],
                 drones: list["Drone"],
                 parse_instance: any) -> None:
        """Initialize the graphical visualizer with fallback safe fonts."""
        pygame.init()
        self.all_hubs: dict[str, "Hub"] = all_hubs
        self.drones: list["Drone"] = drones
        self.parse = parse_instance
        self.turn: int = 0

        self.width: int = 1650
        self.height: int = 950
        self.screen: pygame.surface.Surface = pygame.display.set_mode(
            (self.width, self.height)
        )
        pygame.display.set_caption("42 FLY-IN - PREMIUM VISUALIZER")

        self.clock: pygame.time.Clock = pygame.time.Clock()

        try:
            pygame.font.init()
            self.font = pygame.font.Font(None, 22)
            self.small_font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 34)
            self.has_font = True
        except Exception as e:
            print(f"[Visualizer] Emergency font bypass triggered: {e}")
            self.font = None
            self.small_font = None
            self.title_font = None
            self.has_font = False

        num_hubs = len(all_hubs)
        if num_hubs <= 6:
            self.scale_x = 220
            self.scale_y = 260
            self.offset_x = 250
        else:
            self.scale_x = 62
            self.scale_y = 140
            self.offset_x = 80
        self.offset_y: int = self.height // 2

    def to_screen_coords(self, x: float, y: float) -> tuple[int, int]:
        """Convert world coordinates into screen coordinates."""
        screen_x = int(x * self.scale_x + self.offset_x)
        screen_y = int(-y * self.scale_y + self.offset_y)
        return screen_x, screen_y

    def draw_text(
        self,
        text: str,
        pos: tuple[int, int],
        color: tuple[int, int, int] = WHITE,
        bg_color: tuple[int, int, int] = (20, 30, 45),
    ) -> None:
        """Draw text with a subtle rounded background card."""
        if self.has_font and self.font:
            surface = self.font.render(text, True, color)
            rect = surface.get_rect(center=pos)
            bg = rect.inflate(10, 6)
            pygame.draw.rect(self.screen, bg_color, bg, border_radius=5)
            pygame.draw.rect(self.screen, EDGE_COLOR, bg, 1, border_radius=5)
            self.screen.blit(surface, rect)

    def draw_graph(self) -> None:
        """Draw connections and hubs utilizing full unified color themes."""
        color_map = {
            "green": (46, 204, 113),
            "blue": (52, 152, 219),
            "red": (231, 76, 60),
            "purple": (155, 89, 182),
            "orange": (230, 126, 34),
            "yellow": (241, 196, 15),
            "white": (236, 240, 241),
            "gray": (127, 140, 141),
            "grey": (127, 140, 141),
            "black": (34, 47, 62)
        }

        for hub in self.all_hubs.values():
            start_pos = self.to_screen_coords(hub.x, hub.y)
            connections = getattr(hub, 'connections', [])

            for neighbor in connections:
                neighbor_obj = (
                    neighbor if hasattr(neighbor, 'x')
                    else self.all_hubs[neighbor]
                )
                end_pos = self.to_screen_coords(
                    neighbor_obj.x, neighbor_obj.y
                )

                if hub.current_drones_count > 0:
                    pygame.draw.line(
                        self.screen, (52, 152, 219), start_pos, end_pos, 3
                    )
                else:
                    pygame.draw.line(
                        self.screen, EDGE_COLOR, start_pos, end_pos, 1
                    )

        for hub_name, hub in self.all_hubs.items():
            pos = self.to_screen_coords(hub.x, hub.y)
            base_color = None
            opt_str = getattr(hub, 'color', '')
            if isinstance(opt_str, str) and opt_str:
                match = re.search(r'color\s*=\s*([a-zA-Z0-9_-]+)', opt_str)
                if match:
                    clean_color = match.group(1).strip().lower()
                    if clean_color in color_map:
                        base_color = color_map[clean_color]
                    else:
                        try:
                            hex_color = (clean_color.lstrip('#')
                                         .replace('0x', ''))
                            base_color = tuple(
                                int(hex_color[i:i+2], 16) for i in (0, 2, 4)
                            )
                        except ValueError:
                            base_color = None

            if base_color is None:
                if hub_name == "start":
                    base_color = (46, 204, 113)
                elif "goal" in hub_name or hub_name == "impossible_goal":
                    base_color = (155, 89, 182)
                elif getattr(hub, 'max_drones', 1) == 1:
                    base_color = (231, 76, 60)
                else:
                    base_color = (52, 152, 219)

            if hub_name == "start":
                radius = 35
            elif "goal" in hub_name or hub_name == "impossible_goal":
                radius = 40
            else:
                radius = 26

            if hub.current_drones_count > 0:
                aura = [min(c + 40, 255) for c in base_color]
                pygame.draw.circle(self.screen, aura, pos, radius + 5, 2)
            pygame.draw.circle(self.screen, (17, 24, 37), pos, radius)
            pygame.draw.circle(self.screen, base_color, pos, radius, 3)
            pygame.draw.circle(self.screen, base_color, pos, radius - 6, 1)
            limit_drones = self.parse.zones_max_drones.get(hub_name, 0)

            if limit_drones > 0:
                fill_ratio = min(1.0, hub.current_drones_count / limit_drones)
                if fill_ratio > 0:
                    gauge_color = [int(c * 0.7) for c in base_color]
                    pygame.draw.circle(
                        self.screen, gauge_color, pos,
                        int((radius - 8) * fill_ratio)
                    )

            if self.has_font and self.small_font:
                if hub.current_drones_count > 0:
                    lbl_color = GOLD
                else:
                    lbl_color = TEXT_COLOR
                txt = self.small_font.render(
                    f"{hub_name} ({hub.current_drones_count}/{limit_drones})",
                    True, lbl_color
                )
                self.screen.blit(txt, (pos[0] - 40, pos[1] - radius - 24))

    def draw_drones(self) -> None:
        """Draw custom futuristic drones with detailed positioning."""
        drones_by_zone: dict[str, list[any]] = {}
        for drone in self.drones:
            zone_name = drone.zone
            if zone_name not in drones_by_zone:
                drones_by_zone[zone_name] = []
            drones_by_zone[zone_name].append(drone)

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
                zone_drones = drones_by_zone.get(drone.zone, [])
                num_drones_here = len(zone_drones)

                if num_drones_here <= 1:
                    pos = pos_start
                else:
                    idx_here = zone_drones.index(drone)
                    angle = (2 * math.pi * idx_here) / num_drones_here

                    if drone.zone == "impossible_goal":
                        dist = 52
                    elif drone.zone == "start":
                        dist = 46
                    else:
                        dist = 36

                    pos = (
                        int(pos_start[0] + dist * math.cos(angle)),
                        int(pos_start[1] + dist * math.sin(angle)),
                    )

            color_drone = (
                (230, 126, 34) if transit_turns == 1 else (241, 196, 15)
            )

            pygame.draw.circle(self.screen, color_drone, pos, 8)
            pygame.draw.circle(self.screen, WHITE, pos, 8, 1)

            drone_id = getattr(drone, "id", f"{i+1}")
            self.draw_text(
                f"D{drone_id}",
                (pos[0], pos[1] + 16),
                color=WHITE,
                bg_color=color_drone,
            )

    def run_turn(self) -> None:
        """Update display frame and enforce clean tick constraints."""
        self.turn += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(BG_COLOR)
        self.draw_graph()
        self.draw_drones()

        if self.has_font and self.title_font:
            surface = self.title_font.render(
                f"FLY-IN SYSTEM CORE | TURN {self.turn - 1}", True, TEXT_COLOR
            )
            self.screen.blit(surface, (35, 30))

        pygame.display.flip()
        self.clock.tick(1)
