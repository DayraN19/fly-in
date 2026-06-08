import sys
from drone import Drone
from hub import Hub
from parser import parse_config, parse_hub_line, verify_dict
from pathfinding import find_shortest_path


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
        nouveau_drone = Drone(id=drone_id, zone=start_name, connection="start")
        drones.append(nouveau_drone)

    all_hubs[start_name].is_occupied = True

    for drone in drones:
        drone.display()
    print()

    print("\n--- Liste des Hubs enregistrés en mémoire ---")
    for nom_hub, objet_hub in all_hubs.items():
        objet_hub.display_info()

    for ligne_conn in config["connection"]:
        elements_conn = ligne_conn.split("-", 1)
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

    turn = 0
    sim_run = True

    while sim_run:
        turn += 1
        print(f"--- Tour {turn} ---")
        for drone in drones:
            drone.display()
        print()

        all_arrived = True
        for drone in drones:
            if drone.zone != end_name:
                all_arrived = False
        if all_arrived:
            sim_run = False
            print(f"\nTous les drones sont arrivés en {turn} tours.")
        if turn >= 1:
            print("\n(Fin du Tour 0 / Initialisation attente de l'algorithme)")
            break

    hub_depart = all_hubs[start_name]
    hub_arrivee = all_hubs[end_name]
    chemin_ideal = find_shortest_path(hub_depart, hub_arrivee)

    for drone in drones:
        drone.path = chemin_ideal[1:]


if __name__ == "__main__":
    main()
