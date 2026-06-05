import sys
from drone import Drone
from hub import Hub
from parser import parse_config, parse_hub_line, verify_dict


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


if __name__ == "__main__":
    main()
