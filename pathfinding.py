import heapq
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from hub import Hub


def find_short_path(
    start_hub: "Hub", end_hub: "Hub", all_hubs: dict[str, "Hub"]
) -> Optional[list[str]]:
    """
    Find the shortest path between two hubs using Dijkstra's algorithm.

    The path cost depends on the type of each zone:
    - normal: cost = 1.0
    - priority: cost = 0.9
    - restricted: cost = 2.0
    - blocked: inaccessible

    Args:
        start_hub (Hub): Starting hub.
        end_hub (Hub): Destination hub.
        all_hubs (dict[str, Hub]): Dictionary containing all hubs.

    Returns:
        Optional[list[str]]: List of hub names representing the path
            from start to destination, or None if no path exists.
    """
    queue: list[tuple[float, str, list[str]]] = [
        (0.0, start_hub.name, [start_hub.name])
    ]
    distances: dict[str, float] = {
        hub_name: float("inf") for hub_name in all_hubs
    }
    distances[start_hub.name] = 0.0

    while queue:
        current_cost, current_name, path = heapq.heappop(queue)

        if current_name == end_hub.name:
            return path

        if current_cost > distances[current_name]:
            continue

        current_hub = all_hubs[current_name]
        connections: list["Hub"] = (
            current_hub.connections
            if hasattr(current_hub, "connections")
            else []
        )

        for neighbor in connections:
            neighbor_name = (
                neighbor.name if hasattr(neighbor, "name") else neighbor
            )
            if not isinstance(neighbor_name, str):
                continue
            neighbor_hub = all_hubs[neighbor_name]
            if getattr(neighbor_hub, "zone_type", "normal") == "blocked":
                continue
            zone_type = getattr(neighbor_hub, "zone_type", "normal")
            if zone_type == "restricted":
                move_cost: float = 2.0
            elif zone_type == "priority":
                move_cost = 0.9
            else:
                move_cost = 1.0
            new_cost = current_cost + move_cost
            if new_cost < distances[neighbor_name]:
                distances[neighbor_name] = new_cost
                heapq.heappush(
                    queue, (new_cost, neighbor_name, path + [neighbor_name])
                )

    return None


def get_dynamic_path(
    drone_current_hub: "Hub", end_hub: "Hub", all_hubs: dict[str, "Hub"]
) -> Optional[list[str]]:
    """
    Find the best path while taking hub congestion into account.

    This function extends Dijkstra's algorithm by dynamically
    increasing the movement cost of congested hubs to reduce
    traffic and improve drone distribution.

    Zone costs:
        - normal: cost = 1.0
        - priority: cost = 0.9
        - restricted: cost = 2.0
        - blocked: inaccessible

    Additional congestion penalties are applied when a hub
    exceeds its maximum drone capacity.

    Args:
        drone_current_hub (Hub): Current hub of the drone.
        end_hub (Hub): Destination hub.
        all_hubs (dict[str, Hub]): Dictionary containing all hubs.

    Returns:
        Optional[list[str]]: Optimal path as a list of hub names,
            or None if no valid path exists.
    """
    queue: list[tuple[float, str, list[str]]] = [
        (0.0, drone_current_hub.name, [drone_current_hub.name])
    ]
    distances: dict[str, float] = {
        hub_name: float("inf") for hub_name in all_hubs
    }
    distances[drone_current_hub.name] = 0.0

    while queue:
        current_cost, current_name, path = heapq.heappop(queue)

        if current_name == end_hub.name:
            return path

        if current_cost > distances[current_name]:
            continue

        current_hub = all_hubs[current_name]
        connections: list["Hub"] = (
            current_hub.connections
            if hasattr(current_hub, "connections")
            else []
        )

        for neighbor in connections:
            neighbor_name = (
                neighbor.name if hasattr(neighbor, "name") else neighbor
            )
            if not isinstance(neighbor_name, str):
                continue

            neighbor_hub = all_hubs[neighbor_name]

            zone_type = getattr(neighbor_hub, "zone_type", "normal")
            if zone_type == "blocked":
                continue

            if zone_type == "restricted":
                move_cost = 2.0
            elif zone_type == "priority":
                move_cost = 0.9
            else:
                move_cost = 1.0

            if neighbor_name != end_hub.name:
                current_drones = getattr(
                    neighbor_hub, "current_drones_count", 0
                )
                max_drones = getattr(neighbor_hub, "max_drones", 1)
                if current_drones >= max_drones:
                    move_cost += 10.0 * (current_drones - max_drones + 1)

            new_cost = current_cost + move_cost

            if new_cost < distances[neighbor_name]:
                distances[neighbor_name] = new_cost
                heapq.heappush(
                    queue, (new_cost, neighbor_name, path + [neighbor_name])
                )

    return None
