import re
from typing import Union


class Hub:
    """
    Represents a hub in the drone routing network.

    Each hub has a position, a zone type, a maximum drone capacity,
    and a list of connected neighboring hubs.

    Attributes:
        name (str): Name/identifier of the hub.
        x (float): X coordinate.
        y (float): Y coordinate.
        zone_type (str): Type of zone (normal, restricted, blocked, etc.).
        current_drones_count (int): Number of drones currently inside the hub.
        connections (list[Hub]): Adjacent hubs connected to this hub.
        max_drones (int): Maximum number of drones allowed in the hub.
    """
    def __init__(
        self,
        name: str,
        x: Union[int, float, str],
        y: Union[int, float, str],
        option_str: str,
        metadata_or_max: Union[int, float, str] = 1,
        zone_type: str = "normal",
    ) -> None:
        """
        Initialize a Hub instance.

        Args:
            name (str): Hub identifier.
            x (Union[int, float, str]): X coordinate of the hub.
            y (Union[int, float, str]): Y coordinate of the hub.
            metadata_or_max (Union[int, float, str], optional):
                Either the maximum number of drones allowed or a metadata
                string containing configuration (max_drones, zone, color).
                Defaults to 1.
            zone_type (str, optional): Type of zone for the hub.
                Defaults to "normal".

        Returns:
            None
        """
        self.name: str = name
        self.x: float = float(x)
        self.y: float = float(y)
        self.color = option_str
        self.zone_type: str = zone_type
        self.current_drones_count: int = 0
        self.connections: list["Hub"] = []
        self.max_drones: int = 1

        if option_str:
            max_match = re.search(r'max_drones\s*=\s*([0-9]+)', option_str)
            if max_match:
                self.max_drones = int(max_match.group(1))

            type_match = re.search(r'zone_type\s*=\s*([a-zA-Z]+)', option_str)
            if type_match:
                self.zone_type = type_match.group(1).lower()

        if isinstance(metadata_or_max, (int, float)):
            self.max_drones = int(metadata_or_max)
        elif isinstance(metadata_or_max, str):
            m_match = re.search(r"max_drones=(\d+)", metadata_or_max)
            if m_match:
                self.max_drones = int(m_match.group(1))
            elif metadata_or_max.isdigit():
                self.max_drones = int(metadata_or_max)

            zone_match = re.search(r"zone=(\w+)", metadata_or_max)
            if zone_match:
                self.zone_type = zone_match.group(1)
            if "color=black" in metadata_or_max:
                self.zone_type = "blocked"

    def add_neighbor(self, neighbor_hub: "Hub") -> None:
        """
        Add a neighboring hub to this hub's connections.

        Ensures that connections are not duplicated.

        Args:
            neighbor_hub (Hub): The hub to connect to.

        Returns:
            None
        """
        if neighbor_hub not in self.connections:
            self.connections.append(neighbor_hub)
