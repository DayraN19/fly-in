class Drone:
    def __init__(
        self, id: str, zone: str, connection: str, path: list[str]
    ) -> None:
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
        """Affiche le statut du drone selon ses mouvements.

        - Cache le drone s'il est immobile au départ.
        - Affiche le drone quand il part du départ (en vol/transit).
        - Affiche le drone le tour exact où il arrive au Goal, puis le cache.
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
