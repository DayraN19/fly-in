import math
import random
import pygame.font
import sys
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from drone import Drone
    from hub import Hub

BG_COLOR = (15, 21, 32)
EDGE_COLOR = (41, 56, 84)
EDGE_GLOW = (52, 152, 219)
TEXT_COLOR = (236, 240, 241)
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
            # Initialisation explicite du module de police de pygame
            pygame.font.init()

            # Utilisation de la police par défaut de Pygame (None) pour éviter les crashs de SysFont
            self.font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 18)
            self.has_font = True
        except Exception as e:
            print(f"[Visualizer] Mode de secours activé sans texte : {e}")
            self.font = None
            self.small_font = None
            self.has_font = False
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
        COLOR_MAP = {
            "vert": (46, 204, 113),
            "bleu": (52, 152, 219),
            "rouge": (231, 76, 60),
            "violet": (155, 89, 182),
            "orange": (230, 126, 34),
            "jaune": (241, 196, 15),
            "blanc": (236, 240, 241),
            "gris": (127, 140, 141),
            "noir": (22, 30, 46)
        }

        # 1. Dessin des lignes (Connexions)
        for hub_name, hub in self.all_hubs.items():
            start_pos = self.to_screen_coords(hub.x, hub.y)
            connections = hub.connections if hasattr(hub, 'connections') else []
            
            for neighbor in connections:
                neighbor_obj = neighbor if hasattr(neighbor, 'x') else self.all_hubs[neighbor]
                end_pos = self.to_screen_coords(neighbor_obj.x, neighbor_obj.y)
                
                if hub.current_drones_count > 0:
                    pygame.draw.line(self.screen, EDGE_GLOW, start_pos, end_pos, 4)
                else:
                    pygame.draw.line(self.screen, EDGE_COLOR, start_pos, end_pos, 2)

        # 2. Dessin des cercles (Stations)
        for hub_name, hub in self.all_hubs.items():
            pos = self.to_screen_coords(hub.x, hub.y)
            base_color = None
            
            # --- LECTURE INTELLIGENTE DE LA COULEUR DES MÉTADONNÉES ---
            if hasattr(hub, 'color') and hub.color:
                if isinstance(hub.color, str):
                    clean_color = hub.color.strip().lower()
                    
                    # Cas 1 : C'est un nom de couleur en français (ex: "vert")
                    if clean_color in COLOR_MAP:
                        base_color = COLOR_MAP[clean_color]
                    # Cas 2 : C'est du Hex (ex: "#FF0000" ou "0xFF0000")
                    else:
                        try:
                            hex_color = clean_color.lstrip('#').replace('0x', '')
                            base_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                        except ValueError:
                            base_color = None # En cas de chaîne corrompue, on laisse le fallback agir
                
                elif isinstance(hub.color, (tuple, list)) and len(hub.color) == 3:
                    base_color = hub.color # Déjà un format RGB (R, G, B)

            # Si aucune couleur n'a été trouvée ou valide dans la métadonnée, couleur par défaut :
            if base_color is None:
                if hub_name == "start":
                    base_color = (46, 204, 113)  # Vert de secours
                elif "goal" in hub_name or hub_name == "impossible_goal":
                    base_color = (155, 89, 182) # Violet de secours
                elif hub.max_drones == 1:
                    base_color = (231, 76, 60)   # Rouge Goulot
                else:
                    base_color = (52, 152, 219)  # Bleu standard

            # Dimensionnement des stations
            if hub_name == "start":
                radius = 35
            elif "goal" in hub_name or hub_name == "impossible_goal":
                radius = 40
            else:
                radius = 25

            # Effet d'aura lumineuse si des drones sont présents
            if hub.current_drones_count > 0:
                pygame.draw.circle(self.screen, [min(c + 50, 255) for c in base_color], pos, radius + 4, 2)
            
            # Rendu visuel de la station
            pygame.draw.circle(self.screen, (22, 30, 46), pos, radius)
            pygame.draw.circle(self.screen, base_color, pos, radius, 4)
            pygame.draw.circle(self.screen, base_color, pos, radius - 8, 1)
            
            # Jauge de remplissage interne (Capacité)
            if hub_name != "start" and hub_name != "impossible_goal":
                fill_ratio = hub.current_drones_count / hub.max_drones
                if fill_ratio > 0:
                    gauge_color = (230, 126, 34) if fill_ratio < 1 else (231, 76, 60)
                    pygame.draw.circle(self.screen, gauge_color, pos, int((radius - 10) * fill_ratio))

            # Affichage du texte si disponible
            if self.has_font and self.small_font:
                lbl_color = (241, 196, 15) if hub.current_drones_count > 0 else TEXT_COLOR
                txt = self.small_font.render(f"{hub_name} ({hub.current_drones_count}/{hub.max_drones})", True, lbl_color)
                self.screen.blit(txt, (pos[0] - 40, pos[1] - radius - 20))

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
        self.clock.tick(2)
