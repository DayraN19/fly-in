import re


def parse_config(filename: str) -> dict[str, list[str]]:
    """
    Parse and strictly validate a configuration file.

    Ensures the first active line defines 'nb_drones',

    validates metadata syntax,

    checks for duplicate connections, and enforces data types.

    Args:
        filename (str): Path to the configuration file.

    Returns:
        dict[str, list[str]]: Parsed and validated configuration fields.

    Raises:
        ValueError: If any parsing or validation rule is violated.
    """
    dict_file: dict[str, list[str]] = {
        "nb_drones": [], "start_hub": [], "hub": [], "end_hub": [],
        "connection": []
    }

    seen_connections: set[tuple[str, str]] = set()
    defined_zones: set[str] = set()
    first_active_line = True

    try:
        with open(filename, "r") as f:
            for line_idx, raw_line in enumerate(f, 1):
                clean_line = raw_line.strip()
                if clean_line == "" or clean_line.startswith("#"):
                    continue

                if first_active_line:
                    if not clean_line.startswith("nb_drones:"):
                        raise ValueError(f"Line {line_idx}: First active line"
                                         f" must define 'nb_drones'.")
                    first_active_line = False

                if ":" not in clean_line:
                    raise ValueError(f"Line {line_idx}: Invalid syntax."
                                     f" Expected 'key: value'.")

                key, value = clean_line.split(":", 1)
                clean_key = key.strip()
                clean_value = value.strip()

                if clean_key not in dict_file:
                    raise ValueError(f"Line {line_idx}: Unknown configuration"
                                     f" key '{clean_key}'.")

                if clean_key == "nb_drones":
                    if dict_file["nb_drones"]:
                        raise ValueError(f"Line {line_idx}: 'nb_drones' can"
                                         f" only be defined once.")
                    if not clean_value.isdigit() or int(clean_value) <= 0:
                        raise ValueError(f"Line {line_idx}: 'nb_drones' must"
                                         f" be a positive integer.")
                    dict_file[clean_key].append(clean_value)

                elif clean_key in ["start_hub", "hub", "end_hub"]:
                    parts = clean_value.split('[', 1)
                    main_part = parts[0].split()

                    if len(main_part) < 3:
                        raise ValueError(f"Line {line_idx}: Invalid zone"
                                         f" format. Expected 'name X Y"
                                         f" [metadata]'.")
                    if len(main_part) > 3:
                        bad_name = " ".join(main_part[:-2])
                        raise ValueError(f"Line {line_idx}: Zone name"
                                         f" '{bad_name}' contains spaces .")

                    zone_name = main_part[0]
                    if "-" in zone_name:
                        raise ValueError(f"Line {line_idx}: Zone name"
                                         f" '{zone_name}' contains a dash.")

                    if len(parts) > 1:
                        meta_str = parts[1].rstrip(']').strip()
                        validate_metadata_syntax(meta_str, line_idx)
                        pattern_3 = r'zone_type\s*=\s*([a-zA-Z0-9_-]+)'
                        type_match = re.search(pattern_3, meta_str)
                        if type_match:
                            z_type = type_match.group(1)
                            if z_type not in ["normal", "blocked",
                                              "restricted", "priority"]:
                                raise ValueError(f"Line {line_idx}: Invalid"
                                                 f" zone type '{z_type}'. Must"
                                                 f" be normal, blocked,"
                                                 f" restricted, or priority.")

                        pattern_2 = r'max_drones\s*=\s*([a-zA-Z0-9_-]+)'
                        cap_match = re.search(pattern_2, meta_str)
                        if cap_match:
                            z_cap = cap_match.group(1)
                            if not z_cap.isdigit() or int(z_cap) <= 0:
                                raise ValueError(f"Line {line_idx}: "
                                                 f"'max_drones' capacity must"
                                                 f" be a positive integer.")

                    defined_zones.add(zone_name)
                    dict_file[clean_key].append(clean_value)

                elif clean_key == "connection":
                    parts = clean_value.split('[', 1)
                    conn_part = parts[0].strip()

                    if "-" not in conn_part:
                        raise ValueError(f"Line {line_idx}: Invalid connection"
                                         f" format. Expected 'zone1-zone2'.")

                    if len(parts) > 1:
                        meta_str = parts[1].rstrip(']').strip()
                        validate_metadata_syntax(meta_str, line_idx)
                        pattern_1 = r'max_link_capacity\s*=\s*([a-zA-Z0-9_-]+)'
                        cap_match = re.search(pattern_1, meta_str)
                        if cap_match:
                            l_cap = cap_match.group(1)
                            if not l_cap.isdigit() or int(l_cap) <= 0:
                                raise ValueError(f"Line {line_idx}: "
                                                 f"'max_link_capacity' must be"
                                                 f" a positive integer.")

                    nodes = conn_part.split("-")
                    if len(nodes) != 2:
                        raise ValueError(f"Line {line_idx}: Connection must"
                                         f" link exactly two zones.")
                    node_a, node_b = nodes[0].strip(), nodes[1].strip()

                    if node_a not in defined_zones:
                        raise ValueError(f"Line {line_idx}: Connection links"
                                         f" undefined zone '{node_a}'.")
                    if node_b not in defined_zones:
                        raise ValueError(f"Line {line_idx}: Connection links"
                                         f" undefined zone '{node_b}'.")

                    if node_a < node_b:
                        conn_tuple = (node_a, node_b)
                    else:
                        conn_tuple = (node_b, node_a)
                    if conn_tuple in seen_connections:
                        raise ValueError(f"Line {line_idx}: Duplicate"
                                         f" connection detected between"
                                         f"'{node_a}' and '{node_b}'.")
                    seen_connections.add(conn_tuple)
                    dict_file[clean_key].append(clean_value)

    except FileNotFoundError:
        raise FileNotFoundError("Sorry, config file not found")

    return dict_file


def validate_metadata_syntax(meta_str: str, line_idx: int) -> None:
    """Verifies that a metadata block [key=value] is syntactically valid."""
    if not meta_str:
        return
    pairs = meta_str.split()
    for pair in pairs:
        if "=" not in pair or pair.startswith("=") or pair.endswith("="):
            raise ValueError(f"Line {line_idx}: Invalid metadata syntax "
                             f"near '{pair}'. Expected 'key=value'.")


def verify_dict(dict_file: dict[str, list[str]]) -> bool:
    """Verify that vital configuration sections are not missing or empty."""
    req = ["nb_drones", "start_hub", "hub", "end_hub", "connection"]
    for word in req:
        if word not in dict_file or len(dict_file[word]) == 0:
            raise ValueError(f"Configuration is missing crucial"
                             f" section: '{word}'.")
    return True


def parse_hub_line(line: str) -> tuple[str, int, int, str]:
    """Helper function to break down a validated hub line."""
    int_max = 2147483647
    parts = line.split('[', 1)
    main_part = parts[0].split()
    name = main_part[0]
    x = int(main_part[1])
    y = int(main_part[2])
    if x > int_max or y > int_max:
        raise ValueError(
            f"Coordinates for hub '{name}' exceed INT_MAX ({int_max})."
        )
    option = "[" + parts[1] if len(parts) > 1 else ""
    return name, x, y, option
