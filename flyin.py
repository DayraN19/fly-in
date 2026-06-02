from parser import parse_config, verify_dict
from drone import Drone
import sys


def main() -> None:
    try:
        drone1 = Drone("1", "roof1", "tunnelB")
        drone2 = Drone("2", "roof2", "tunnelA")
        drones = [drone1, drone2]
        for drone in drones:
            Drone.display(drone)
    except Exception as e:
        print(e)
        return
    config = parse_config(sys.argv[1])
    try:
        verify_dict(config)
    except Exception as e:
        print(e)
        return


if __name__ == "__main__":
    main()
