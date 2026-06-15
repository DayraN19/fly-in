import sys
from drone import Drone
from hub import Hub
from parser import parse_config, parse_hub_line, verify_dict
from pathfinding import find_short_path, get_dynamic_path
from visualizer import GraphVisualizer


def main() -> None:
    try:
        config = parse_config(sys.argv[1])
        verify_dict(config)
    except Exception as e:
        print(e)
        return

    all_hubs = {}

    start_line = config["start_hub"][0]
    start_name, start_x, start_y, start_color = parse_hub_line(start_line)
    all_hubs[start_name] = Hub(start_name, start_x, start_y, start_color)

    for ligne_hub in config["hub"]:
        nom, x, y, couleur = parse_hub_line(ligne_hub)
        all_hubs[nom] = Hub(nom, x, y, couleur)

    end_line = config["end_hub"][0]
    end_name, end_x, end_y, end_color = parse_hub_line(end_line)
    all_hubs[end_name] = Hub(end_name, end_x, end_y, end_color)

    nb_drones = int(config["nb_drones"][0])
    drones = []
    for i in range(nb_drones):
        drone_id = str(i + 1)
        nouveau_drone = Drone(id=drone_id, zone=start_name,
                              connection="", path=[])
        drones.append(nouveau_drone)

    all_hubs[start_name].current_drones_count = nb_drones

    for ligne_conn in config["connection"]:
        ligne_nettoyee = ligne_conn.split('[')[0].strip()
        ligne_nettoyee = ligne_nettoyee.replace('-', ' ')
        elements_conn = ligne_nettoyee.split()
        if len(elements_conn) < 2:
            continue
        nom_a = elements_conn[0]
        nom_b = elements_conn[1]
        hub_a = all_hubs[nom_a]
        hub_b = all_hubs[nom_b]
        hub_a.add_neighbor(hub_b)
        hub_b.add_neighbor(hub_a)

    print("\n--- Vérification des connexions ---")
    for nom, hub_obj in all_hubs.items():
        voisins = [voisin.name for voisin in hub_obj.connections]
        print(f"Le Hub '{nom}' est connecté à : {voisins}")

    # Remise à zéro propre des compteurs avant simulation
    for nom, hub_obj in all_hubs.items():
        hub_obj.current_drones_count = 0
    all_hubs[start_name].current_drones_count = nb_drones

    visualizer = GraphVisualizer(all_hubs, drones)

    turn = 0
    sim_run = True

    while sim_run:
        turn += 1
        print(f"--- Tour {turn} ---")

        for drone in drones:
            if drone.transit_turns_left > 0:
                drone.transit_turns_left -= 1
                if drone.transit_turns_left == 1 and drone.connection:
                    next_hub_name = drone.connection
                    current_hub_object = all_hubs[drone.zone]

                    if drone.zone != start_name:
                        current_hub_object.current_drones_count -= 1
                    drone.zone = next_hub_name

                elif drone.transit_turns_left == 0 and drone.connection:
                    drone.connection = ""
                    if len(drone.path) > 0 and drone.path[0] == drone.zone:
                        drone.path.pop(0)

        for drone in drones:
            if drone.transit_turns_left > 0 or drone.connection:
                continue
            dynamic_path = get_dynamic_path(all_hubs[drone.zone],
                                            all_hubs[end_name], all_hubs)
            if not dynamic_path:
                dynamic_path = find_short_path(all_hubs[drone.zone],
                                               all_hubs[end_name], all_hubs)
            if dynamic_path:
                if dynamic_path[0] == drone.zone:
                    dynamic_path.pop(0)
                drone.path = dynamic_path

        for drone in drones:
            if drone.transit_turns_left > 0 or drone.connection:
                continue

            if len(drone.path) > 0:
                next_hub_name = drone.path[0]
                next_hub_object = all_hubs[next_hub_name]
                current_hub_object = all_hubs[drone.zone]

                connected_neighbors = [v.name for v in
                                       current_hub_object.connections]
                if (next_hub_name != end_name and
                        next_hub_name not in connected_neighbors):
                    continue

                zone_type = getattr(next_hub_object, 'zone_type', 'normal')
                is_restricted = (zone_type == "restricted" or
                                 "restricted" in next_hub_name.lower())

                if is_restricted:
                    # Vérification de place sur le restricted cible
                    if (next_hub_object.current_drones_count <
                            int(next_hub_object.max_drones)):
                        next_hub_object.current_drones_count += 1
                        drone.transit_turns_left = 2
                        drone.connection = next_hub_name
                else:
                    if (next_hub_object.current_drones_count <
                            int(next_hub_object.max_drones) or
                            next_hub_name == end_name):
                        if drone.zone != start_name:
                            current_hub_object.current_drones_count -= 1
                        if next_hub_name != end_name:
                            next_hub_object.current_drones_count += 1
                        drone.zone = next_hub_name
                        drone.path.pop(0)

        for drone in drones:
            drone.display(start_name, end_name)
        print()

        visualizer.turn = turn
        visualizer.run_turn()

        all_arrived = all(drone.zone == end_name and
                          drone.transit_turns_left == 0 for drone in drones)
        if all_arrived:
            sim_run = False
            print(f"\nSimulation terminée avec succès en {turn} tours !")


if __name__ == "__main__":
    main()
