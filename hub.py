from typing import List


class Hub:
    def __init__(self, name: str, x: int, y: int, color: str = "") -> None:
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.connections: List["Hub"] = []
        self.is_occupied = False

    def display_info(self) -> None:
        print(
            f"Hub {self.name} ({self.x}, {self.y}) - "
            f"Couleur: {self.color if self.color else 'Aucune'}"
        )

    def add_neighbor(self, neighbor_hub: "Hub") -> None:
        if neighbor_hub not in self.connections:
            self.connections.append(neighbor_hub)
