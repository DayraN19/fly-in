import heapq

def find_short_path(start_hub, end_hub, all_hubs):
    queue = [(0, start_hub.name, [start_hub.name])]
    distances = {hub_name: float('inf') for hub_name in all_hubs}
    distances[start_hub.name] = 0

    while queue:
        current_cost, current_name, path = heapq.heappop(queue)
        if current_name == end_hub.name:
            return path
        if current_cost > distances[current_name]:
            continue
        current_hub = all_hubs[current_name]
        connections = current_hub.connections if hasattr(current_hub, 'connections') else []
        for neighbor in connections:
            neighbor_name = neighbor.name if hasattr(neighbor, 'name') else neighbor
            neighbor_hub = all_hubs[neighbor_name]
            if getattr(neighbor_hub, 'zone_type', 'normal') == 'blocked':
                continue
            zone_type = getattr(neighbor_hub, 'zone_type', 'normal')
            if zone_type == 'restricted':
                move_cost = 2
            elif zone_type == 'priority':
                move_cost = 0.9
            else:
                move_cost = 1
            new_cost = current_cost + move_cost
            if new_cost < distances[neighbor_name]:
                distances[neighbor_name] = new_cost
                heapq.heappush(queue, (new_cost, neighbor_name, path + [neighbor_name]))

    return None

def get_dynamic_path(drone_current_hub, end_hub, all_hubs):
    """
    Version dynamique facultative : recalcule un chemin si un goulot d'étranglement 
    est détecté sur la route prévue, en appliquant une pénalité temporaire aux hubs pleins.
    """
    queue = [(0, drone_current_hub.name, [drone_current_hub.name])]
    distances = {hub_name: float('inf') for hub_name in all_hubs}
    distances[drone_current_hub.name] = 0

    while queue:
        current_cost, current_name, path = heapq.heappop(queue)

        if current_name == end_hub.name:
            return path

        if current_cost > distances[current_name]:
            continue

        current_hub = all_hubs[current_name]
        connections = current_hub.connections if hasattr(current_hub, 'connections') else []

        for neighbor in connections:
            neighbor_name = neighbor.name if hasattr(neighbor, 'name') else neighbor
            neighbor_hub = all_hubs[neighbor_name]

            zone_type = getattr(neighbor_hub, 'zone_type', 'normal')
            if zone_type == 'blocked':
                continue
            if zone_type == 'restricted':
                move_cost = 2
            elif zone_type == 'priority':
                move_cost = 0.9
            else:
                move_cost = 1

            # --- ANTICIPATION DU TRAFIC ---
            # Si le hub cible est déjà complet à ce tour, on ajoute une lourde pénalité de temps (ex: +5 tours)
            # pour forcer Dijkstra à contourner ce hub s'il existe une autre route libre.
            if neighbor_name != end_hub.name:
                current_drones = getattr(neighbor_hub, 'current_drones_count', 0)
                max_drones = getattr(neighbor_hub, 'max_drones', 1)
                if current_drones >= max_drones:
                    move_cost += 5  # Pénalité de trafic

            new_cost = current_cost + move_cost

            if new_cost < distances[neighbor_name]:
                distances[neighbor_name] = new_cost
                heapq.heappush(queue, (new_cost, neighbor_name, path + [neighbor_name]))

    return None