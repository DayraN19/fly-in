class Drone:
    def __init__(self, id: str, zone: str, connection: str,
                 path: list) -> None:
        self.id = id
        self.zone = zone
        self.connection = connection
        self.path = path
        self.transit_turns_left = 0

    def display(self) -> None:
        if self.transit_turns_left == 2 and self.connection:
            print(f"D{self.id}-{self.zone}->"
                  f"{self.connection}(VOL_MILIEU)", end=" ")
        elif self.transit_turns_left == 1 and self.connection:
            print(f"D{self.id}-{self.zone}(ATTENTE_RESTRICTED)", end=" ")
        else:
            print(f"D{self.id}-{self.zone}", end=" ")
