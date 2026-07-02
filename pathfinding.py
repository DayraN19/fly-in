import heapq
from typing import Optional


class Hub:
    """Represents a node (Hub) within the distribution network."""

    def __init__(
        self,
        name: str,
        zone_type: str = "normal",
        max_drones: int = 1,
        current_drones_count: int = 0,
    ):
        self.name: str = name
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones
        self.current_drones_count: int = current_drones_count
        self.connections: list["Hub"] = []

    def add_connection(self, neighbor: "Hub") -> None:
        """Adds a bidirectional connection to another hub."""
        if neighbor not in self.connections:
            self.connections.append(neighbor)
        if self not in neighbor.connections:
            neighbor.connections.append(self)


class Pathfinder:
    """Responsible for calculating routing paths between hubs."""

    ZONE_COSTS: dict[str, float] = {
        "normal": 1.0,
        "priority": 0.9,
        "restricted": 2.0,
    }

    @classmethod
    def _get_base_move_cost(cls, hub: Hub) -> Optional[float]:
        """Calculates the base movement cost of a hub
        based on its zone type."""
        if hub.zone_type == "blocked":
            return None
        return cls.ZONE_COSTS.get(hub.zone_type, 1.0)

    @classmethod
    def find_shortest_path(
        cls, start_hub: Hub, end_hub: Hub, all_hubs: dict[str, Hub]
    ) -> Optional[list[str]]:
        """Finds the shortest path between two hubs using
        standard Dijkstra's algorithm."""
        if start_hub.name not in all_hubs or end_hub.name not in all_hubs:
            return None

        queue: list[tuple[float, str,
                          list[str]]] = [(0.0, start_hub.name,
                                          [start_hub.name])]
        distances: dict[str, float] = {name: float("inf") for name in all_hubs}
        distances[start_hub.name] = 0.0

        while queue:
            current_cost, current_name, path = heapq.heappop(queue)

            if current_name == end_hub.name:
                return path

            if current_cost > distances[current_name]:
                continue

            current_hub = all_hubs[current_name]

            for neighbor in current_hub.connections:
                base_cost = cls._get_base_move_cost(neighbor)
                if base_cost is None:
                    continue

                new_cost = current_cost + base_cost

                if new_cost < distances[neighbor.name]:
                    distances[neighbor.name] = new_cost
                    heapq.heappush(
                        queue, (new_cost,
                                neighbor.name, path + [neighbor.name])
                    )

        return None

    @classmethod
    def find_dynamic_path(
        cls, drone_current_hub: Hub, end_hub: Hub, all_hubs: dict[str, Hub],
        exclude_hub_name: Optional[str] = None
    ) -> Optional[list[str]]:
        """Finds the optimal path while dynamically
        accounting for hub congestion."""
        if (drone_current_hub.name not in all_hubs
                or end_hub.name not in all_hubs):
            return None

        queue: list[tuple[float, str,
                          list[str]]] = [(0.0, drone_current_hub.name,
                                          [drone_current_hub.name])]
        distances: dict[str, float] = {name: float("inf") for name in all_hubs}
        distances[drone_current_hub.name] = 0.0

        while queue:
            current_cost, current_name, path = heapq.heappop(queue)

            if current_name == end_hub.name:
                return path

            if current_cost > distances[current_name]:
                continue

            current_hub = all_hubs[current_name]

            for neighbor in current_hub.connections:
                base_cost = cls._get_base_move_cost(neighbor)
                if neighbor.name == exclude_hub_name:
                    continue
                if base_cost is None:
                    continue

                move_cost = base_cost

                if neighbor.name != end_hub.name:
                    if neighbor.current_drones_count >= neighbor.max_drones:
                        penalty = 10.0 * (neighbor.current_drones_count
                                          - neighbor.max_drones + 1)
                        move_cost += penalty

                new_cost = current_cost + move_cost

                if new_cost < distances[neighbor.name]:
                    distances[neighbor.name] = new_cost
                    heapq.heappush(
                        queue, (new_cost, neighbor.name,
                                path + [neighbor.name])
                    )

        return None
