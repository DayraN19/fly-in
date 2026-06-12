import re


class Hub:
    def __init__(self, name, x, y, metadata_or_max=1, zone_type="normal"):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.zone_type = zone_type
        self.current_drones_count = 0
        self.connections = []
        self.max_drones = 1

        if isinstance(metadata_or_max, (int, float)):
            self.max_drones = int(metadata_or_max)
        elif isinstance(metadata_or_max, str):
            max_match = re.search(r'max_drones=(\d+)', metadata_or_max)
            if max_match:
                self.max_drones = int(max_match.group(1))
            elif metadata_or_max.isdigit():
                self.max_drones = int(metadata_or_max)

            zone_match = re.search(r'zone=(\w+)', metadata_or_max)
            if zone_match:
                self.zone_type = zone_match.group(1)
            if 'color=black' in metadata_or_max:
                self.zone_type = "blocked"

    def add_neighbor(self, neighbor_hub: "Hub") -> None:
        if neighbor_hub not in self.connections:
            self.connections.append(neighbor_hub)
