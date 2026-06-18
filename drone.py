class Drone:
    """
    Represents a drone moving through different zones.

    Attributes:
        id (str): Unique identifier of the drone.
        zone (str): Current zone where the drone is located.
        connection (str): Current connection or destination link.
        path (list[str]): Sequence of zones the drone must follow.
        transit_turns_left (int): Remaining turns before completing transit.
        has_arrived_reported (bool): Indicates whether,
        arrival has already been displayed.
        total_cost (float): Total cost accumulated by the drone.
        turns_count (int): Number of turns elapsed for the drone.
        is_active (bool): Indicates whether the drone is still active.
    """

    def __init__(
        self,
        id: str,
        zone: str,
        connection: str,
        path: list[str]
    ) -> None:
        """
        Initialize a Drone instance.

        Args:
            id (str): Unique identifier of the drone.
            zone (str): Starting zone of the drone.
            connection (str): Initial connection of the drone.
            path (list[str]): List of zones the drone will traverse.

        Returns:
            None
        """
        self.id: str = id
        self.zone: str = zone
        self.connection: str = connection
        self.path: list[str] = path
        self.transit_turns_left: int = 0
        self.has_arrived_reported: bool = False
        self.total_cost: float = 0.0
        self.turns_count: int = 0
        self.is_active: bool = True

    def display(self, start_name: str, end_name: str) -> None:
        """
        Display the current state of the drone.

        The drone is not displayed if it is still at the start
        without an active connection. Once the drone reaches
        the destination, it is displayed only once.

        Args:
            start_name (str): Name of the starting zone.
            end_name (str): Name of the destination zone.

        Returns:
            None
        """
        if self.zone == start_name:
            if self.transit_turns_left == 0 and not self.connection:
                return

        if self.zone == end_name:
            if self.has_arrived_reported:
                return
            self.has_arrived_reported = True

        if self.transit_turns_left == 2 and self.connection:
            print(f"D{self.id}-{self.zone}-{self.connection}", end=" ")
        else:
            print(f"D{self.id}-{self.zone}", end=" ")
