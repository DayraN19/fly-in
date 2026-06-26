import re


class Parser:
    """A parser class to clean, validate, and structure map configurations."""
    def __init__(self) -> None:
        """Initialize the parser state for a single file validation."""
        self.dict_file: dict[str, list[str]] = {
            "nb_drones": [],
            "start_hub": [],
            "hub": [],
            "end_hub": [],
            "connection": []
        }
        self.seen_connections: set[tuple[str, str]] = set()
        self.defined_zones: set[str] = set()
        self.first_active_line: bool = True
        self.int_max: int = 2147483647
        self.int_min: int = -2147483647

    def validate_metadata_syntax(self, meta_str: str, line_idx: int) -> None:
        """Verify that a metadata block [key=value] is syntactically valid."""
        if not meta_str:
            return
        pairs = meta_str.split()
        for pair in pairs:
            if "=" not in pair or pair.startswith("=") or pair.endswith("="):
                raise ValueError(
                    f"Line {line_idx}: Invalid metadata syntax "
                    f"near '{pair}'. Expected 'key=value'."
                )

    def _parse_zone(self, clean_value: str, line_idx: int) -> None:
        """Parse and validate start_hub, hub, and end_hub entries."""
        parts = clean_value.split('[', 1)
        main_part = parts[0].split()

        if len(main_part) < 3:
            raise ValueError(
                f"Line {line_idx}: Invalid zone format. "
                f"Expected 'name X Y [metadata]'."
            )
        if len(main_part) > 3:
            bad_name = " ".join(main_part[:-2])
            raise ValueError(
                f"Line {line_idx}: Zone name '{bad_name}' contains spaces."
            )

        zone_name = main_part[0]
        if "-" in zone_name:
            raise ValueError(
                f"Line {line_idx}: Zone name '{zone_name}' contains a dash."
            )
        try:
            x_3 = int(main_part[1])
            y_3 = int(main_part[2])
        except Exception:
            raise ValueError("Number is not an int")

        if (x_3 > self.int_max or x_3 < self.int_min or y_3 > self.int_max
                or y_3 < self.int_min):
            raise ValueError(f"Line {line_idx}: Coordinates exceed INT_MIN"
                             f" or MAX")

        if len(parts) > 1:
            meta_str = parts[1].rstrip(']').strip()
            self.validate_metadata_syntax(meta_str, line_idx)

            type_match = re.search(r'zone_type\s*=\s*([a-zA-Z0-9_-]+)',
                                   meta_str)
            if type_match:
                z_type = type_match.group(1)
                if z_type not in ["normal", "blocked", "restricted",
                                  "priority"]:
                    raise ValueError(
                        f"Line {line_idx}: Invalid zone type '{z_type}'."
                    )

            cap_match = re.search(r'max_drones\s*=\s*([a-zA-Z0-9_-]+)',
                                  meta_str)
            if cap_match:
                z_cap = cap_match.group(1)
                if not z_cap.isdigit() or int(z_cap) <= 0:
                    raise ValueError(
                        f"Line {line_idx}: 'max_drones' must be positive."
                    )

        self.defined_zones.add(zone_name)

    def _parse_connection(self, clean_value: str, line_idx: int) -> None:
        """Parse and validate connection pathways between hubs."""
        parts = clean_value.split('[', 1)
        conn_part = parts[0].strip()

        if "-" not in conn_part:
            raise ValueError(
                f"Line {line_idx}: Invalid connection format."
            )

        if len(parts) > 1:
            meta_str = parts[1].rstrip(']').strip()
            self.validate_metadata_syntax(meta_str, line_idx)
            pat = r'max_link_capacity\s*=\s*([a-zA-Z0-9_-]+)'
            cap_match = re.search(pat, meta_str)
            if cap_match:
                l_cap = cap_match.group(1)
                if not l_cap.isdigit() or int(l_cap) <= 0:
                    raise ValueError(
                        f"Line {line_idx}: 'max_link_capacity' must be > 0."
                    )

        nodes = conn_part.split("-")
        if len(nodes) != 2:
            raise ValueError(
                f"Line {line_idx}: Connection must link exactly two zones."
            )
        node_a, node_b = nodes[0].strip(), nodes[1].strip()

        if (node_a not in self.defined_zones
                or node_b not in self.defined_zones):
            raise ValueError(
                f"Line {line_idx}: Connection links undefined zones."
            )

        conn_tuple = (node_a, node_b) if node_a < node_b else (node_b, node_a)
        if conn_tuple in self.seen_connections:
            raise ValueError(
                f"Line {line_idx}: Duplicate connection detected."
            )
        self.seen_connections.add(conn_tuple)

    def verify_dict(self) -> None:
        """Verify that vital configuration sections aren't missing or empty."""
        req = ["nb_drones", "start_hub", "hub", "end_hub", "connection"]
        for word in req:
            if word not in self.dict_file or len(self.dict_file[word]) == 0:
                raise ValueError(
                    f"Configuration is missing crucial section: '{word}'."
                )

    def parse_config(self, filename: str) -> dict[str, list[str]]:
        """Parse and strictly validate a configuration file."""
        try:
            with open(filename, "r") as f:
                for line_idx, raw_line in enumerate(f, 1):
                    clean_line = raw_line.strip()
                    if clean_line == "" or clean_line.startswith("#"):
                        continue

                    if self.first_active_line:
                        if not clean_line.startswith("nb_drones:"):
                            raise ValueError(
                                f"Line {line_idx}: First active line"
                                f" must define 'nb_drones'."
                            )
                        self.first_active_line = False

                    if ":" not in clean_line:
                        raise ValueError(
                            f"Line {line_idx}: Syntax Error. Expected"
                            f" 'key: value'."
                        )

                    key, value = clean_line.split(":", 1)
                    clean_key = key.strip()
                    clean_value = value.strip()

                    if clean_key not in self.dict_file:
                        raise ValueError(
                            f"Line {line_idx}: Unknown key '{clean_key}'."
                        )

                    if clean_key == "nb_drones":
                        if self.dict_file["nb_drones"]:
                            raise ValueError(
                                f"Line {line_idx}: 'nb_drones' defined twice."
                            )
                        if not clean_value.isdigit() or int(clean_value) <= 0:
                            raise ValueError(
                                f"Line {line_idx}: 'nb_drones' must be"
                                f" positive."
                            )
                    elif clean_key in ["start_hub", "hub", "end_hub"]:
                        self._parse_zone(clean_value, line_idx)
                    elif clean_key == "connection":
                        self._parse_connection(clean_value, line_idx)

                    self.dict_file[clean_key].append(clean_value)

        except FileNotFoundError:
            raise FileNotFoundError("Sorry, config file not found")

        self.verify_dict()
        return self.dict_file

    def parse_hub_line(self, line: str) -> tuple[str, int, int, str]:
        """Helper function to break down a validated hub line."""
        parts = line.split('[', 1)
        main_part = parts[0].split()
        name = main_part[0]
        try:
            x = int(main_part[1])
            y = int(main_part[2])
        except ValueError:
            raise ValueError("swuidhguge")
        option = "[" + parts[1] if len(parts) > 1 else ""
        return name, x, y, option
