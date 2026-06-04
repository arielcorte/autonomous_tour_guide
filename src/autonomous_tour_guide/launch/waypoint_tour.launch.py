from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    package_share = Path(get_package_share_directory("autonomous_tour_guide"))
    waypoints_file = package_share / "config" / "waypoints.yaml"

    return LaunchDescription(
        [
            Node(
                package="autonomous_tour_guide",
                executable="waypoint_runner",
                name="waypoint_runner",
                output="screen",
                parameters=[
                    {
                        "mission_id": "room_tour_demo",
                        "waypoints_file": str(waypoints_file),
                        "waypoint_order": ["station_1", "station_2", "station_3", "home"],
                    }
                ],
            )
        ]
    )
