import json
from dataclasses import asdict, dataclass

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


@dataclass
class MissionStatus:
    mission_id: str
    state: str
    current_waypoint: str
    status_text: str
    anomaly: str


class MissionStatusPublisher(Node):
    def __init__(self) -> None:
        super().__init__("mission_status_publisher")
        self.publisher = self.create_publisher(String, "/tour_guide/mission_status", 10)
        self.declare_parameter("mission_id", "room_tour_demo")
        self.declare_parameter("publish_period_sec", 1.0)

        period = self.get_parameter("publish_period_sec").value
        self.timer = self.create_timer(float(period), self.publish_status)
        self.sequence = 0

    def publish_status(self) -> None:
        waypoints = ["home", "station_1", "station_2", "station_3"]
        waypoint = waypoints[self.sequence % len(waypoints)]
        status = MissionStatus(
            mission_id=str(self.get_parameter("mission_id").value),
            state="observing",
            current_waypoint=waypoint,
            status_text=f"Demo telemetry heartbeat at {waypoint}",
            anomaly="none",
        )

        message = String()
        message.data = json.dumps(asdict(status), sort_keys=True)
        self.publisher.publish(message)
        self.sequence += 1


def main() -> None:
    rclpy.init()
    node = MissionStatusPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
