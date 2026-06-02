class Drone:
    def __init__(self, id: str, zone: str, connection: str) -> None:
        self.id = id
        self.zone = zone
        self.connection = connection

    def display(self) -> str:
        print(f"D{self.id}={self.zone} or <{self.connection}>", end=" ")

        drone1 = Drone("1", "roof1", "start")
        drone2 = Drone("2", "tunnelB", "goal")
        drones = [drone1, drone2]
        for drone in drones:
            return drones[drone].display()
