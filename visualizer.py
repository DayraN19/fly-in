"""
Graphical visualizer module using Pygame for the Fly-In drone simulation.
Modern Dark-Mode Edition with unified metadata coloring.
"""

import math
import random
import re
import sys
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from drone import Drone
    from hub import Hub

# --- PALETTE DE COULEURS INTERFACE (MODERNE & ÉPURÉE) ---
BG_COLOR = (11, 16, 25)        # Fond espace profond ultra-sombre
EDGE_COLOR = (28, 41, 61)      # Liaisons standards discrètes
TEXT_COLOR = (218, 227, 240)    # Blanc doux pour la lisibilité
WHITE = (255, 255, 255)
GOLD = (241, 196, 15)          # Accentuation turn et IDs


class GraphVisualizer:
    """Visualize the drone simulation using an advanced, sleek Pygame interface.

    Handles unified metadata colors for hubs, connections, and smooth rendering.
    """

    def __init__(self, all_hubs: dict[str, "Hub"],
                 drones: list["Drone"]) -> None:
        """Initialize the graphical visualizer with fallback safe fonts."""
        pygame.init()
        self.all_hubs: dict[str, "Hub"] = all_hubs
        self.drones: list["Drone"] = drones
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

        self.scale_x: int = 62
        self.scale_y: int = 140
        self.offset_x: int = 80
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

        # 1. Dessin des lignes (Connexions Cyber-Glow)
        for hub in self.all_hubs.values():
            start_pos = self.to_screen_coords(hub.x, hub.y)
            connections = hub.connections if hasattr(hub, 'connections') else []
            
            for neighbor in connections:
                neighbor_obj = (
                    neighbor if hasattr(neighbor, 'x') 
                    else self.all_hubs[neighbor]
                )
                end_pos = self.to_screen_coords(
                    neighbor_obj.x, neighbor_obj.y
                )
                
                # Si le hub source contient des drones, la ligne brille de sa couleur !
                if hub.current_drones_count > 0:
                    pygame.draw.line(
                        self.screen, (52, 152, 219), start_pos, end_pos, 3
                    )
                else:
                    pygame.draw.line(
                        self.screen, EDGE_COLOR, start_pos, end_pos, 1
                    )

        # 2. Dessin des cercles (Stations)
        for hub_name, hub in self.all_hubs.items():
            pos = self.to_screen_coords(hub.x, hub.y)
            base_color = None
            
            # --- EXTRACTION DE LA COULEUR DE CONFIGURATION EN ANGLAIS ---
            opt_str = getattr(hub, 'color', '')
            if isinstance(opt_str, str) and opt_str:
                match = re.search(r'color\s*=\s*([a-zA-Z0-9_-]+)', opt_str)
                if match:
                    clean_color = match.group(1).strip().lower()
                    if clean_color in color_map:
                        base_color = color_map[clean_color]
                    else:
                        try:
                            hex_color = clean_color.lstrip('#').replace('0x', '')
                            base_color = tuple(
                                int(hex_color[i:i+2], 16) for i in (0, 2, 4)
                            )
                        except ValueError:
                            base_color = None

            # Valeurs par défaut intelligentes si non spécifiées
            if base_color is None:
                if hub_name == "start":
                    base_color = (46, 204, 113)  # Vert
                elif "goal" in hub_name or hub_name == "impossible_goal":
                    base_color = (155, 89, 182)  # Violet
                elif getattr(hub, 'max_drones', 1) == 1:
                    base_color = (231, 76, 60)   # Rouge
                else:
                    base_color = (52, 152, 219)  # Bleu

            # Gestion des rayons
            if hub_name == "start":
                radius = 35
            elif "goal" in hub_name or hub_name == "impossible_goal":
                radius = 40
            else:
                radius = 26

            # Aura lumineuse unifiée s'il y a de l'activité
            if hub.current_drones_count > 0:
                aura = [min(c + 40, 255) for c in base_color]
                pygame.draw.circle(self.screen, aura, pos, radius + 5, 2)
            
            # Rendu visuel global unifié (Fini le centre rouge imposé !)
            pygame.draw.circle(self.screen, (17, 24, 37), pos, radius)
            pygame.draw.circle(self.screen, base_color, pos, radius, 3)
            pygame.draw.circle(self.screen, base_color, pos, radius - 6, 1)
            
            # JAUGE INTERNE HARMONISÉE (Utilise la même couleur, assombrie)
            max_dr = 
            if max_dr > 0:
                fill_ratio = min(1.0, hub.current_drones_count / max_dr)
                if fill_ratio > 0:
                    # Remplissage élégant basé sur la couleur propre du Hub
                    gauge_color = [int(c * 0.7) for c in base_color]
                    pygame.draw.circle(
                        self.screen, gauge_color, pos,
                        int((radius - 8) * fill_ratio)
                    )

            # Étiquettes de texte fluides
            if self.has_font and self.small_font:
                lbl_color = GOLD if hub.current_drones_count > 0 else TEXT_COLOR
                txt = self.small_font.render(
                    f"{hub_name} ({hub.current_drones_count}/{max_dr})",
                    True, lbl_color
                )
                self.screen.blit(txt, (pos[0] - 40, pos[1] - radius - 20))

    def draw_drones(self) -> None:
        """Draw custom futuristic drones with detailed positioning."""
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
                    dist = 52 if drone.zone == "impossible_goal" else 46
                    pos = (
                        int(pos_start[0] + dist * math.cos(angle)),
                        int(pos_start[1] + dist * math.sin(angle)),
                    )
                else:
                    random.seed(i)
                    pos = (
                        pos_start[0] + random.randint(-10, 10),
                        pos_start[1] + random.randint(-10, 10),
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
                f"FLY-IN SYSTEM CORE  |  TURN {self.turn}", True, TEXT_COLOR
            )
            self.screen.blit(surface, (35, 30))

        pygame.display.flip()
        self.clock.tick(4)
