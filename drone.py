from typing import Any


class Drone:
    def __init__(self, id: str, zone: str, connection: str) -> None:
        self.id = id
        self.zone = zone
        self.connection = connection

    def display(self) -> Any:
        print(f"D{self.id}={self.zone} or <{self.connection}>", end=" ")
