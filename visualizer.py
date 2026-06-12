import pygame
import sys
import math
import random

BG_COLOR = (11, 16, 25)
EDGE_COLOR = (52, 73, 94)
EDGE_ACTIVE = (46, 134, 193)
WHITE = (255, 255, 255)
GOLD = (241, 196, 15)


class GraphVisualizer:
    def __init__(self, all_hubs, drones):
        pygame.init()
        self.all_hubs = all_hubs
        self.drones = drones
        self.turn = 0

        self.width, self.height = 1650, 950
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("42 FLY-IN - VISUALIZER PRO")

        self.clock = pygame.time.Clock()

        try:
            self.font = pygame.font.SysFont("Arial", 13, bold=True)
            self.title_font = pygame.font.SysFont("Arial", 22, bold=True)
            self.has_font = True
        except:
            self.has_font = False

        self.scale_x = 62
        self.scale_y = 140
        self.offset_x = 80
        self.offset_y = self.height // 2

    def to_screen_coords(self, x, y):
        """ Applique un étalement asymétrique pour aérer la grille """
        screen_x = int(x * self.scale_x + self.offset_x)
        screen_y = int(-y * self.scale_y + self.offset_y)
        return screen_x, screen_y

    def draw_text(self, text, pos, color=WHITE, bg_color=(26, 36, 54)):
        if self.has_font:
            surface = self.font.render(text, True, color)
            rect = surface.get_rect(center=pos)
            bg = rect.inflate(8, 4)
            pygame.draw.rect(self.screen, bg_color, bg, border_radius=4)
            pygame.draw.rect(self.screen, EDGE_COLOR, bg, 1, border_radius=4)
            self.screen.blit(surface, rect)

    def draw_graph(self):
        for hub_name, hub in self.all_hubs.items():
            start_pos = self.to_screen_coords(hub.x, hub.y)
            connections = hub.connections if hasattr(hub, 'connections') else []
            for neighbor in connections:
                neighbor_obj = neighbor if hasattr(neighbor, 'x') else self.all_hubs[neighbor]
                end_pos = self.to_screen_coords(neighbor_obj.x, neighbor_obj.y)
                is_active = hub.current_drones_count > 0
                color = EDGE_ACTIVE if is_active else EDGE_COLOR
                width = 3 if is_active else 1
                pygame.draw.line(self.screen, color, start_pos, end_pos, width)

        for hub_name, hub in self.all_hubs.items():
            pos = self.to_screen_coords(hub.x, hub.y)
            radius = 24
            if hub_name == "start" or hub_name == "impossible_goal":
                radius = 35

            # Attribution des couleurs du fichier de configuration
            if hub_name == "start": color = (46, 204, 113)      # Green
            elif hub_name == "impossible_goal": color = (155, 89, 182) # Rainbow/Violet
            elif "gate_hell" in hub_name: color = (231, 76, 60) # Red
            elif "trap" in hub_name: color = (142, 68, 173)    # Purple
            elif "dead" in hub_name: color = (44, 62, 80)       # Black
            elif "loop" in hub_name: color = (211, 84, 0)       # Brown
            elif "overflow" in hub_name: color = (192, 57, 43)  # Maroon
            elif "false_hope" in hub_name or "priority" in hub_name: color = (241, 196, 15) # Gold
            elif "conv_restricted" in hub_name: color = (120, 40, 40) # Darkred
            else: color = (52, 152, 219)

            pygame.draw.circle(self.screen, (20, 27, 41), pos, radius)
            pygame.draw.circle(self.screen, color, pos, radius, 3)

            # Étiquette de la station
            label = f"{hub_name} [{hub.current_drones_count}/{hub.max_drones}]"
            self.draw_text(label, (pos[0], pos[1] - radius - 14), color=WHITE)

    def draw_drones(self):
        for i, drone in enumerate(self.drones):
            hub_actuel = self.all_hubs.get(drone.zone)
            if not hub_actuel:
                continue
            pos_start = self.to_screen_coords(hub_actuel.x, hub_actuel.y)
            if (getattr(drone, 'transit_turns_left', 0) == 2 and
                    getattr(drone, 'connection', '')):
                hub_cible = self.all_hubs.get(drone.connection)
                if hub_cible:
                    pos_end = self.to_screen_coords(hub_cible.x, hub_cible.y)
                    pos = (
                        int((pos_start[0] + pos_end[0]) / 2),
                        int((pos_start[1] + pos_end[1]) / 2)
                    )
                else:
                    pos = pos_start
            else:
                if drone.zone == "start" or drone.zone == "impossible_goal":
                    num_drones_here = len([d for d in self.drones if d.zone ==
                                           drone.zone])
                    idx_here = [d for d in self.drones if d.zone ==
                                drone.zone].index(drone)
                    angle = (2 * math.pi * idx_here) / (num_drones_here if
                                                        num_drones_here > 0
                                                        else 1)
                    dist = 50 if drone.zone == "impossible_goal" else 45
                    pos = (int(pos_start[0] + dist * math.cos(angle)),
                           int(pos_start[1] + dist * math.sin(angle)))
                else:
                    random.seed(i)
                    pos = (pos_start[0] + random.randint(-12, 12),
                           pos_start[1] + random.randint(-12, 12))

            color_drone = (231, 76, 60) if getattr(drone,
                                                   'transit_turns_left',
                                                   0) == 1 else (230, 126, 34)

            pygame.draw.circle(self.screen, color_drone, pos, 9)
            pygame.draw.circle(self.screen, WHITE, pos, 9, 1)

            drone_id = getattr(drone, 'id', f"{i+1}")
            self.draw_text(f"D{drone_id}", (pos[0], pos[1] + 16), color=GOLD,
                           bg_color=color_drone)

            pygame.draw.circle(self.screen, (230, 126, 34), pos, 9)
            pygame.draw.circle(self.screen, WHITE, pos, 9, 1)

            drone_id = getattr(drone, 'name', f"D{i+1}")
            self.draw_text(str(drone_id), (pos[0], pos[1] + 16), color=GOLD,
                           bg_color=(230, 126, 34))

    def run_turn(self):
        self.turn += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(BG_COLOR)
        self.draw_graph()
        self.draw_drones()

        if self.has_font:
            surface = self.title_font.render(f"SIMULATION TURN :"
                                             f"{self.turn}", True, GOLD)
            self.screen.blit(surface, (30, 25))

        pygame.display.flip()
        self.clock.tick(4)
