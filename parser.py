def parse_config(filename: str) -> dict[str, list[str]]:
    """
    Parse a configuration file and store its content in a dictionary.

    Each valid line must follow the format "key: value".
    Empty lines and comments starting with '#' are ignored.

    Args:
        filename (str): Path to the configuration file.

    Returns:
        dict[str, list[str]]: A dictionary where each key is associated
            with a list of values from the configuration file.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """
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
    """
    Verify that all required configuration fields are present.

    Args:
        dict_file (dict[str, list[str]]): Parsed configuration dictionary.

    Returns:
        bool: True if all required attributes are present and non-empty.

    Raises:
        ValueError: If a required attribute is missing or empty.
    """
    req = ["nb_drones", "start_hub", "hub", "end_hub", "connection"]

    for word in req:
        if word not in dict_file:
            raise ValueError(f"Missing required attribute: '{word}'")
        if len(dict_file[word]) == 0:
            raise ValueError(f"Attribute '{word}' is empty.")

    return True


def parse_hub_line(line: str) -> tuple[str, int, int, str]:
    """
    Parse a hub definition line.

    Extracts the hub name, coordinates, and optional parameters.

    Args:
        line (str): A line describing a hub.

    Returns:
        tuple[str, int, int, str]:
            - Hub name.
            - X coordinate.
            - Y coordinate.
            - Optional attributes as a string.
    """
    parts = line.split('[', 1)
    main_part = parts[0].split()

    name = main_part[0]
    x = int(main_part[1])
    y = int(main_part[2])
    option = "[" + parts[1] if len(parts) > 1 else ""

    return name, x, y, option
