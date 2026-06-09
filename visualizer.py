import pygame
import sys
import time

# Configuration des couleurs
BACKGROUND = (30, 30, 30)      # Gris foncé
HUB_COLOR = (100, 149, 237)    # Bleu
EDGE_COLOR = (70, 70, 70)      # Gris clair
DRONE_COLOR = (255, 255, 0)     # Orange/Rouge
TEXT_COLOR = (255, 255, 255)   # Blanc


class GraphVisualizer:
    def __init__(self, all_hubs, drones):
        pygame.init()
        self.all_hubs = all_hubs
        self.drones = drones
        # Dimensions de la fenêtre
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("42 Fly-In - Visualisateur de Trafic")
        self.font = pygame.font.SysFont("Arial", 12)
        self.clock = pygame.time.Clock()

        # Facteur d'échelle pour adapter les coordonnées (x, y) à l'écran
        self.scale = 40
        self.offset_x = 100
        self.offset_y = self.height // 2

    def to_screen_coords(self, x, y):
        """ Convertit les coordonnées cartésienes du fichier en pixels écran"""
        screen_x = int(x * self.scale + self.offset_x)
        # En graphisme, l'axe Y est inversé (le 0 est en haut)
        screen_y = int(-y * self.scale + self.offset_y)
        return screen_x, screen_y

    def draw_graph(self):
        # 1. Dessiner les connexions (les arrêtes)
        for hub_name, hub in self.all_hubs.items():
            start_pos = self.to_screen_coords(hub.x, hub.y)
            # Gérer si connections contient des strings ou des objets Hub
            connections = hub.connections if hasattr(hub, 'connections') else []
            for neighbor in connections:
                neighbor_obj = neighbor if hasattr(neighbor, 'x') else self.all_hubs[neighbor]
                end_pos = self.to_screen_coords(neighbor_obj.x, neighbor_obj.y)
                pygame.draw.line(self.screen, EDGE_COLOR, start_pos, end_pos, 2)

        # 2. Dessiner les Hubs (les sommets)
        for hub_name, hub in self.all_hubs.items():
            pos = self.to_screen_coords(hub.x, hub.y)
            # Couleur spéciale selon la capacité ou le nom
            color = HUB_COLOR
            if hub_name == "start": color = (46, 204, 113)      # Vert
            elif "goal" in hub_name: color = (155, 89, 182)    # Violet
            elif hub.max_drones == 1: color = (231, 76, 60)    # Rouge (Goulot)

            pygame.draw.circle(self.screen, color, pos, 15)
            # Afficher le nom du Hub juste au-dessus
            text_surface = self.font.render(hub_name, True, TEXT_COLOR)
            self.screen.blit(text_surface, (pos[0] - 20, pos[1] - 32))

    def draw_drones(self):
        # Dessiner la position actuelle de chaque drone
        for drone in self.drones:
            # On récupère le hub où se trouve le drone
            current_hub = self.all_hubs[drone.zone]
            pos = self.to_screen_coords(current_hub.x, current_hub.y)
            import random
            random.seed(id(drone))  # Assure un décalage fixe par drone
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)
            pygame.draw.circle(self.screen, DRONE_COLOR,
                               (pos[0] + offset_x, pos[1] + offset_y), 6)

    def run_turn(self):
        """ Appelé à chaque tour de ta boucle de simulation """
        # Gestion des événements Pygame (pour pouvoir fermer la fenêtre)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(BACKGROUND)
        self.draw_graph()
        self.draw_drones()

        pygame.display.flip()
        # Vitesse de l'animation (pause de 300ms entre chaque tour pour avoir le temps de voir)
        time.sleep(0.3)
