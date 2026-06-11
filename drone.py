from typing import Any


class Drone:
    def __init__(self, id: str, zone: str, connection: str,
                 path: list) -> None:
        self.id = id
        self.zone = zone
        self.connection = connection
        self.path: list = []

    def display(self) -> Any:
        print(f"D{self.id}-{self.zone}", end=" ")
