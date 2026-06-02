def parse_config(filename: str) -> dict[str, str]:
    dict_file: dict[str, str] = {}

    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip() == "" or line.strip().startswith("#"):
                    continue
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                dict_file[key.strip()] = value.strip()
    except FileNotFoundError:
        raise FileNotFoundError("Sorry, config file not found")

    return dict_file


def verify_dict(dict_file: dict[str, str]) -> bool:
    req = ["nb_drones", "start_hub", "hub", "end_hub", "connection"]

    for word in req:
        if word not in dict_file:
            raise ValueError(f"Missing required attribute: '{word}'")
        if not dict_file[word].strip():
            raise ValueError(f"Attribute '{word}' is empty.")

    return True
