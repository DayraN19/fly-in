from typing import Any


def find_short_path(start_hub: Any, end_hub: Any,
                    ignore_trafic=False) -> list[str]:
    queue = [[start_hub]]
    visited = {start_hub}

    while queue:
        current_path = queue.pop(0)
        current_hub = current_path[-1]
        if current_hub == end_hub:
            return [hub.name for hub in current_path]
        for neighbor in current_hub.connections:
            if neighbor not in visited:
                if not ignore_trafic and neighbor != end_hub:
                    if neighbor.current_drones_count >= neighbor.max_drones:
                        continue
                visited.add(neighbor)
                new_path = list(current_path)
                new_path.append(neighbor)
                queue.append(new_path)

    return []
