import pygame
import sys
import math
import random

# Palette de couleurs Cyberpunk / l'école 42
BG_COLOR = (15, 21, 32)         # Bleu espace très sombre
EDGE_COLOR = (41, 56, 84)       # Bleu acier pour les connexions
EDGE_GLOW = (52, 152, 219)      # Bleu néon pour les routes actives
TEXT_COLOR = (236, 240, 241)    # Blanc cassé

class GraphVisualizer:
    def __init__(self, all_hubs, drones):
        pygame.init()
        self.all_hubs = all_hubs
        self.drones = drones
        self.turn = 0
        
        # Fenêtre plus grande et compatible écrans Retina/Mac
        self.width, self.height = 1400, 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🚀 42 FLY-IN: THE IMPOSSIBLE DREAM - VISUALIZER")
        
        self.clock = pygame.time.Clock()
        
        # Calcul automatique de l'échelle pour que TOUTE la carte prenne de la place
        coords_x = [hub.x for hub in all_hubs.values()]
        coords_y = [hub.y for hub in all_hubs.values()]
        
        min_x, max_x = min(coords_x), max(coords_x)
        min_y, max_y = min(coords_y), max(coords_y)
        
        # Ajustement des marges
        span_x = max_x - min_x if max_x != min_x else 1
        span_y = max_y - min_y if max_y != min_y else 1
        
        self.scale_x = (self.width - 250) / span_x
        self.scale_y = (self.height - 250) / span_y
        self.scale = min(self.scale_x, self.scale_y, 60) # Échelle agrandie
        
        self.offset_x = (self.width / 2) - ((max_x + min_x) / 2 * self.scale)
        self.offset_y = (self.height / 2) + ((max_y + min_y) / 2 * self.scale)

        # Tentative de chargement de la police, repli sur dessin manuel si crash
        try:
            self.font = pygame.font.SysFont("Impact", 22)
            self.small_font = pygame.font.SysFont("Arial", 12)
            self.has_font = True
        except:
            self.has_font = False

    def to_screen_coords(self, x, y):
        """ Convertit les coordonnées cartésiennes en pixels """
        screen_x = int(x * self.scale + self.offset_x)
        screen_y = int(-y * self.scale + self.offset_y) # Inversion de l'axe Y pour l'écran
        return screen_x, screen_y

    def draw_hud(self):
        """ Dessine un panneau de contrôle moderne en haut à droite """
        # Rectangle de fond transparent
        hud_rect = pygame.Rect(self.width - 280, 20, 250, 100)
        pygame.draw.rect(self.screen, (26, 36, 54), hud_rect, border_radius=10)
        pygame.draw.rect(self.screen, (52, 152, 219), hud_rect, 2, border_radius=10)
        
        if self.has_font:
            txt_turn = self.font.render(f"TOUR : {self.turn}", True, (241, 196, 15))
            txt_drones = self.small_font.render(f"Drones en vol : {len([d for d in self.drones if d.zone != 'impossible_goal'])}", True, TEXT_COLOR)
            self.screen.blit(txt_turn, (self.width - 260, 35))
            self.screen.blit(txt_drones, (self.width - 260, 75))

    def draw_graph(self):
        # 1. DESSIN DES LIGNES (CONNEXIONS NEON)
        for hub_name, hub in self.all_hubs.items():
            start_pos = self.to_screen_coords(hub.x, hub.y)
            connections = hub.connections if hasattr(hub, 'connections') else []
            
            for neighbor in connections:
                neighbor_obj = neighbor if hasattr(neighbor, 'x') else self.all_hubs[neighbor]
                end_pos = self.to_screen_coords(neighbor_obj.x, neighbor_obj.y)
                
                # Si des drones transitent sur ce hub, on illumine la ligne
                if hub.current_drones_count > 0:
                    pygame.draw.line(self.screen, EDGE_GLOW, start_pos, end_pos, 4)
                else:
                    pygame.draw.line(self.screen, EDGE_COLOR, start_pos, end_pos, 2)

        # 2. DESSIN DES HUBS (STATIONS FUTURISTES GIGANTESQUES)
        for hub_name, hub in self.all_hubs.items():
            pos = self.to_screen_coords(hub.x, hub.y)
            
            # Détermination de la couleur de la station
            if hub_name == "start":
                base_color = (46, 204, 113)  # Émeraude
                radius = 35
            elif "goal" in hub_name or hub_name == "impossible_goal":
                base_color = (155, 89, 182) # Violet Galaxie
                radius = 40
            elif hub.max_drones == 1:
                base_color = (231, 76, 60)   # Rouge Goulot (Danger)
                radius = 25
            else:
                base_color = (52, 152, 219)  # Bleu standard
                radius = 25

            # Effet d'aura lumineuse (Glow)
            if hub.current_drones_count > 0:
                pygame.draw.circle(self.screen, [min(c + 50, 255) for c in base_color], pos, radius + 4, 2)
            
            # Corps de la station
            pygame.draw.circle(self.screen, (22, 30, 46), pos, radius) # Fond sombre
            pygame.draw.circle(self.screen, base_color, pos, radius, 4)  # Contour épais
            pygame.draw.circle(self.screen, base_color, pos, radius - 8, 1) # Anneau interne
            
            # Affichage des jauges de remplissage (Capacité)
            if hub_name != "start" and hub_name != "impossible_goal":
                fill_ratio = hub.current_drones_count / hub.max_drones
                if fill_ratio > 0:
                    # Plus c'est plein, plus ça devient rouge orange
                    gauge_color = (230, 126, 34) if fill_ratio < 1 else (231, 76, 60)
                    pygame.draw.circle(self.screen, gauge_color, pos, int((radius - 10) * fill_ratio))

            # Noms des Hubs
            if self.has_font:
                lbl_color = (241, 196, 15) if hub.current_drones_count > 0 else TEXT_COLOR
                txt = self.small_font.render(f"{hub_name} ({hub.current_drones_count}/{hub.max_drones})", True, lbl_color)
                self.screen.blit(txt, (pos[0] - 40, pos[1] - radius - 20))

    def draw_spaceship(self, surface, color, pos, angle, size=24):
        """ Dessine un magnifique vaisseau triangulaire vectoriel stylisé """
        x, y = pos
        rad = math.radians(angle)
        
        # Sommets du triangle orienté vers sa direction
        p1 = (x + size * math.cos(rad), y - size * math.sin(rad))
        p2 = (x + (size/2) * math.cos(rad + 2.5), y - (size/2) * math.sin(rad + 2.5))
        p3 = (x + (size/2) * math.cos(rad - 2.5), y - (size/2) * math.sin(rad - 2.5))
        
        # Traînée de propulsion du vaisseau
        fire_p = (x - (size/1.5) * math.cos(rad), y + (size/1.5) * math.sin(rad))
        pygame.draw.line(surface, (254, 202, 87), ((p2[0]+p3[0])/2, (p2[1]+p3[1])/2), fire_p, 4)

        # Corps du vaisseau
        pygame.draw.polygon(surface, color, [p1, p2, p3])
        pygame.draw.polygon(surface, (255, 255, 255), [p1, p2, p3], 2) # Liseré blanc ardent

    def draw_drones(self):
        """ Anime et affiche les drones sous forme de vaisseaux spatiaux """
        for i, drone in enumerate(self.drones):
            current_hub = self.all_hubs[drone.zone]
            pos = self.to_screen_coords(current_hub.x, current_hub.y)
            
            # Gestion d'un angle de rotation fictif selon le nom du drone pour le look mécanique
            angle = (i * 15) % 360
            
            # S'il a un chemin, on l'oriente vers sa prochaine cible pour le réalisme
            if len(drone.path) > 0:
                next_hub = self.all_hubs[drone.path[0]]
                next_pos = self.to_screen_coords(next_hub.x, next_hub.y)
                angle = math.degrees(math.atan2(-(next_pos[1] - pos[1]), next_pos[0] - pos[0]))

            # Si le drone est aglutiné sur un hub (ex: au start ou à l'arrivée),
            # on les espace en cercle autour du hub pour éviter la superposition crade
            if drone.zone == "start" or drone.zone == "impossible_goal":
                num_drones_here = len([d for d in self.drones if d.zone == drone.zone])
                idx_here = [d for d in self.drones if d.zone == drone.zone].index(drone)
                circle_angle = (2 * math.pi * idx_here) / (num_drones_here if num_drones_here > 0 else 1)
                dist = 50 if drone.zone == "impossible_goal" else 45
                pos = (int(pos[0] + dist * math.cos(circle_angle)), int(pos[1] + dist * math.sin(circle_angle)))
                angle = math.degrees(circle_angle)

            # Couleur unique pour chaque drone générée proprement (Dégradé orange/jaune chaud)
            random.seed(i)
            ship_color = (255, random.randint(100, 180), 0)

            # Dessin final du vaisseau
            self.draw_spaceship(self.screen, ship_color, pos, angle, size=20)

    def run_turn(self):
        """ Appelé à chaque étape de boucle dans flyin.py """
        self.turn += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Rendu complet
        self.screen.fill(BG_COLOR)
        self.draw_graph()
        self.draw_drones()
        self.draw_hud()
        
        pygame.display.flip()
        
        # 8 FPS pour avoir une superbe fluidité et apprécier le déplacement
        self.clock.tick(5)