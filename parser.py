def parse_config(filename: str) -> dict[str, list[str]]:
    dict_file: dict[str, list[str]] = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip() == "" or line.strip().startswith("#"):
                    continue
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                clean_key = key.strip()
                clean_value = value.strip()
                if clean_key not in dict_file:
                    dict_file[clean_key] = [clean_value]
                else:
                    dict_file[clean_key].append(clean_value)
    except FileNotFoundError:
        raise FileNotFoundError("Sorry, config file not found")
    return dict_file


def verify_dict(dict_file: dict[str, list[str]]) -> bool:
    req = ["nb_drones", "start_hub", "hub", "end_hub", "connection"]

    for word in req:
        if word not in dict_file:
            raise ValueError(f"Missing required attribute: '{word}'")
        if len(dict_file[word]) == 0:
            raise ValueError(f"Attribute '{word}' is empty.")

    return True


def parse_hub_line(line: str) -> tuple[str, int, int, str]:
    parts = line.split('[', 1)
    main_part = parts[0].split()
    name = main_part[0]
    x = int(main_part[1])
    y = int(main_part[2])
    option = "[" + parts[1] if len(parts) > 1 else ""

    return name, x, y, option
