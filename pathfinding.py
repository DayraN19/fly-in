def find_shortest_path(start_hub, end_hub):
    queue = [[start_hub]]
    visited = set()
    visited.add(start_hub)

    while queue:
        current_path = queue.pop(0)
        current_hub = current_path[-1]

        if current_hub == end_hub:
            return current_path

        for neighbor in current_hub.connections:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(current_path)
                new_path.append(neighbor)
                queue.append(new_path)

    return []
