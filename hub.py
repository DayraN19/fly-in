class Hub:
    def __init__(self, name: str, x: int, y: int,
                 option_str: str = "") -> None:
        self.name = name
        self.x = x
        self.y = y
        self.connections = []
        self.color = "Aucune"
        self.max_drones = 1
        self.current_drones_count = 0
        if option_str:
            clean_opt = option_str.replace("[", "").replace("]", "")
            attributes = clean_opt.split()
            for attr in attributes:
                if "color=" in attr:
                    self.color = attr.split("=")[1]
                elif "max_drones=" in attr:
                    self.max_drones = int(attr.split("=")[1])

    def display_info(self) -> None:
        print(f"Hub {self.name} ({self.x}, {self.y})"
              f" - Couleur: {self.color} - Capacité Max: {self.max_drones}")

    def add_neighbor(self, neighbor_hub: "Hub") -> None:
        if neighbor_hub not in self.connections:
            self.connections.append(neighbor_hub)
