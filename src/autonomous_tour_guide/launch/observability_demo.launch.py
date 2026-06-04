from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="autonomous_tour_guide",
                executable="mission_status_publisher",
                name="mission_status_publisher",
                output="screen",
                parameters=[
                    {
                        "mission_id": "room_tour_demo",
                        "publish_period_sec": 1.0,
                    }
                ],
            )
        ]
    )
