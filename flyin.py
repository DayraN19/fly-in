import sys
from drone import Drone
from hub import Hub
from parser import parse_config, parse_hub_line, verify_dict
from pathfinding import find_short_path
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
        nouveau_drone = Drone(id=drone_id, zone=start_name, connection="start",
                              path=[])
        drones.append(nouveau_drone)

    all_hubs[start_name].current_drones_count = nb_drones

    for drone in drones:
        drone.display()
    print()

    print("\n--- Liste des Hubs enregistrés en mémoire ---")
    for nom_hub, objet_hub in all_hubs.items():
        objet_hub.display_info()

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

    hub_start = all_hubs[start_name]
    hub_end = all_hubs[end_name]

    for drone in drones:
        free_path = find_short_path(hub_start, hub_end, ignore_trafic=False)
        if not free_path:
            free_path = find_short_path(hub_start, hub_end, ignore_trafic=True)
        drone.path = free_path[1:]
        if free_path:
            for step_name in drone.path:
                if step_name != end_name:
                    all_hubs[step_name].current_drones_count += 1

    for nom, hub_obj in all_hubs.items():
        if nom != start_name and nom != end_name:
            hub_obj.current_drones_count = 0

    visualizer = GraphVisualizer(all_hubs, drones)
    turn = 0
    sim_run = True

    while sim_run:
        turn += 1
        print(f"--- Tour {turn} ---")

        for drone in drones:
            if len(drone.path) > 0:
                next_hub_name = drone.path[0]
                next_hub_object = all_hubs[next_hub_name]
                if (next_hub_object.current_drones_count <
                        next_hub_object.max_drones
                        or next_hub_name == end_name):
                    if drone.zone != start_name:
                        all_hubs[drone.zone].current_drones_count -= 1
                    drone.zone = next_hub_name
                    if next_hub_name != end_name:
                        next_hub_object.current_drones_count += 1
                    drone.path.pop(0)
                else:
                    pass

        for drone in drones:
            drone.display()
        print()

        visualizer.run_turn()

        all_arrived = True
        for drone in drones:
            if drone.zone != end_name:
                all_arrived = False

        if all_arrived:
            sim_run = False
            print(f"\nSimulation terminée avec succès en {turn} tours !")


if __name__ == "__main__":
    main()
