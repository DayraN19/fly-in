import sys
from parser import parse_config, verify_dict


def main() -> None:
    try:
        config = parse_config(sys.argv[1])
        verify_dict(config)
    except Exception as e:
        print(e)
        return

    start_line = config["start_hub"][0]
    start_elements = start_line.split()
    print("Nom du hub de départ :", start_elements[0])

    for ligne_hub in config["hub"]:
        elements_hub = ligne_hub.split()
        nom = elements_hub[0]
        x = int(elements_hub[1])
        y = int(elements_hub[2])
        print(f"Hub trouvé : {nom} aux coordonnées ({x}, {y})")



if __name__ == "__main__":
    main()
