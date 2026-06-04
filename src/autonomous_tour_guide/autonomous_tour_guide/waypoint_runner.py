import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import rclpy
import yaml
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.task import Future
from std_msgs.msg import String


@dataclass
class TourEvent:
    mission_id: str
    state: str
    current_waypoint: str
    status_text: str
    anomaly: str


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    half_yaw = yaw * 0.5
    return 0.0, 0.0, math.sin(half_yaw), math.cos(half_yaw)


class WaypointRunner(Node):
    def __init__(self) -> None:
        super().__init__("waypoint_runner")
        self.declare_parameter("mission_id", "room_tour_demo")
        self.declare_parameter("waypoints_file", "")
        self.declare_parameter("waypoint_order", ["station_1", "station_2", "station_3", "home"])

        self.status_publisher = self.create_publisher(String, "/tour_guide/mission_status", 10)
        self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.waypoints = self.load_waypoints()
        self.waypoint_order = list(self.get_parameter("waypoint_order").value)
        self.current_index = 0
        self.active_goal_name = ""

        self.publish_event("starting", "", "Waiting for Nav2 navigate_to_pose action", "none")
        self.nav_client.wait_for_server()
        self.publish_event("running", "", "Nav2 is available; starting waypoint tour", "none")
        self.send_next_goal()

    def load_waypoints(self) -> dict[str, Any]:
        waypoints_file = str(self.get_parameter("waypoints_file").value)
        if not waypoints_file:
            raise RuntimeError("waypoints_file parameter is required")

        path = Path(waypoints_file)
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

        return data["waypoints"]

    def send_next_goal(self) -> None:
        if self.current_index >= len(self.waypoint_order):
            self.publish_event("succeeded", "done", "Waypoint tour complete", "none")
            rclpy.shutdown()
            return

        self.active_goal_name = self.waypoint_order[self.current_index]
        waypoint = self.waypoints[self.active_goal_name]
        goal = NavigateToPose.Goal()
        goal.pose = self.create_pose(waypoint)

        self.publish_event(
            "navigating",
            self.active_goal_name,
            f"Navigating to {self.active_goal_name}",
            "none",
        )
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    def create_pose(self, waypoint: dict[str, Any]) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = str(waypoint.get("frame_id", "map"))
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(waypoint["x"])
        pose.pose.position.y = float(waypoint["y"])
        qx, qy, qz, qw = yaw_to_quaternion(float(waypoint["yaw"]))
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw
        return pose

    def goal_response_callback(self, future: Future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.publish_event("failed", self.active_goal_name, "Nav2 rejected the goal", "goal_rejected")
            rclpy.shutdown()
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future: Future) -> None:
        result = future.result()
        if result.status != GoalStatus.STATUS_SUCCEEDED:
            self.publish_event(
                "failed",
                self.active_goal_name,
                f"Navigation failed with action status {result.status}",
                "navigation_failed",
            )
            rclpy.shutdown()
            return

        self.publish_event("arrived", self.active_goal_name, f"Arrived at {self.active_goal_name}", "none")
        self.current_index += 1
        self.send_next_goal()

    def publish_event(self, state: str, waypoint: str, text: str, anomaly: str) -> None:
        event = TourEvent(
            mission_id=str(self.get_parameter("mission_id").value),
            state=state,
            current_waypoint=waypoint,
            status_text=text,
            anomaly=anomaly,
        )
        message = String()
        message.data = json.dumps(asdict(event), sort_keys=True)
        self.status_publisher.publish(message)
        self.get_logger().info(message.data)


def main() -> None:
    rclpy.init()
    node = WaypointRunner()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
